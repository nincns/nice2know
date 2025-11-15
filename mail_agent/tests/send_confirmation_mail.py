#!/usr/bin/env python3
"""
Nice2Know - Send Confirmation Mail
Sends HTML confirmation mail to original sender with extracted knowledge
"""
import sys
import json
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.message import EmailMessage
from datetime import datetime
from typing import Optional, Dict, Any
import email
from email import policy

# Auto-detect mail_agent/ directory
def find_mail_agent_root(start_path: Path) -> Path:
    """Walk up directory tree to find mail_agent/ (has agents/, catalog/, storage/)"""
    current = start_path
    for _ in range(5):
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'storage').exists():
            return current
        if current.parent != current:
            current = current.parent
        else:
            break
    return start_path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKING_DIR = find_mail_agent_root(SCRIPT_DIR)

# Add to Python path for imports
sys.path.insert(0, str(WORKING_DIR))

from utils.credentials import get_credentials

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def load_json_file(filepath: Path) -> Optional[Dict]:
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}✗ Failed to load {filepath.name}: {e}{NC}")
        return None

def load_html_template(filepath: Path) -> Optional[str]:
    """Load HTML template"""
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
        
        # Extract email from "Name <email@domain.com>" format
        if '<' in sender and '>' in sender:
            sender_email = sender[sender.find('<')+1:sender.find('>')]
        else:
            sender_email = sender
        
        return {
            'sender': sender_email,
            'subject': subject
        }
    except Exception as e:
        print(f"{RED}✗ Failed to parse mail: {e}{NC}")
        return {'sender': 'unknown@example.com', 'subject': 'No Subject'}

