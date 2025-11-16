#!/usr/bin/env python3
"""
Nice2Know - Send Confirmation Mail v3
Loads mail from processed/ and moves to sent/ after successful sending
Uses hex mail_id from JSON for URLs
"""
import sys
import json
import smtplib
import shutil
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, Dict
import email
from email import policy

# Auto-detect mail_agent/ directory
def find_mail_agent_root(start_path: Path) -> Path:
    """Find mail_agent root by looking for key directories"""
    current = start_path
    for _ in range(5):
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'config').exists():
            return current
        if current.parent != current:
            current = current.parent
        else:
            break
    return start_path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKING_DIR = find_mail_agent_root(SCRIPT_DIR)
sys.path.insert(0, str(WORKING_DIR))

from utils.analyze_json_quality import analyze_quality, get_field_status

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def load_application_config() -> Dict:
    """Load application.json from correct location"""
    # Try multiple locations
    possible_locations = [
        WORKING_DIR / 'config' / 'connections' / 'application.json',
        WORKING_DIR / 'utils' / 'config' / 'connections' / 'application.json',
        Path('/opt/nice2know/mail_agent/config/connections/application.json'),
    ]
    
    for config_path in possible_locations:
        if config_path.exists():
            print(f"{GREEN}✓ Found application.json at: {config_path}{NC}")
            with open(config_path, 'r') as f:
                return json.load(f)
    
    print(f"{YELLOW}Warning: application.json not found, using defaults{NC}")
    return {
        'storage': {
            'base_path': '/opt/nice2know/storage'
        },
        'base_url': 'http://localhost/n2k',
        'admin': {
            'email': 'support@example.com'
        }
    }

def get_base_url() -> str:
    """Get base URL from application config"""
    config = load_application_config()
    base_url = config.get('base_url', 'http://localhost/n2k')
    # Remove trailing slash if present
    return base_url.rstrip('/')

def get_editor_url(mail_id: str) -> str:
    """Generate editor URL using base_url from config"""
    base_url = get_base_url()
    return f"{base_url}/?mail_id={mail_id}"

def get_confirm_url(mail_id: str) -> str:
    """Generate confirm URL using base_url from config"""
    base_url = get_base_url()
    return f"{base_url}/confirm.php?mail_id={mail_id}"

def get_support_email() -> str:
    """Get support email from application config"""
    config = load_application_config()
    return config.get('admin', {}).get('email', 'support@example.com')


def get_storage_base() -> Path:
    """Get absolute storage base path from config"""
    config = load_application_config()
    base_path = config.get('storage', {}).get('base_path', '/opt/nice2know/storage')
    
    # Always use absolute path
    if not Path(base_path).is_absolute():
        # If relative, resolve from project root (parent of mail_agent)
        storage_base = WORKING_DIR.parent / base_path
    else:
        storage_base = Path(base_path)
    
    return storage_base.resolve()

def load_mail_config() -> tuple[Dict, Dict]:
    """Load mail configuration and secrets"""
    config_dir = WORKING_DIR / 'config'
    
    mail_config_path = config_dir / 'connections' / 'mail_config.json'
    secrets_path = config_dir / 'secrets.json'
    
    if not mail_config_path.exists():
        raise FileNotFoundError(f"mail_config.json not found at {mail_config_path}")
    
    if not secrets_path.exists():
        raise FileNotFoundError(f"secrets.json not found at {secrets_path}")
    
    with open(mail_config_path, 'r') as f:
        mail_config = json.load(f)
    
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    
    return mail_config, secrets

def load_json_file(filepath: Path) -> Optional[Dict]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}✗ Failed to load {filepath.name}: {e}{NC}")
        return None

def load_html_template(filepath: Path) -> Optional[str]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"{RED}✗ Failed to load template: {e}{NC}")
        return None

