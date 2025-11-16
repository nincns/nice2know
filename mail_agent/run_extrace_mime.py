#!/usr/bin/env python3
"""
Nice2Know - Extract JSONs from Unprocessed Mails
Processes all mails in storage/mails/ from oldest to newest
Moves successful extractions to processed/, failed ones to failed/

IMPROVED: Automatically decodes .eml to plaintext before LLM processing

Usage:
  python run_extract.py              # Process all unprocessed mails
  python run_extract.py --limit 5    # Process max 5 mails
  python run_extract.py --latest     # Process only the latest mail
"""
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List
import argparse

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

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def load_application_config() -> dict:
    """Load application configuration from JSON"""
    config_file = WORKING_DIR / 'config' / 'connections' / 'application.json'
    
    if not config_file.exists():
        print(f"{RED}Error: application.json not found at {config_file}{NC}")
        sys.exit(1)
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}Error loading application config: {e}{NC}")
        sys.exit(1)

def get_storage_base() -> Path:
    """Get absolute storage base path from config"""
    config = load_application_config()
    base_path = config.get('storage', {}).get('base_path', './storage')
    
    # Resolve relative path from WORKING_DIR
    if not Path(base_path).is_absolute():
        storage_base = WORKING_DIR / base_path
    else:
        storage_base = Path(base_path)
    
    return storage_base.resolve()

def get_unprocessed_mails(mail_dir: Path) -> List[Path]:
    """Get all .eml files, sorted from oldest to newest"""
    if not mail_dir.exists():
        return []
    
    mail_files = list(mail_dir.glob("*.eml"))
    
    if not mail_files:
        return []
    
    def get_timestamp(filepath: Path) -> datetime:
        try:
            filename = filepath.stem
            timestamp_str = '_'.join(filename.split('_')[:2])
            return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            return datetime.fromtimestamp(filepath.stat().st_mtime)
    
    # Sort oldest to newest (FIFO)
    return sorted(mail_files, key=get_timestamp)

