#!/usr/bin/env python3
"""
Nice2Know - Test Script: Extract All JSONs from Latest Mail
Finds the most recent mail and extracts Problem, Solution, and Asset JSONs

Usage:
  python test_extract_all.py              # From mail_agent/ directory
  python mail_agent/test_extract_all.py   # From project root
  
The script uses WORKING_DIR to find all resources relative to the script location.
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# ============================================================================
# CONFIGURATION: Working Directory
# ============================================================================
# SCRIPT_DIR: Actual location of this script file
# WORKING_DIR: Base directory for all operations (storage, catalog, agents)
#
# Auto-detection: Find mail_agent/ directory by walking up from script location
# If script is in mail_agent/tests/ → finds mail_agent/
# If script is in mail_agent/ → uses mail_agent/
#
# Manual override (uncomment to use):
#   WORKING_DIR = Path("/absolute/path/to/mail_agent")
# ============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent

# Auto-detect mail_agent/ directory
def find_mail_agent_root(start_path: Path) -> Path:
    """Walk up directory tree to find mail_agent/ (has agents/, catalog/, storage/)"""
    current = start_path
    max_levels = 5  # Don't go too far up
    
    for _ in range(max_levels):
        # Check if this looks like mail_agent/ directory
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'storage').exists():
            return current
        
        # Check if we're in a subdirectory of mail_agent/
        if current.parent != current:  # Not at filesystem root
            current = current.parent
        else:
            break
    
    # Fallback: assume script is in mail_agent/
    return start_path

WORKING_DIR = find_mail_agent_root(SCRIPT_DIR)

# Manual override (uncomment to set custom path):
# WORKING_DIR = Path("/custom/path/to/mail_agent")

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

def find_latest_mail(mail_dir: Path) -> Optional[Path]:
    """Find the most recent .eml file based on timestamp in filename"""
    mail_files = list(mail_dir.glob("*.eml"))
    
    if not mail_files:
        return None
    
    # Parse timestamps from filenames (format: YYYYMMDD_HHMMSS_*.eml)
    def get_timestamp(filepath: Path) -> datetime:
        try:
            filename = filepath.stem
            timestamp_str = '_'.join(filename.split('_')[:2])  # YYYYMMDD_HHMMSS
            return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except:
            # Fallback to file modification time
            return datetime.fromtimestamp(filepath.stat().st_mtime)
    
    # Sort by timestamp, most recent first
    sorted_mails = sorted(mail_files, key=get_timestamp, reverse=True)
    return sorted_mails[0]

def extract_json(mail_path: Path, json_type: str, output_dir: Path) -> Tuple[bool, Optional[Path]]:
    """
    Extract JSON using llm_request.py
    
    Args:
        mail_path: Path to .eml file
        json_type: 'problem', 'solution', or 'asset'
        output_dir: Directory for output files
    
    Returns:
        (success, output_path)
    """
    # Determine prompt and schema files
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
        print(f"{RED}✗ Unknown JSON type: {json_type}{NC}")
        return False, None
    
    # Generate output filename using mail timestamp
    mail_parts = mail_path.stem.split('_')
    if len(mail_parts) >= 2:
        # Use mail timestamp: YYYYMMDD_HHMMSS
        mail_timestamp = f"{mail_parts[0]}_{mail_parts[1]}"
    else:
        # Fallback to current time
        mail_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_path = output_dir / f"{mail_timestamp}_{json_type}.json"
    
    # Build command
    llm_script = WORKING_DIR / 'agents' / 'llm_request.py'
    
    cmd = [
        sys.executable,  # Use same Python interpreter
        str(llm_script),
        '--pre_prompt', str(WORKING_DIR / prompts[json_type]),
        '--json', str(WORKING_DIR / schemas[json_type]),
        '--mailbody', str(mail_path),
        '--export', str(output_path)
    ]
    
    print(f"\n{CYAN}{'=' * 60}{NC}")
    print(f"{CYAN}Extracting {json_type.upper()} JSON{NC}")
    print(f"{CYAN}{'=' * 60}{NC}")
    print(f"Mail:    {mail_path.name}")
    print(f"Prompt:  {prompts[json_type]}")
    print(f"Schema:  {schemas[json_type]}")
    print(f"Output:  {output_path.name}")
    print()
    
    try:
        # Run llm_request.py
        result = subprocess.run(
            cmd,
            capture_output=False,  # Show real-time output
            text=True
        )
        
        if result.returncode == 0 and output_path.exists():
            print(f"\n{GREEN}✓ {json_type.upper()} JSON extracted successfully{NC}")
            print(f"  → {output_path}")
            return True, output_path
        else:
            print(f"\n{RED}✗ {json_type.upper()} extraction failed{NC}")
            return False, None
            
    except Exception as e:
        print(f"\n{RED}✗ Error during extraction: {e}{NC}")
        return False, None

def main():
    """Main test runner"""
    mail_dir = WORKING_DIR / 'storage' / 'mails'
    output_dir = WORKING_DIR / 'storage' / 'processed'
    
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know - Extract All JSONs from Latest Mail{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Script location:   {SCRIPT_DIR}")
    print(f"Working directory: {WORKING_DIR}")
    print()
    
    # Check directories
    if not mail_dir.exists():
        print(f"{RED}✗ Mail directory not found: {mail_dir}{NC}")
        print(f"\n{YELLOW}Troubleshooting:{NC}")
        print(f"  Script location:   {SCRIPT_DIR}")
        print(f"  Working directory: {WORKING_DIR}")
        print(f"  Expected structure:")
        print(f"    {WORKING_DIR}/")
        print(f"    ├── agents/")
        print(f"    ├── catalog/")
        print(f"    └── storage/")
        print(f"        └── mails/")
        print(f"\n{YELLOW}Solutions:{NC}")
        print(f"  1. Check if storage/mails/ exists in {WORKING_DIR}")
        print(f"  2. Create it: mkdir -p {mail_dir}")
        print(f"  3. Or set WORKING_DIR manually in the script")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find latest mail
    print(f"Searching for mails in: {mail_dir}")
    latest_mail = find_latest_mail(mail_dir)
    
    if not latest_mail:
        print(f"{RED}✗ No mail files found in {mail_dir}{NC}")
        sys.exit(1)
    
    print(f"{GREEN}✓ Found latest mail: {latest_mail.name}{NC}")
    
    # Extract timestamp from filename
    try:
        timestamp_str = '_'.join(latest_mail.stem.split('_')[:2])
        mail_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        print(f"  Mail timestamp: {mail_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        print(f"  (Could not parse timestamp)")
    
    print()
    
    # Extract all JSON types
    json_types = ['problem', 'solution', 'asset']
    results = {}
    
    for json_type in json_types:
        success, output_path = extract_json(latest_mail, json_type, output_dir)
        results[json_type] = (success, output_path)
    
    # Summary
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Extraction Summary{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"Source mail: {latest_mail.name}\n")
    
    success_count = 0
    for json_type in json_types:
        success, output_path = results[json_type]
        status = f"{GREEN}✓ OK{NC}" if success else f"{RED}✗ FAILED{NC}"
        print(f"  {json_type.capitalize():10s}: {status}")
        if output_path:
            print(f"               → {output_path.name}")
        if success:
            success_count += 1
    
    print(f"\n{BLUE}{'=' * 60}{NC}")
    
    if success_count == len(json_types):
        print(f"{GREEN}✓ All extractions completed successfully! ({success_count}/{len(json_types)}){NC}")
        sys.exit(0)
    elif success_count > 0:
        print(f"{YELLOW}⚠ Partial success: {success_count}/{len(json_types)} extractions completed{NC}")
        sys.exit(1)
    else:
        print(f"{RED}✗ All extractions failed{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