def extract_mail_info(mail_path: Path) -> Dict[str, str]:
    """Extract sender and subject from .eml file"""
    try:
        with open(mail_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        sender = msg.get('From', 'unknown@example.com')
        subject = msg.get('Subject', 'No Subject')
        
        if '<' in sender and '>' in sender:
            sender_email = sender[sender.find('<')+1:sender.find('>')]
        else:
            sender_email = sender
        
        return {'sender': sender_email, 'subject': subject}
    except Exception as e:
        print(f"{RED}✗ Failed to parse mail: {e}{NC}")
        return {'sender': 'unknown@example.com', 'subject': 'No Subject'}

def build_quality_summary(quality: Dict) -> str:
    """Build quality summary HTML"""
    summary = quality['summary']
    
    # Build missing fields list with anchors
    missing_html = ""
    if quality['missing'] or quality['unclear']:
        missing_items = []
        
        # Map field names to user-friendly labels
        field_labels = {
            'reporter_department': ('Abteilung', '#problem'),
            'affected_users': ('Betroffene Nutzer', '#problem'),
            'solution_approach': ('Lösungsansatz', '#solution'),
            'solution_complexity': ('Komplexität', '#solution'),
            'asset_version': ('Software-Version', '#asset'),
            'asset_platform': ('Plattform', '#asset'),
            'asset_deployment': ('Deployment-Art', '#asset'),
        }
        
        for field in quality['missing']:
            if field in field_labels:
                label, anchor = field_labels[field]
                missing_items.append(f'<li><a href="{anchor}">{label}</a></li>')
        
        for field in quality['unclear']:
            if field in field_labels:
                label, anchor = field_labels[field]
                missing_items.append(f'<li><a href="{anchor}">{label} (unklar)</a></li>')
        
        if missing_items:
            missing_html = f"""
            <div class="missing-fields">
                <div class="missing-fields-title">Fehlende oder unklare Felder:</div>
                <ul class="missing-fields-list">
                    {''.join(missing_items)}
                </ul>
            </div>
            """
    
    return f"""
    <div class="quality-summary">
        <div class="quality-header">
            <span class="quality-icon">📊</span>
            <div>
                <div class="quality-title">Datenqualität</div>
                <div class="quality-score">{summary['completeness_percent']}%</div>
            </div>
        </div>
        <div class="quality-stats">
            <span class="quality-stat complete">✓ {summary['complete_count']} Felder vollständig</span>
            <span class="quality-stat missing">⚠ {summary['missing_count']} fehlen</span>
            <span class="quality-stat unclear">❓ {summary['unclear_count']} unklar</span>
        </div>
        <p style="font-size: 13px; color: #666; font-style: italic;">
            Fehlende oder unklare Felder sind unten markiert. Sie können diese über den Link ergänzen.
        </p>
        {missing_html}
    </div>
    """

def build_field_html(label: str, value: str, field_name: str, quality: Dict) -> str:
    """Build field HTML with status indicator"""
    status = get_field_status(field_name, quality)
    
    if not value or value == 'null' or value == 'N/A':
        value = "[Nicht erkannt]"
        css_class = "missing"
        indicator = '<span class="status-missing">⚠</span> '
    elif status == 'complete':
        css_class = ""
        indicator = '<span class="status-complete">✓</span> '
    elif status == 'unclear':
        css_class = "unclear"
        indicator = '<span class="status-unclear">❓</span> '
    elif status == 'missing':
        css_class = "missing"
        value = "[Nicht erkannt]"
        indicator = '<span class="status-missing">⚠</span> '
    else:
        css_class = ""
        indicator = ""
    
    return f"""
    <div class="field">
        <div class="field-label">{label}</div>
        <div class="field-value {css_class}">{indicator}{value}</div>
    </div>
    """

def fill_template_v2(template: str, problem: Dict, solution: Dict, asset: Dict,
                     mail_info: Dict, quality: Dict) -> str:
    """Fill template with smart status indicators"""
    
    # Reporter name
    reporter_name = problem.get('reporter', {}).get('name', 'Benutzer')
    template = template.replace('{{reporter_name}}', reporter_name)
    
    # Quality Summary
    quality_html = build_quality_summary(quality)
    template = template.replace('{{QUALITY_SUMMARY}}', quality_html)
    
    # === PROBLEM FIELDS ===
    prob = problem.get('problem', {})
    reporter = problem.get('reporter', {})
    
    problem_fields = ""
    problem_fields += build_field_html("Titel", prob.get('title', ''), 'problem_title', quality)
    problem_fields += build_field_html("Beschreibung", prob.get('description', ''), 'problem_description', quality)
    
    # Symptoms
    symptoms = prob.get('symptoms', [])
    if symptoms:
        symptoms_html = '\n'.join([f'<li>{s}</li>' for s in symptoms])
        problem_fields += f"""
        <div class="field">
            <div class="field-label"><span class="status-complete">✓</span> Symptome</div>
            <ul class="list-items">{symptoms_html}</ul>
        </div>
        """
    
    # Department (often missing)
    problem_fields += build_field_html("Abteilung", reporter.get('department', ''), 'reporter_department', quality)
    
    template = template.replace('{{PROBLEM_FIELDS}}', problem_fields)
    
    # Problem Meta
    classification = problem.get('classification', {})
    problem_meta = f"""
    <div class="meta-item">
        <div class="meta-label">Schweregrad</div>
        <div class="meta-value">
            <span class="badge badge-severity-{classification.get('severity', 'medium')}">{classification.get('severity', 'medium').upper()}</span>
        </div>
    </div>
    <div class="meta-item">
        <div class="meta-label">Kategorie</div>
        <div class="meta-value">{classification.get('category', 'N/A')}</div>
    </div>
    <div class="meta-item">
        <div class="meta-label">Status</div>
        <div class="meta-value">
            <span class="badge badge-status-{problem.get('status', 'new')}">{problem.get('status', 'new').upper()}</span>
        </div>
    </div>
    """
    template = template.replace('{{PROBLEM_META}}', problem_meta)
    
    # === SOLUTION SECTION ===
    sol = solution.get('solution', {}) if solution else {}
    metadata = solution.get('metadata', {}) if solution else {}
    steps = sol.get('steps', [])
    
    if steps and len(steps) > 0:
        solution_fields = ""
        solution_fields += build_field_html("Titel", sol.get('title', ''), 'solution_title', quality)
        solution_fields += build_field_html("Beschreibung", sol.get('description', ''), 'solution_description', quality)
        
        # Prerequisites (optional)
        prereqs = sol.get('prerequisites', [])
        if prereqs:
            prereq_html = '\n'.join([f'<li>{p}</li>' for p in prereqs])
            solution_fields += f"""
            <div class="field">
                <div class="field-label">Voraussetzungen</div>
                <ul class="list-items">{prereq_html}</ul>
            </div>
            """
        
        # Steps
        steps_html = ""
        for step in steps:
            step_html = f"""
            <div class="step">
                <div class="step-action">{step.get('action', 'N/A')}</div>
                <div class="step-details">{step.get('details', '')}</div>
            """
            if step.get('command'):
                step_html += f'<div class="step-command">{step["command"]}</div>'
            step_html += f"""
                <div class="step-result">✓ Erwartetes Ergebnis: {step.get('expected_result', 'N/A')}</div>
            </div>
            """
            steps_html += step_html
        
        solution_fields += f"""
        <div class="field">
            <div class="field-label"><span class="status-complete">✓</span> Lösungsschritte</div>
            <div class="steps">{steps_html}</div>
        </div>
        """
        
        # Solution Meta
        solution_meta = f"""
        <div class="meta-item">
            <div class="meta-label">Typ</div>
            <div class="meta-value">{sol.get('type', 'N/A')}</div>
        </div>
        """
        
        # Approach with status
        approach = sol.get('approach')
        if not approach or approach == 'N/A':
            solution_meta += f"""
            <div class="meta-item">
                <div class="meta-label">Ansatz</div>
                <div class="meta-value"><span class="status-missing">⚠</span> [Nicht erkannt]</div>
            </div>
            """
        else:
            solution_meta += f"""
            <div class="meta-item">
                <div class="meta-label">Ansatz</div>
                <div class="meta-value"><span class="status-complete">✓</span> {approach}</div>
            </div>
            """
        
        solution_meta += f"""
        <div class="meta-item">
            <div class="meta-label">Komplexität</div>
            <div class="meta-value">{metadata.get('complexity', 'N/A')}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">Geschätzte Zeit</div>
            <div class="meta-value">{metadata.get('estimated_time', 'N/A')}</div>
        </div>
        """
        
        solution_section = f"""
        <div class="section" id="solution">
            <div class="section-header">
                <span class="section-icon">✅</span>
                <span class="section-title">Lösung</span>
            </div>
            <div class="section-body">
                {solution_fields}
                <div class="meta-info">
                    {solution_meta}
                </div>
            </div>
        </div>
        """
    else:
        solution_section = ""
    
    template = template.replace('{{SOLUTION_SECTION}}', solution_section)
    
    # === ASSET FIELDS ===
    ast = asset.get('asset', {})
    technical = asset.get('technical', {})
    
    asset_fields = ""
    asset_name = ast.get('display_name') or ast.get('name', 'N/A')
    asset_fields += build_field_html("Name", asset_name, 'asset_name', quality)
    asset_fields += build_field_html("Beschreibung", ast.get('description', ''), 'asset_description', quality)
    
    template = template.replace('{{ASSET_FIELDS}}', asset_fields)
    
    # Asset Meta
    asset_meta = f"""
    <div class="meta-item">
        <div class="meta-label">Typ</div>
        <div class="meta-value">{ast.get('type', 'N/A')}</div>
    </div>
    <div class="meta-item">
        <div class="meta-label">Kategorie</div>
        <div class="meta-value">{ast.get('category', 'N/A')}</div>
    </div>
    <div class="meta-item">
        <div class="meta-label">Kritikalität</div>
        <div class="meta-value">{ast.get('criticality', 'N/A')}</div>
    </div>
    <div class="meta-item">
        <div class="meta-label">Status</div>
        <div class="meta-value">{ast.get('status', 'N/A')}</div>
    </div>
    """
    template = template.replace('{{ASSET_META}}', asset_meta)
    
    # Technical Details
    software = technical.get('software')
    version = technical.get('version')
    platform = technical.get('platform')
    
    if software:
        tech_html = '<div class="field" style="margin-top: 15px;"><div class="field-label">Technische Details</div><div class="meta-info">'
        
        tech_html += f'<div class="meta-item"><div class="meta-label">Software</div><div class="meta-value"><span class="status-complete">✓</span> {software}</div></div>'
        
        if version:
            tech_html += f'<div class="meta-item"><div class="meta-label">Version</div><div class="meta-value"><span class="status-complete">✓</span> {version}</div></div>'
        else:
            tech_html += '<div class="meta-item"><div class="meta-label">Version</div><div class="meta-value"><span class="status-missing">⚠</span> [Nicht erkannt]</div></div>'
        
        if platform:
            tech_html += f'<div class="meta-item"><div class="meta-label">Plattform</div><div class="meta-value"><span class="status-complete">✓</span> {platform}</div></div>'
        else:
            tech_html += '<div class="meta-item"><div class="meta-label">Plattform</div><div class="meta-value"><span class="status-missing">⚠</span> [Nicht erkannt]</div></div>'
        
        tech_html += '</div></div>'
    else:
        tech_html = ""
    
    template = template.replace('{{ASSET_TECHNICAL}}', tech_html)
    
    # Footer data - Use HEX mail_id from JSON
    mail_id = problem.get('mail_id', 'N/A')
    
    print(f"{BLUE}[INFO] Using mail_id from JSON: {mail_id}{NC}")
    
    if mail_id != 'N/A':
        editor_url = get_editor_url(mail_id)
        confirm_url = get_confirm_url(mail_id)
        print(f"{BLUE}[INFO] Generated Editor URL: {editor_url}{NC}")
        print(f"{BLUE}[INFO] Generated Confirm URL: {confirm_url}{NC}")
    else:
        editor_url = '#edit'
        confirm_url = '#confirm'
        print(f"{YELLOW}[WARN] mail_id is N/A, using placeholder URLs{NC}")
    
    support_email = get_support_email()
    
    template = template.replace('{{magic_link}}', editor_url)
    template = template.replace('{{confirm_link}}', confirm_url)
    template = template.replace('{{support_email}}', support_email)
    template = template.replace('{{case_id}}', problem.get('id', 'N/A'))
    template = template.replace('{{created_at}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
    template = template.replace('{{mail_id}}', mail_id)
    
    return template

def send_mail(recipient: str, subject: str, html_body: str, mail_config: Dict, secrets: Dict) -> bool:
    """Send email using SMTP configuration"""
    try:
        smtp_config = mail_config.get('smtp', {})
        imap_config = mail_config.get('imap', {})
        mail_secrets = secrets.get('mail', {})
        
        # Get SMTP settings with fallback to IMAP host
        smtp_host = smtp_config.get('host') or imap_config.get('host', 'localhost')
        smtp_port = smtp_config.get('port', 587)
        smtp_user = mail_secrets.get('smtp_username', '')
        smtp_password = mail_secrets.get('smtp_password', '')
        from_address = smtp_config.get('from_address', smtp_user)
        from_name = smtp_config.get('from_name', 'Nice2Know System')
        use_starttls = smtp_config.get('use_starttls', True)
        
        print(f"[DEBUG] SMTP Config: host={smtp_host}, port={smtp_port}, user={smtp_user[:10]}...")
        
        # Build message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_address}>"
        msg['To'] = recipient
        msg['Subject'] = f"Re: {subject}"
        
        text_body = "Bitte öffnen Sie diese E-Mail in einem HTML-fähigen E-Mail-Client."
        
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"[SMTP] Connecting to {smtp_host}:{smtp_port}...")
        
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if use_starttls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"{RED}✗ Failed to send mail: {e}{NC}")
        import traceback
        traceback.print_exc()
        return False