def fill_template(template: str, problem: Dict, solution: Dict, asset: Dict,
                  mail_info: Dict) -> str:
    """Fill HTML template with data (simple string replacement)"""
    
    # Problem data
    template = template.replace('{{reporter_name}}',
                               problem.get('reporter', {}).get('name', 'Benutzer'))
    template = template.replace('{{problem_title}}',
                               problem.get('problem', {}).get('title', 'N/A'))
    template = template.replace('{{problem_description}}',
                               problem.get('problem', {}).get('description', 'N/A'))
    template = template.replace('{{problem_severity}}',
                               problem.get('classification', {}).get('severity', 'medium'))
    template = template.replace('{{problem_category}}',
                               problem.get('classification', {}).get('category', 'N/A'))
    template = template.replace('{{problem_status}}',
                               problem.get('status', 'new'))
    
    # Symptoms list
    symptoms = problem.get('problem', {}).get('symptoms', [])
    symptoms_html = '\n'.join([f'<li>{s}</li>' for s in symptoms]) if symptoms else '<li>Keine Symptome erfasst</li>'
    template = template.replace('{{#problem_symptoms}}\n                            <li>{{.}}</li>\n                            {{/problem_symptoms}}',
                               symptoms_html)
    
    # Error messages (optional section)
    error_messages = problem.get('problem', {}).get('error_messages', [])
    if error_messages:
        errors_html = '\n'.join([f'<li>{e}</li>' for e in error_messages])
        template = template.replace('{{#problem_error_messages}}', '')
        template = template.replace('{{/problem_error_messages}}', '')
        template = template.replace('{{#problem_error_messages}}\n                            <li>{{.}}</li>\n                            {{/problem_error_messages}}',
                                   errors_html)
    else:
        # Remove error messages section completely
        import re
        template = re.sub(r'{{#problem_error_messages}}.*?{{/problem_error_messages}}', '',
                         template, flags=re.DOTALL)
    
    # Solution data
    has_solution = solution and solution.get('solution', {}).get('steps', [])
    
    if has_solution:
        template = template.replace('{{#has_solution}}', '')
        template = template.replace('{{/has_solution}}', '')
        
        template = template.replace('{{solution_title}}',
                                   solution.get('solution', {}).get('title', 'N/A'))
        template = template.replace('{{solution_description}}',
                                   solution.get('solution', {}).get('description', 'N/A'))
        template = template.replace('{{solution_type}}',
                                   solution.get('solution', {}).get('type', 'N/A'))
        template = template.replace('{{solution_approach}}',
                                   solution.get('solution', {}).get('approach', 'N/A'))
        template = template.replace('{{solution_complexity}}',
                                   solution.get('metadata', {}).get('complexity', 'N/A'))
        template = template.replace('{{solution_estimated_time}}',
                                   solution.get('metadata', {}).get('estimated_time', 'N/A'))
        
        # Prerequisites (optional)
        prereqs = solution.get('solution', {}).get('prerequisites', [])
        if prereqs:
            prereqs_html = '\n'.join([f'<li>{p}</li>' for p in prereqs])
            template = template.replace('{{#solution_prerequisites}}', '')
            template = template.replace('{{/solution_prerequisites}}', '')
            template = template.replace('{{#solution_prerequisites}}\n                            <li>{{.}}</li>\n                            {{/solution_prerequisites}}',
                                       prereqs_html)
        else:
            import re
            template = re.sub(r'{{#solution_prerequisites}}.*?{{/solution_prerequisites}}', '',
                             template, flags=re.DOTALL)
        
        # Steps
        steps = solution.get('solution', {}).get('steps', [])
        steps_html = ''
        for step in steps:
            step_html = '<div class="step">'
            step_html += f'<div class="step-action">{step.get("action", "N/A")}</div>'
            step_html += f'<div class="step-details">{step.get("details", "N/A")}</div>'
            if step.get('command'):
                step_html += f'<div class="step-command">{step["command"]}</div>'
            step_html += f'<div class="step-result">✓ Erwartetes Ergebnis: {step.get("expected_result", "N/A")}</div>'
            step_html += '</div>'
            steps_html += step_html
        
        template = template.replace('{{#solution_steps}}\n                            <div class="step">\n                                <div class="step-action">{{action}}</div>\n                                <div class="step-details">{{details}}</div>\n                                {{#command}}\n                                <div class="step-command">{{command}}</div>\n                                {{/command}}\n                                <div class="step-result">✓ Erwartetes Ergebnis: {{expected_result}}</div>\n                            </div>\n                            {{/solution_steps}}',
                                   steps_html)
        
        # Tags (optional)
        tags = solution.get('tags', [])
        if tags:
            tags_html = '\n'.join([f'<span class="tag">{t}</span>' for t in tags])
            template = template.replace('{{#solution_tags}}', '')
            template = template.replace('{{/solution_tags}}', '')
            template = template.replace('{{#solution_tags}}\n                            <span class="tag">{{.}}</span>\n                            {{/solution_tags}}',
                                       tags_html)
        else:
            import re
            template = re.sub(r'{{#solution_tags}}.*?{{/solution_tags}}', '',
                             template, flags=re.DOTALL)
    else:
        # Remove solution section completely
        import re
        template = re.sub(r'{{#has_solution}}.*?{{/has_solution}}', '',
                         template, flags=re.DOTALL)
    
    # Asset data
    template = template.replace('{{asset_name}}',
                               asset.get('asset', {}).get('display_name',
                                  asset.get('asset', {}).get('name', 'N/A')))
    template = template.replace('{{asset_description}}',
                               asset.get('asset', {}).get('description', 'N/A'))
    template = template.replace('{{asset_type}}',
                               asset.get('asset', {}).get('type', 'N/A'))
    template = template.replace('{{asset_category}}',
                               asset.get('asset', {}).get('category', 'N/A'))
    template = template.replace('{{asset_criticality}}',
                               asset.get('asset', {}).get('criticality', 'N/A'))
    template = template.replace('{{asset_status}}',
                               asset.get('asset', {}).get('status', 'N/A'))
    
    # Technical details (optional)
    software = asset.get('technical', {}).get('software')
    if software:
        template = template.replace('{{#asset_software}}', '')
        template = template.replace('{{/asset_software}}', '')
        template = template.replace('{{asset_software}}', software)
        
        version = asset.get('technical', {}).get('version')
        if version:
            template = template.replace('{{#asset_version}}', '')
            template = template.replace('{{/asset_version}}', '')
            template = template.replace('{{asset_version}}', version)
        else:
            import re
            template = re.sub(r'{{#asset_version}}.*?{{/asset_version}}', '',
                             template, flags=re.DOTALL)
        
        platform = asset.get('technical', {}).get('platform')
        if platform:
            template = template.replace('{{#asset_platform}}', '')
            template = template.replace('{{/asset_platform}}', '')
            template = template.replace('{{asset_platform}}', platform)
        else:
            import re
            template = re.sub(r'{{#asset_platform}}.*?{{/asset_platform}}', '',
                             template, flags=re.DOTALL)
    else:
        import re
        template = re.sub(r'{{#asset_software}}.*?{{/asset_software}}', '',
                         template, flags=re.DOTALL)
    
    # Footer data
    template = template.replace('{{magic_link}}', '#')  # TODO: Generate actual link
    template = template.replace('{{confirm_link}}', '#')  # TODO: Generate actual link
    template = template.replace('{{support_email}}', 'support@example.com')  # TODO: From config
    template = template.replace('{{case_id}}', problem.get('id', 'N/A'))
    template = template.replace('{{created_at}}',
                               datetime.now().strftime('%Y-%m-%d %H:%M'))
    template = template.replace('{{mail_id}}', problem.get('mail_id', 'N/A'))
    
    return template

