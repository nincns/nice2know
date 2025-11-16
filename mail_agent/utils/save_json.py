#!/usr/bin/env python3
"""
Nice2Know - Save JSON via Python (No Backup)
Overwrites JSON files directly without backup

Usage:
  python save_json.py <mail_id> <problem.json> <solution.json> <asset.json>
"""
import sys
import json
from pathlib import Path

def find_mail_agent_root(start_path: Path) -> Path:
    """Find mail_agent root directory"""
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
    
    # Fallback for when script is in mail_agent/utils/
    if (start_path.parent / 'agents').exists():
        return start_path.parent
    
    return start_path

def load_application_config(mail_agent_root: Path) -> dict:
    """Load application configuration"""
    config_file = mail_agent_root / 'config' / 'connections' / 'application.json'
    
    if not config_file.exists():
        print(f"ERROR: Config not found: {config_file}")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        return json.load(f)

def get_storage_base(config: dict, mail_agent_root: Path) -> Path:
    """Get storage base path"""
    base_path = config.get('storage', {}).get('base_path', './storage')
    
    if not Path(base_path).is_absolute():
        storage_base = mail_agent_root / base_path
    else:
        storage_base = Path(base_path)
    
    return storage_base.resolve()

def find_timestamp_from_mail_id(mail_id: str, processed_dir: Path) -> str:
    """Find timestamp by searching problem.json files"""
    problem_files = list(processed_dir.glob('*_problem.json'))
    
    for problem_file in problem_files:
        try:
            with open(problem_file, 'r') as f:
                data = json.load(f)
            
            if data.get('mail_id') == mail_id:
                # Extract timestamp from filename
                filename = problem_file.stem
                # Format: YYYYMMDD_HHMMSS_problem
                parts = filename.split('_')
                if len(parts) >= 2:
                    timestamp = f"{parts[0]}_{parts[1]}"
                    return timestamp
        except Exception as e:
            print(f"Warning: Could not read {problem_file}: {e}")
            continue
    
    return None

def save_json_files(mail_id: str, problem_data: dict, solution_data: dict, asset_data: dict):
    """Save JSON files directly (no backup)"""
    # Find mail_agent root
    script_dir = Path(__file__).resolve().parent
    mail_agent_root = find_mail_agent_root(script_dir)
    
    print(f"Mail Agent Root: {mail_agent_root}")
    
    # Load config
    config = load_application_config(mail_agent_root)
    storage_base = get_storage_base(config, mail_agent_root)
    processed_dir = storage_base / 'processed'
    
    print(f"Storage Base: {storage_base}")
    print(f"Processed Dir: {processed_dir}")
    
    # Find timestamp
    timestamp = find_timestamp_from_mail_id(mail_id, processed_dir)
    
    if not timestamp:
        print(f"ERROR: Timestamp not found for mail_id: {mail_id}")
        sys.exit(1)
    
    print(f"Timestamp: {timestamp}")
    
    # File paths
    problem_file = processed_dir / f"{timestamp}_problem.json"
    solution_file = processed_dir / f"{timestamp}_solution.json"
    asset_file = processed_dir / f"{timestamp}_asset.json"
    
    # Save files directly (no backup)
    try:
        with open(problem_file, 'w', encoding='utf-8') as f:
            json.dump(problem_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {problem_file.name}")
    except Exception as e:
        print(f"ERROR: Could not save problem.json: {e}")
        sys.exit(1)
    
    # Save solution only if provided and not null
    if solution_data and solution_data != 'null':
        try:
            with open(solution_file, 'w', encoding='utf-8') as f:
                json.dump(solution_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved: {solution_file.name}")
        except Exception as e:
            print(f"Warning: Could not save solution.json: {e}")
    
    try:
        with open(asset_file, 'w', encoding='utf-8') as f:
            json.dump(asset_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved: {asset_file.name}")
    except Exception as e:
        print(f"ERROR: Could not save asset.json: {e}")
        sys.exit(1)
    
    print("✓ All files saved successfully!")

def main():
    if len(sys.argv) < 5:
        print("Usage: python save_json.py <mail_id> <problem.json> <solution.json> <asset.json>")
        sys.exit(1)
    
    mail_id = sys.argv[1]
    problem_file = Path(sys.argv[2])
    solution_file = Path(sys.argv[3])
    asset_file = Path(sys.argv[4])
    
    # Load JSON files
    try:
        with open(problem_file, 'r') as f:
            problem_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load problem.json: {e}")
        sys.exit(1)
    
    solution_data = None
    if solution_file.exists() and solution_file.stat().st_size > 0:
        try:
            with open(solution_file, 'r') as f:
                solution_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load solution.json: {e}")
    
    try:
        with open(asset_file, 'r') as f:
            asset_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load asset.json: {e}")
        sys.exit(1)
    
    # Save
    save_json_files(mail_id, problem_data, solution_data, asset_data)

if __name__ == '__main__':
    main()