def move_to_sent(mail_file: Path, sent_dir: Path) -> bool:
    """Move .eml file to sent directory after successful sending"""
    try:
        sent_dir.mkdir(parents=True, exist_ok=True)
        dest_file = sent_dir / mail_file.name
        shutil.move(str(mail_file), str(dest_file))
        print(f"{GREEN}✓ Moved {mail_file.name} to sent/{NC}")
        return True
    except Exception as e:
        print(f"{RED}✗ Failed to move mail to sent: {e}{NC}")
        return False

def main():
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know - Send Confirmation Mail v3 (Fixed){NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Working directory: {WORKING_DIR}\n")
    
    # Get storage base from config
    storage_base = get_storage_base()
    processed_dir = storage_base / 'processed'
    sent_dir = storage_base / 'sent'
    
    print(f"Storage base:        {storage_base}")
    print(f"Processed directory: {processed_dir}")
    print(f"Sent directory:      {sent_dir}")
    print()
    
    # Load mail configuration
    try:
        print("Loading mail configuration...")
        mail_config, secrets = load_mail_config()
        print(f"{GREEN}✓ Mail configuration loaded{NC}\n")
    except Exception as e:
        print(f"{RED}✗ Failed to load mail configuration: {e}{NC}")
        sys.exit(1)
    
    if not processed_dir.exists():
        print(f"{RED}✗ Processed directory not found: {processed_dir}{NC}")
        sys.exit(1)
    
    # Find latest
    json_files = list(processed_dir.glob('*_problem.json'))
    if not json_files:
        print(f"{RED}✗ No problem JSON files found in {processed_dir}{NC}")
        sys.exit(1)
    
    latest_problem = sorted(json_files, key=lambda p: p.stem)[-1]
    timestamp = '_'.join(latest_problem.stem.split('_')[:2])
    
    print(f"Using timestamp: {timestamp}")
    
    # Load JSONs
    problem_path = processed_dir / f"{timestamp}_problem.json"
    solution_path = processed_dir / f"{timestamp}_solution.json"
    asset_path = processed_dir / f"{timestamp}_asset.json"
    
    print(f"Loading: {problem_path.name}")
    problem = load_json_file(problem_path)
    if not problem:
        sys.exit(1)
    
    print(f"Loading: {solution_path.name}")
    solution = load_json_file(solution_path)
    
    print(f"Loading: {asset_path.name}")
    asset = load_json_file(asset_path)
    if not asset:
        sys.exit(1)
    
    # Load mail from processed directory
    mail_files = list(processed_dir.glob(f"{timestamp}_*.eml"))
    if not mail_files:
        print(f"{RED}✗ No mail file found for timestamp {timestamp}{NC}")
        print(f"{YELLOW}Expected: {processed_dir}/{timestamp}_*.eml{NC}")
        sys.exit(1)
    
    mail_file = mail_files[0]
    mail_info = extract_mail_info(mail_file)
    print(f"Loading mail: {mail_file.name}")
    
    print(f"\n{GREEN}✓ Data loaded{NC}")
    print(f"  Recipient: {mail_info['sender']}")
    print(f"  Subject: Re: {mail_info['subject']}")
    print(f"  Mail-ID (hex): {problem.get('mail_id', 'N/A')}\n")
    
    # Analyze quality
    print("Analyzing JSON quality...")
    quality_analysis = analyze_quality(problem, solution, asset)
    
    print(f"  ✓ Complete: {quality_analysis['summary']['complete_count']}")
    print(f"  ⚠ Missing:  {quality_analysis['summary']['missing_count']}")
    print(f"  ❓ Unclear:  {quality_analysis['summary']['unclear_count']}")
    print(f"  Overall:    {quality_analysis['summary']['completeness_percent']}%\n")
    
    # Load template
    template_path = WORKING_DIR / 'catalog' / 'mail' / 'added_knowledge_mail.html'
    print(f"Loading template: {template_path.name}")
    template = load_html_template(template_path)
    if not template:
        sys.exit(1)
    
    # Fill template
    print("Filling template with data...")
    html_body = fill_template_v2(template, problem, solution, asset, mail_info, quality_analysis)
    
    print(f"{GREEN}✓ Template filled ({len(html_body)} chars){NC}\n")
    
    # Send mail
    print(f"Sending mail to {mail_info['sender']}...")
    success = send_mail(mail_info['sender'], mail_info['subject'], html_body, mail_config, secrets)
    
    if success:
        print(f"{GREEN}✓ Mail sent successfully!{NC}\n")
        
        # Move mail to sent directory
        print(f"Moving mail to sent directory...")
        if move_to_sent(mail_file, sent_dir):
            print(f"\n{GREEN}✓ Process completed successfully!{NC}")
            sys.exit(0)
        else:
            print(f"\n{YELLOW}⚠ Mail sent but failed to move to sent directory{NC}")
            sys.exit(0)
    else:
        print(f"\n{RED}✗ Failed to send mail{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
