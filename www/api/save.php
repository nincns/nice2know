#!/usr/bin/env python3
"""
Nice2Know - Process Export Files
Reads edited data from export/ and updates processed/ JSONs

Usage:
  python process_exports.py
"""
import json
from pathlib import Path
from datetime import datetime

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
    return start_path.parent if (start_path.parent / 'agents').exists() else start_path

def load_application_config(mail_agent_root: Path) -> dict:
    """Load application configuration"""
    config_file = mail_agent_root / 'config' / 'connections' / 'application.json'
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

def process_export(export_file: Path, processed_dir: Path):
    """Process a single export file"""
    print(f"\nProcessing: {export_file.name}")
    
    # Load export data
    with open(export_file, 'r') as f:
        export_data = json.load(f)
    
    timestamp = export_data['timestamp']
    
    # Target files
    problem_file = processed_dir / f"{timestamp}_problem.json"
    solution_file = processed_dir / f"{timestamp}_solution.json"
    asset_file = processed_dir / f"{timestamp}_asset.json"
    
    # Update files
    with open(problem_file, 'w', encoding='utf-8') as f:
        json.dump(export_data['problem'], f, indent=2, ensure_ascii=False)
    print(f"  ✓ Updated: {problem_file.name}")
    
    if export_data.get('solution'):
        with open(solution_file, 'w', encoding='utf-8') as f:
            json.dump(export_data['solution'], f, indent=2, ensure_ascii=False)
        print(f"  ✓ Updated: {solution_file.name}")
    
    with open(asset_file, 'w', encoding='utf-8') as f:
        json.dump(export_data['asset'], f, indent=2, ensure_ascii=False)
    print(f"  ✓ Updated: {asset_file.name}")
    
    # Archive export file
    archive_dir = export_file.parent / 'archive'
    archive_dir.mkdir(exist_ok=True)
    
    archive_file = archive_dir / f"{export_file.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    export_file.rename(archive_file)
    print(f"  ✓ Archived: {archive_file.name}")

def main():
    # Setup
    script_dir = Path(__file__).resolve().parent
    mail_agent_root = find_mail_agent_root(script_dir)
    config = load_application_config(mail_agent_root)
    storage_base = get_storage_base(config, mail_agent_root)
    
    export_dir = storage_base / 'export'
    processed_dir = storage_base / 'processed'
    
    print("=" * 60)
    print("Nice2Know - Process Export Files")
    print("=" * 60)
    print(f"Export Dir:    {export_dir}")
    print(f"Processed Dir: {processed_dir}")
    
    # Find export files
    export_files = list(export_dir.glob('*_edited.json'))
    
    if not export_files:
        print("\nNo export files found.")
        return
    
    print(f"\nFound {len(export_files)} export file(s)")
    
    # Process each
    for export_file in export_files:
        try:
            process_export(export_file, processed_dir)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