def send_mail(recipient: str, subject: str, html_body: str) -> bool:
    """Send HTML email via SMTP"""
    try:
        creds = get_credentials()
        smtp_config = creds.get_mail_config()
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_config.get('smtp_user', 'noreply@example.com')
        msg['To'] = recipient
        msg['Subject'] = f"Re: {subject}"
        
        # Plain text fallback
        text_body = "Bitte öffnen Sie diese E-Mail in einem HTML-fähigen E-Mail-Client."
        
        # Attach parts
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect and send
        smtp_server = smtp_config.get('smtp_server', 'localhost')
        smtp_port = smtp_config.get('smtp_port', 587)
        smtp_user = smtp_config.get('smtp_user')
        smtp_password = smtp_config.get('smtp_password')
        
        print(f"[SMTP] Connecting to {smtp_server}:{smtp_port}...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"{RED}✗ Failed to send mail: {e}{NC}")
        return False

def main():
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know - Send Confirmation Mail{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Working directory: {WORKING_DIR}\n")
    
    # Paths
    processed_dir = WORKING_DIR / 'storage' / 'processed'
    if not processed_dir.exists():
        print(f"{RED}✗ Processed directory not found{NC}")
        sys.exit(1)
    
    # Find matching JSON files (same timestamp)
    json_files = list(processed_dir.glob('*_problem.json'))
    if not json_files:
        print(f"{RED}✗ No problem JSON files found{NC}")
        sys.exit(1)
    
    # Use most recent
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
    
    # Load mail for sender/subject
    mail_dir = WORKING_DIR / 'storage' / 'mails'
    mail_files = list(mail_dir.glob(f"{timestamp}_*.eml"))
    if not mail_files:
        print(f"{YELLOW}⚠ No mail file found for timestamp{NC}")
        mail_info = {'sender': 'test@example.com', 'subject': 'Test'}
    else:
        mail_path = mail_files[0]
        print(f"Loading mail: {mail_path.name}")
        mail_info = extract_mail_info(mail_path)
    
    print(f"\n{GREEN}✓ Data loaded{NC}")
    print(f"  Recipient: {mail_info['sender']}")
    print(f"  Subject: Re: {mail_info['subject']}\n")
    
    # Load HTML template
    template_path = WORKING_DIR / 'catalog' / 'mail' / 'added_knowledge_mail.html'
    print(f"Loading template: {template_path.name}")
    template = load_html_template(template_path)
    if not template:
        sys.exit(1)
    
    # Fill template
    print("Filling template with data...")
    html_body = fill_template(template, problem, solution, asset, mail_info)
    
    print(f"{GREEN}✓ Template filled ({len(html_body)} chars){NC}\n")
    
    # Send mail
    print(f"Sending mail to {mail_info['sender']}...")
    success = send_mail(mail_info['sender'], mail_info['subject'], html_body)
    
    if success:
        print(f"\n{GREEN}✓ Mail sent successfully!{NC}")
        sys.exit(0)
    else:
        print(f"\n{RED}✗ Failed to send mail{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
