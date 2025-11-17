#!/usr/bin/env python3
"""
Nice2Know - Classify Incoming Mails (Stage 0)
Processes all mails in storage/mails/ and creates classification JSONs
This runs BEFORE run_extract.py to enable intelligent routing

Usage:
  python run_classifier.py              # Classify all unclassified mails
  python run_classifier.py --limit 5    # Classify max 5 mails
  python run_classifier.py --latest     # Classify only the latest mail
  python run_classifier.py --reclassify # Re-classify already classified mails
"""
import sys
import subprocess
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
MAGENTA = '\033[0;35m'
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

def get_unclassified_mails(mail_dir: Path, classified_dir: Path, reclassify: bool = False) -> List[Path]:
    """
    Get all .eml files that don't have a classification JSON yet
    Sorted from oldest to newest
    
    Args:
        mail_dir: Directory containing .eml files
        classified_dir: Directory containing classification JSONs
        reclassify: If True, return all mails regardless of classification status
    """
    if not mail_dir.exists():
        return []
    
    mail_files = list(mail_dir.glob("*.eml"))
    
    if not mail_files:
        return []
    
    if reclassify:
        # Return all mails
        unclassified = mail_files
    else:
        # Filter out already classified mails
        unclassified = []
        for mail_file in mail_files:
            # Generate expected classification filename
            mail_parts = mail_file.stem.split('_')
            if len(mail_parts) >= 2:
                mail_timestamp = f"{mail_parts[0]}_{mail_parts[1]}"
            else:
                mail_timestamp = mail_file.stem
            
            classification_file = classified_dir / f"{mail_timestamp}_identifier.json"
            
            # Only process if no classification exists
            if not classification_file.exists():
                unclassified.append(mail_file)
    
    def get_timestamp(filepath: Path) -> datetime:
        try:
            filename = filepath.stem
            timestamp_str = '_'.join(filename.split('_')[:2])
            return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            return datetime.fromtimestamp(filepath.stat().st_mtime)
    
    # Sort oldest to newest (FIFO)
    return sorted(unclassified, key=get_timestamp)