def extract_json(mail_path: Path, json_type: str, output_dir: Path, timeout: int = 300) -> Tuple[bool, Optional[Path]]:
    """
    Extract JSON using llm_request.py with increased timeout
    Automatically decodes .eml to plaintext before LLM processing
    
    Args:
        mail_path: Path to .eml file
        json_type: 'problem', 'solution', or 'asset'
        output_dir: Directory for output files
        timeout: LLM timeout in seconds (default 300)
    
    Returns:
        (success, output_path)
    """
    prompts = {
        'problem': 'catalog/prompts/extract_problem.txt',
        'solution': 'catalog/prompts/extract_solution.txt',
        'asset': 'catalog/prompts/extract_asset.txt'
    }
    
    schemas = {
        'problem': 'catalog/json_store/problem_schema.json',
        'solution': 'catalog/json_store/solution_schema.json',
        'asset': 'catalog/json_store/asset_schema.json'
    }
    
    if json_type not in prompts:
        return False, None
    
    # Generate output filename
    mail_parts = mail_path.stem.split('_')
    if len(mail_parts) >= 2:
        mail_timestamp = f"{mail_parts[0]}_{mail_parts[1]}"
    else:
        mail_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_path = output_dir / f"{mail_timestamp}_{json_type}.json"
    
    # === NEW: Parse .eml and extract plaintext ===
    temp_txt = None
    try:
        sys.path.insert(0, str(WORKING_DIR))
        from agents.mail_parser import MailParser
        
        parser = MailParser()
        with open(mail_path, 'rb') as f:
            raw_email = f.read()
        
        parsed = parser.parse(raw_email)
        if not parsed:
            print(f"{RED}✗ (parsing failed){NC}")
            return False, None
        
        # Get plaintext (prefer plain over HTML)
        plaintext = parsed['body']['plain'] or parsed['body']['html']
        
        if not plaintext:
            print(f"{RED}✗ (no body content){NC}")
            return False, None
        
        # Create temporary .txt file for LLM
        temp_txt = mail_path.parent / f"{mail_path.stem}_decoded.txt"
        with open(temp_txt, 'w', encoding='utf-8') as f:
            f.write(plaintext)
        
        # Use decoded .txt instead of .eml
        mailbody_path = temp_txt
        
    except Exception as e:
        print(f"{RED}✗ (decode error: {str(e)[:50]}){NC}")
        # Cleanup temp file on error
        if temp_txt and temp_txt.exists():
            temp_txt.unlink()
        return False, None
    
    # Build command with decoded plaintext
    llm_script = WORKING_DIR / 'agents' / 'llm_request.py'
    
    cmd = [
        sys.executable,
        str(llm_script),
        '--pre_prompt', str(WORKING_DIR / prompts[json_type]),
        '--json', str(WORKING_DIR / schemas[json_type]),
        '--mailbody', str(mailbody_path),
        '--export', str(output_path)
    ]
    
    print(f"  Extracting {json_type}...", end=' ', flush=True)
    
    try:
        # Run with longer timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Cleanup temp file
        if temp_txt and temp_txt.exists():
            temp_txt.unlink()
        
        if result.returncode == 0 and output_path.exists():
            print(f"{GREEN}✓{NC}")
            return True, output_path
        else:
            print(f"{RED}✗{NC}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print(f"{RED}✗ TIMEOUT{NC}")
        # Cleanup temp file on timeout
        if temp_txt and temp_txt.exists():
            temp_txt.unlink()
        return False, None
    except Exception as e:
        print(f"{RED}✗ {e}{NC}")
        # Cleanup temp file on error
        if temp_txt and temp_txt.exists():
            temp_txt.unlink()
        return False, None

def process_mail(mail_path: Path, output_dir: Path, failed_dir: Path, processed_dir: Path) -> bool:
    """
    Process a single mail: extract all JSONs and move to appropriate folder
    
    Returns:
        True if all extractions successful, False otherwise
    """
    print(f"\n{CYAN}Processing: {mail_path.name}{NC}")
    
    # Extract all JSON types
    json_types = ['problem', 'solution', 'asset']
    results = {}
    
    for json_type in json_types:
        success, output_path = extract_json(mail_path, json_type, output_dir, timeout=300)
        results[json_type] = (success, output_path)
    
    # Check if all succeeded
    all_success = all(success for success, _ in results.values())
    
    # Move mail to appropriate folder
    if all_success:
        dest = processed_dir / mail_path.name
        shutil.move(str(mail_path), str(dest))
        print(f"  {GREEN}→ Moved to processed/{NC}")
        return True
    else:
        dest = failed_dir / mail_path.name
        shutil.move(str(mail_path), str(dest))
        print(f"  {RED}→ Moved to failed/ (partial extraction){NC}")
        
        # List what failed
        failed = [jt for jt, (s, _) in results.items() if not s]
        print(f"    Failed: {', '.join(failed)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Nice2Know Mail Extraction Pipeline')
    parser.add_argument('--limit', type=int, help='Max number of mails to process')
    parser.add_argument('--latest', action='store_true', help='Process only the latest mail')
    
    args = parser.parse_args()
    
    # Get storage base from config
    storage_base = get_storage_base()
    
    # Define directories from config
    mail_dir = storage_base / 'mails'
    output_dir = storage_base / 'processed'
    failed_dir = storage_base / 'failed'
    processed_dir = storage_base / 'processed'
    
    # Create directories if they don't exist
    for directory in [mail_dir, output_dir, failed_dir, processed_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know - Mail Extraction Pipeline (Improved){NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Working directory:   {WORKING_DIR}")
    print(f"Storage base:        {storage_base}")
    print(f"Mail directory:      {mail_dir}")
    print(f"Processed directory: {processed_dir}")
    print(f"Failed directory:    {failed_dir}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{CYAN}NOTE: .eml files are automatically decoded to plaintext{NC}")
    print(f"{CYAN}      for LLM processing (originals preserved){NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print()
    
    # Get unprocessed mails
    mails = get_unprocessed_mails(mail_dir)
    
    if not mails:
        print(f"{YELLOW}No unprocessed mails found in {mail_dir}{NC}")
        sys.exit(0)
    
    # Apply filters
    if args.latest:
        mails = [mails[-1]]  # Only newest
        print(f"Processing latest mail only...")
    elif args.limit:
        mails = mails[:args.limit]
        print(f"Processing up to {args.limit} mails...")
    else:
        print(f"Processing all {len(mails)} unprocessed mails (oldest first)...")
    
    print()
    
    # Process each mail
    success_count = 0
    failed_count = 0
    
    for i, mail_path in enumerate(mails, 1):
        print(f"{BLUE}[{i}/{len(mails)}]{NC}", end=' ')
        
        if process_mail(mail_path, output_dir, failed_dir, processed_dir):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Extraction Summary{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"  {GREEN}Successful: {success_count}{NC}")
    print(f"  {RED}Failed:     {failed_count}{NC}")
    print(f"  {BLUE}Total:      {len(mails)}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")
    
    if success_count == len(mails):
        print(f"{GREEN}✓ All mails processed successfully!{NC}")
        sys.exit(0)
    elif success_count > 0:
        print(f"{YELLOW}⚠ Partial success: {success_count}/{len(mails)} processed{NC}")
        print(f"\n{YELLOW}Failed mails moved to: {failed_dir}{NC}")
        print(f"{YELLOW}Review and retry manually if needed{NC}")
        sys.exit(1)
    else:
        print(f"{RED}✗ All extractions failed{NC}")
        print(f"{RED}Check LLM connectivity and mail format{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