def classify_mail(mail_path: Path, output_dir: Path, timeout: int = 300) -> Tuple[bool, Optional[Path], Optional[dict]]:
    """
    Classify mail using llm_request.py
    
    Args:
        mail_path: Path to .eml file
        output_dir: Directory for output files
        timeout: LLM timeout in seconds (default 300)
    
    Returns:
        (success, output_path, classification_data)
    """
    prompt_file = 'catalog/prompts/extract_identifier.txt'
    schema_file = 'catalog/json_store/identifier_schema.json'
    
    # Generate output filename
    mail_parts = mail_path.stem.split('_')
    if len(mail_parts) >= 2:
        mail_timestamp = f"{mail_parts[0]}_{mail_parts[1]}"
    else:
        mail_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_path = output_dir / f"{mail_timestamp}_identifier.json"
    
    # Build command
    llm_script = WORKING_DIR / 'agents' / 'llm_request.py'
    
    cmd = [
        sys.executable,
        str(llm_script),
        '--pre_prompt', str(WORKING_DIR / prompt_file),
        '--json', str(WORKING_DIR / schema_file),
        '--mailbody', str(mail_path),
        '--export', str(output_path)
    ]
    
    print(f"  Classifying mail...", end=' ', flush=True)
    
    try:
        # Run with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and output_path.exists():
            # Load and return classification data
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    classification = json.load(f)
                print(f"{GREEN}✓{NC}")
                return True, output_path, classification
            except Exception as e:
                print(f"{YELLOW}✓ (but couldn't parse JSON){NC}")
                return True, output_path, None
        else:
            print(f"{RED}✗{NC}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False, None, None
            
    except subprocess.TimeoutExpired:
        print(f"{RED}✗ TIMEOUT{NC}")
        return False, None, None
    except Exception as e:
        print(f"{RED}✗ {e}{NC}")
        return False, None, None

def display_classification_summary(classification: dict):
    """Display a nice summary of the classification"""
    if not classification:
        return
    
    try:
        mail_class = classification.get('mail_classification', {})
        content = classification.get('content_analysis', {})
        workflow = classification.get('workflow_routing', {})
        participants = classification.get('participants', {})
        
        print(f"\n  {MAGENTA}Classification Summary:{NC}")
        print(f"    Type:        {mail_class.get('type', 'unknown')}")
        print(f"    Confidence:  {mail_class.get('confidence', 0):.2f}")
        print(f"    Urgency:     {content.get('urgency_level', 'unknown')}")
        print(f"    Complexity:  {content.get('complexity', 'unknown')}")
        
        print(f"\n  {MAGENTA}Content Flags:{NC}")
        print(f"    Problem:     {content.get('has_problem', False)}")
        print(f"    Solution:    {content.get('has_solution', False)}")
        print(f"    Asset Info:  {content.get('has_asset_info', False)}")
        
        print(f"\n  {MAGENTA}Workflow Routing:{NC}")
        print(f"    Extract Problem:  {workflow.get('should_extract_problem', False)}")
        print(f"    Extract Solution: {workflow.get('should_extract_solution', False)}")
        print(f"    Extract Assets:   {workflow.get('should_extract_assets', False)}")
        print(f"    Priority:         {workflow.get('processing_priority', 0)}")
        
        sender = participants.get('sender', {})
        if sender:
            print(f"\n  {MAGENTA}Sender:{NC}")
            print(f"    Name:  {sender.get('name', 'unknown')}")
            print(f"    Role:  {sender.get('role', 'unknown')}")
        
    except Exception as e:
        print(f"  {YELLOW}Could not display summary: {e}{NC}")

def process_mail(mail_path: Path, classified_dir: Path) -> Tuple[bool, Optional[dict]]:
    """
    Classify a single mail
    
    Returns:
        (success, classification_data)
    """
    print(f"\n{CYAN}Processing: {mail_path.name}{NC}")
    
    success, output_path, classification = classify_mail(mail_path, classified_dir, timeout=300)
    
    if success:
        print(f"  {GREEN}→ Classification saved to: {output_path.name}{NC}")
        if classification:
            display_classification_summary(classification)
        return True, classification
    else:
        print(f"  {RED}→ Classification failed{NC}")
        return False, None

def main():
    parser = argparse.ArgumentParser(description='Nice2Know Mail Classification Pipeline (Stage 0)')
    parser.add_argument('--limit', type=int, help='Max number of mails to classify')
    parser.add_argument('--latest', action='store_true', help='Classify only the latest mail')
    parser.add_argument('--reclassify', action='store_true', help='Re-classify already classified mails')
    
    args = parser.parse_args()
    
    # Get storage base from config
    storage_base = get_storage_base()
    
    # Define directories from config
    mail_dir = storage_base / 'mails'
    classified_dir = storage_base / 'classified'
    
    # Create directories if they don't exist
    for directory in [mail_dir, classified_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know - Mail Classification Pipeline (Stage 0){NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Working directory:      {WORKING_DIR}")
    print(f"Storage base:           {storage_base}")
    print(f"Mail directory:         {mail_dir}")
    print(f"Classification output:  {classified_dir}")
    if args.reclassify:
        print(f"{YELLOW}Mode:                   RE-CLASSIFY (overwrite existing){NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print()
    
    # Get unclassified mails
    mails = get_unclassified_mails(mail_dir, classified_dir, reclassify=args.reclassify)
    
    if not mails:
        if args.reclassify:
            print(f"{YELLOW}No mails found in {mail_dir}{NC}")
        else:
            print(f"{YELLOW}No unclassified mails found in {mail_dir}{NC}")
            print(f"{YELLOW}All mails already have classification JSONs{NC}")
        sys.exit(0)
    
    # Apply filters
    if args.latest:
        mails = [mails[-1]]  # Only newest
        print(f"Classifying latest mail only...")
    elif args.limit:
        mails = mails[:args.limit]
        print(f"Classifying up to {args.limit} mails...")
    else:
        if args.reclassify:
            print(f"Re-classifying all {len(mails)} mails (oldest first)...")
        else:
            print(f"Classifying all {len(mails)} unclassified mails (oldest first)...")
    
    print()
    
    # Process each mail
    success_count = 0
    failed_count = 0
    classifications = []
    
    for i, mail_path in enumerate(mails, 1):
        print(f"{BLUE}[{i}/{len(mails)}]{NC}", end=' ')
        
        success, classification = process_mail(mail_path, classified_dir)
        
        if success:
            success_count += 1
            if classification:
                classifications.append(classification)
        else:
            failed_count += 1
    
    # Summary
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Classification Summary{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"  {GREEN}Successful: {success_count}{NC}")
    print(f"  {RED}Failed:     {failed_count}{NC}")
    print(f"  {BLUE}Total:      {len(mails)}{NC}")
    
    # Statistics from classifications
    if classifications:
        print(f"\n{MAGENTA}Classification Statistics:{NC}")
        
        # Count types
        types = {}
        for c in classifications:
            mail_type = c.get('mail_classification', {}).get('type', 'unknown')
            types[mail_type] = types.get(mail_type, 0) + 1
        
        print(f"  Types:")
        for mail_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"    {mail_type:20s}: {count}")
        
        # Count urgency levels
        urgencies = {}
        for c in classifications:
            urgency = c.get('content_analysis', {}).get('urgency_level', 'unknown')
            urgencies[urgency] = urgencies.get(urgency, 0) + 1
        
        print(f"\n  Urgency Levels:")
        for urgency, count in sorted(urgencies.items(), key=lambda x: x[1], reverse=True):
            print(f"    {urgency:20s}: {count}")
        
        # Count routing decisions
        extract_problem = sum(1 for c in classifications 
                             if c.get('workflow_routing', {}).get('should_extract_problem', False))
        extract_solution = sum(1 for c in classifications 
                              if c.get('workflow_routing', {}).get('should_extract_solution', False))
        extract_assets = sum(1 for c in classifications 
                            if c.get('workflow_routing', {}).get('should_extract_assets', False))
        
        print(f"\n  Workflow Routing:")
        print(f"    Should extract problem:  {extract_problem}/{len(classifications)}")
        print(f"    Should extract solution: {extract_solution}/{len(classifications)}")
        print(f"    Should extract assets:   {extract_assets}/{len(classifications)}")
    
    print(f"{BLUE}{'=' * 60}{NC}\n")
    
    if success_count == len(mails):
        print(f"{GREEN}✓ All mails classified successfully!{NC}")
        print(f"\n{CYAN}Next step:{NC}")
        print(f"  Run: python run_extract.py")
        print(f"  (This will use the classifications to route extraction processes)")
        sys.exit(0)
    elif success_count > 0:
        print(f"{YELLOW}⚠ Partial success: {success_count}/{len(mails)} classified{NC}")
        sys.exit(1)
    else:
        print(f"{RED}✗ All classifications failed{NC}")
        print(f"{RED}Check LLM connectivity and mail format{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
