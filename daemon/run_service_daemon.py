#!/usr/bin/env python3
"""
Nice2Know Service Daemon
Main orchestrator for automated mail processing workflow

Workflow:
1. Fetch new mails (run_agent.py)
2. Classify mails (run_classifier.py)
3. Determine workflow from processing_catalog.json
4. Execute workflow steps (extract, send confirmation)
5. Move processed mails to appropriate folders

Usage:
  python run_service_daemon.py                    # Run once
  python run_service_daemon.py --daemon           # Run continuously
  python run_service_daemon.py --interval 300     # Custom interval (seconds)
"""
import sys
import time
import json
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import argparse

# Auto-detect project root
def find_project_root(start_path: Path) -> Path:
    """
    Find project root by looking for mail_agent/ subdirectory
    Supports both daemon/ and mail_agent/ as script location
    """
    current = start_path
    
    # Try up to 5 levels up
    for _ in range(5):
        # Check if we're in mail_agent/ (has agents/, catalog/, config/)
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'config').exists():
            return current
        
        # Check if mail_agent/ is a sibling or child directory
        if (current / 'mail_agent').exists():
            mail_agent = current / 'mail_agent'
            if (mail_agent / 'agents').exists():
                return mail_agent
        
        # Go up one level
        if current.parent != current:
            current = current.parent
        else:
            break
    
    # Fallback: assume mail_agent is sibling
    if start_path.parent != start_path:
        sibling = start_path.parent / 'mail_agent'
        if sibling.exists():
            return sibling
    
    return start_path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKING_DIR = find_project_root(SCRIPT_DIR)
sys.path.insert(0, str(WORKING_DIR))

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
BOLD = '\033[1m'
NC = '\033[0m'

class Nice2KnowService:
    """Main service daemon for Nice2Know mail processing"""
    
    def __init__(self, interval: int = 60, dry_run: bool = False):
        self.interval = interval
        self.dry_run = dry_run
        self.running = True
        self.cycle_count = 0
        
        # Load configurations
        self.app_config = self._load_application_config()
        self.processing_catalog = self._load_processing_catalog()
        
        # Get storage paths
        self.storage_base = self._get_storage_base()
        self.mail_dir = self.storage_base / 'mails'
        self.classified_dir = self.storage_base / 'classified'
        self.processed_dir = self.storage_base / 'processed'
        self.failed_dir = self.storage_base / 'failed'
        self.sent_dir = self.storage_base / 'sent'
        
        # Ensure directories exist
        for directory in [self.mail_dir, self.classified_dir, self.processed_dir,
                         self.failed_dir, self.sent_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._log_startup()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
        print(f"\n{YELLOW}Received {signal_name}, shutting down gracefully...{NC}")
        self.running = False
    
    def _load_application_config(self) -> Dict:
        """Load application configuration"""
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
    
    def _load_processing_catalog(self) -> Dict:
        """Load processing catalog with workflow definitions"""
        catalog_file = WORKING_DIR / 'catalog' / 'processing_catalog.json'
        
        if not catalog_file.exists():
            print(f"{RED}Error: processing_catalog.json not found at {catalog_file}{NC}")
            sys.exit(1)
        
        try:
            with open(catalog_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{RED}Error loading processing catalog: {e}{NC}")
            sys.exit(1)
    
    def _get_storage_base(self) -> Path:
        """Get absolute storage base path from config"""
        base_path = self.app_config.get('storage', {}).get('base_path', './storage')
        
        if not Path(base_path).is_absolute():
            storage_base = WORKING_DIR / base_path
        else:
            storage_base = Path(base_path)
        
        return storage_base.resolve()
    
    def _log_startup(self):
        """Log startup information"""
        print(f"\n{BLUE}{'=' * 70}{NC}")
        print(f"{BLUE}{BOLD}Nice2Know Service Daemon{NC}")
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"Script Location:  {SCRIPT_DIR}")
        print(f"Working Dir:      {WORKING_DIR}")
        print(f"Config Dir:       {WORKING_DIR / 'config' / 'connections'}")
        print(f"Catalog Dir:      {WORKING_DIR / 'catalog'}")
        print(f"Storage Base:     {self.storage_base}")
        print(f"Interval:         {self.interval}s")
        print(f"Dry Run:          {self.dry_run}")
        print(f"Catalog Version:  {self.processing_catalog.get('catalog_version', 'unknown')}")
        print(f"Started:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{BLUE}{'=' * 70}{NC}\n")
    
    def _run_script(self, script_name: str, args: List[str] = None, timeout: int = 600) -> bool:
        """
        Execute a Python script
        
        Args:
            script_name: Script filename (e.g., 'run_agent.py')
            args: Optional command-line arguments
            timeout: Timeout in seconds
        
        Returns:
            True if successful, False otherwise
        """
        script_path = WORKING_DIR / script_name
        
        if not script_path.exists():
            print(f"{RED}✗ Script not found: {script_path}{NC}")
            return False
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            print(f"  Executing: {script_name} {' '.join(args or [])}", end=' ... ', flush=True)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(WORKING_DIR)
            )
            
            if result.returncode == 0:
                print(f"{GREEN}✓{NC}")
                return True
            else:
                print(f"{RED}✗{NC}")
                if result.stderr:
                    print(f"    {RED}Error: {result.stderr[:200]}{NC}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{RED}✗ TIMEOUT{NC}")
            return False
        except Exception as e:
            print(f"{RED}✗ {e}{NC}")
            return False
    
    def fetch_mails(self) -> int:
        """
        Fetch new mails using run_agent.py
        
        Returns:
            Number of mails in mail directory after fetch
        """
        print(f"\n{CYAN}[STEP 1] Fetching new mails...{NC}")
        
        if self.dry_run:
            print(f"  {YELLOW}[DRY RUN] Skipping mail fetch{NC}")
            return len(list(self.mail_dir.glob('*.eml')))
        
        # Run mail agent
        success = self._run_script('run_agent.py')
        
        # Count mails in directory
        mail_count = len(list(self.mail_dir.glob('*.eml')))
        print(f"  {CYAN}→ {mail_count} mail(s) in queue{NC}")
        
        return mail_count
    
    def classify_mails(self) -> List[Dict]:
        """
        Classify unprocessed mails using run_classifier.py
        
        Returns:
            List of classification data for successfully classified mails
        """
        print(f"\n{CYAN}[STEP 2] Classifying mails...{NC}")
        
        # Get unclassified mails
        mail_files = list(self.mail_dir.glob('*.eml'))
        classified_files = list(self.classified_dir.glob('*_identifier.json'))
        
        # Filter out already classified
        unclassified = []
        for mail_file in mail_files:
            mail_parts = mail_file.stem.split('_')
            if len(mail_parts) >= 2:
                mail_timestamp = f"{mail_parts[0]}_{mail_parts[1]}"
            else:
                mail_timestamp = mail_file.stem
            
            classification_file = self.classified_dir / f"{mail_timestamp}_identifier.json"
            if not classification_file.exists():
                unclassified.append(mail_file)
        
        if not unclassified:
            print(f"  {YELLOW}No unclassified mails found{NC}")
            return []
        
        print(f"  {CYAN}Found {len(unclassified)} unclassified mail(s){NC}")
        
        if self.dry_run:
            print(f"  {YELLOW}[DRY RUN] Skipping classification{NC}")
            return []
        
        # Run classifier
        success = self._run_script('run_classifier.py')
        
        if not success:
            print(f"  {RED}Classification failed{NC}")
            return []
        
        # Load all classification JSONs
        classifications = []
        for json_file in self.classified_dir.glob('*_identifier.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_json_path'] = json_file
                    classifications.append(data)
            except Exception as e:
                print(f"  {RED}Failed to load {json_file.name}: {e}{NC}")
        
        print(f"  {GREEN}→ {len(classifications)} classification(s) available{NC}")
        return classifications
    
    def match_workflow(self, classification: Dict) -> Optional[Dict]:
        """
        Match classification to workflow rule
        
        Args:
            classification: Classification data from identifier JSON
        
        Returns:
            Workflow rule dict or None if no match
        """
        content = classification.get('content_analysis', {})
        mail_class = classification.get('mail_classification', {})
        
        for rule_name, rule in self.processing_catalog['workflow_rules'].items():
            conditions = rule['conditions']
            
            # Check all conditions
            match = True
            for key, value in conditions.items():
                if key == 'classification_type':
                    if isinstance(value, list):
                        if mail_class.get('type') not in value:
                            match = False
                            break
                    elif mail_class.get('type') != value:
                        match = False
                        break
                elif key in content:
                    if content[key] != value:
                        match = False
                        break
            
            if match:
                return {
                    'name': rule_name,
                    'rule': rule
                }
        
        return None
    
    def execute_workflow(self, classification: Dict, workflow: Dict) -> bool:
        """
        Execute workflow processing sequence
        
        Args:
            classification: Classification data
            workflow: Matched workflow rule
        
        Returns:
            True if all steps successful, False otherwise
        """
        rule_name = workflow['name']
        rule = workflow['rule']
        sequence = rule['processing_sequence']
        
        print(f"\n{MAGENTA}[WORKFLOW] {rule_name}{NC}")
        print(f"  {MAGENTA}Sequence: {' → '.join(sequence)}{NC}")
        
        # Extract timestamp and mail_id from classification
        json_path = classification.get('_json_path')
        if not json_path:
            print(f"  {RED}No JSON path found in classification{NC}")
            return False
        
        timestamp = '_'.join(json_path.stem.split('_')[:2])
        mail_id = classification.get('mail_id', 'N/A')
        
        # Find corresponding .eml file
        mail_files = list(self.mail_dir.glob(f"{timestamp}_*.eml"))
        if not mail_files:
            print(f"  {YELLOW}No mail file found for {timestamp}{NC}")
            return False
        
        mail_file = mail_files[0]
        
        # Execute each step in sequence
        for step_name in sequence:
            if step_name not in self.processing_catalog['processing_types']:
                print(f"  {RED}Unknown processing type: {step_name}{NC}")
                return False
            
            processor = self.processing_catalog['processing_types'][step_name]
            
            # Check if enabled
            if not processor.get('enabled', True):
                print(f"  {YELLOW}Skipping disabled step: {step_name}{NC}")
                continue
            
            # Execute processor
            success = self._execute_processor(processor, mail_file, timestamp)
            
            if not success:
                print(f"  {RED}Step '{step_name}' failed{NC}")
                self._handle_failure(mail_file)
                return False
        
        # All steps successful - move to sent
        self._move_to_sent(mail_file)
        
        return True
    
    def _execute_processor(self, processor: Dict, mail_file: Path, timestamp: str) -> bool:
        """
        Execute a single processor step
        
        Args:
            processor: Processor configuration from catalog
            mail_file: Path to .eml file
            timestamp: Mail timestamp
        
        Returns:
            True if successful, False otherwise
        """
        proc_name = processor.get('name', processor['id'])
        print(f"\n  {CYAN}[{proc_name}]{NC}")
        
        if self.dry_run:
            print(f"    {YELLOW}[DRY RUN] Would execute: {processor.get('script', 'N/A')}{NC}")
            return True
        
        # Special handling for different processor types
        if processor['id'] == 'problem_extraction':
            return self._extract_json(mail_file, 'problem', timestamp, processor)
        
        elif processor['id'] == 'solution_extraction':
            return self._extract_json(mail_file, 'solution', timestamp, processor)
        
        elif processor['id'] == 'asset_extraction':
            return self._extract_json(mail_file, 'asset', timestamp, processor)
        
        elif processor['id'] == 'confirmation_mail':
            return self._send_confirmation(timestamp)
        
        elif processor['id'] == 'auto_archive':
            return self._auto_archive(mail_file)
        
        else:
            print(f"    {YELLOW}Processor type not implemented: {processor['id']}{NC}")
            return False
    
    def _extract_json(self, mail_file: Path, json_type: str, timestamp: str, processor: Dict) -> bool:
        """Extract JSON using run_extract_all.py logic"""
        # Check if JSON already exists
        output_path = self.processed_dir / f"{timestamp}_{json_type}.json"
        if output_path.exists():
            print(f"    {GREEN}✓ Already exists: {output_path.name}{NC}")
            return True
        
        # Use run_extract_all.py for extraction
        # For simplicity, we call it with --latest flag
        args = ['--latest']
        success = self._run_script('run_extract_all.py', args, timeout=processor.get('timeout', 300))
        
        # Check if output was created
        if output_path.exists():
            print(f"    {GREEN}✓ Created: {output_path.name}{NC}")
            return True
        else:
            print(f"    {RED}✗ Output not found: {output_path.name}{NC}")
            return False
    
    def _send_confirmation(self, timestamp: str) -> bool:
        """Send confirmation mail using run_send_response.py"""
        # Check prerequisites: problem, solution, asset JSONs must exist
        required_jsons = ['problem', 'solution', 'asset']
        
        for json_type in required_jsons:
            json_path = self.processed_dir / f"{timestamp}_{json_type}.json"
            if not json_path.exists():
                print(f"    {RED}✗ Missing prerequisite: {json_path.name}{NC}")
                return False
        
        # Run confirmation mail script
        success = self._run_script('run_send_response.py', timeout=120)
        
        return success
    
    def _auto_archive(self, mail_file: Path) -> bool:
        """Move mail to archive without processing"""
        archive_dir = self.storage_base / 'archived'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            dest = archive_dir / mail_file.name
            mail_file.rename(dest)
            print(f"    {GREEN}✓ Archived: {mail_file.name}{NC}")
            return True
        except Exception as e:
            print(f"    {RED}✗ Failed to archive: {e}{NC}")
            return False
    
    def _move_to_sent(self, mail_file: Path):
        """Move processed mail to sent directory"""
        try:
            dest = self.sent_dir / mail_file.name
            if mail_file.exists():
                mail_file.rename(dest)
                print(f"  {GREEN}→ Moved to sent: {mail_file.name}{NC}")
        except Exception as e:
            print(f"  {YELLOW}Could not move to sent: {e}{NC}")
    
    def _handle_failure(self, mail_file: Path):
        """Move failed mail to failed directory"""
        try:
            dest = self.failed_dir / mail_file.name
            if mail_file.exists():
                mail_file.rename(dest)
                print(f"  {RED}→ Moved to failed: {mail_file.name}{NC}")
        except Exception as e:
            print(f"  {RED}Could not move to failed: {e}{NC}")
    
    def process_cycle(self) -> Dict[str, int]:
        """
        Execute one complete processing cycle
        
        Returns:
            Statistics dict with counts
        """
        self.cycle_count += 1
        
        print(f"\n{BLUE}{BOLD}{'=' * 70}{NC}")
        print(f"{BLUE}{BOLD}Processing Cycle #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{NC}")
        print(f"{BLUE}{BOLD}{'=' * 70}{NC}")
        
        stats = {
            'mails_fetched': 0,
            'mails_classified': 0,
            'workflows_executed': 0,
            'workflows_successful': 0,
            'workflows_failed': 0
        }
        
        # Step 1: Fetch mails
        stats['mails_fetched'] = self.fetch_mails()
        
        # Step 2: Classify mails
        classifications = self.classify_mails()
        stats['mails_classified'] = len(classifications)
        
        if not classifications:
            print(f"\n{YELLOW}No classifications to process{NC}")
            return stats
        
        # Step 3: Process each classification
        print(f"\n{CYAN}[STEP 3] Processing workflows...{NC}")
        
        for classification in classifications:
            # Match to workflow
            workflow = self.match_workflow(classification)
            
            if not workflow:
                print(f"\n{YELLOW}No workflow matched for classification{NC}")
                continue
            
            stats['workflows_executed'] += 1
            
            # Execute workflow
            success = self.execute_workflow(classification, workflow)
            
            if success:
                stats['workflows_successful'] += 1
            else:
                stats['workflows_failed'] += 1
        
        # Print summary
        self._print_cycle_summary(stats)
        
        return stats
    
    def _print_cycle_summary(self, stats: Dict[str, int]):
        """Print cycle statistics"""
        print(f"\n{BLUE}{'=' * 70}{NC}")
        print(f"{BLUE}{BOLD}Cycle #{self.cycle_count} Summary{NC}")
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"Mails Fetched:        {stats['mails_fetched']}")
        print(f"Mails Classified:     {stats['mails_classified']}")
        print(f"Workflows Executed:   {stats['workflows_executed']}")
        print(f"  {GREEN}Successful:         {stats['workflows_successful']}{NC}")
        print(f"  {RED}Failed:             {stats['workflows_failed']}{NC}")
        print(f"{BLUE}{'=' * 70}{NC}\n")
    
    def run_once(self):
        """Run one processing cycle and exit"""
        self.process_cycle()
        print(f"{GREEN}✓ Single cycle completed{NC}\n")
    
    def run_daemon(self):
        """Run continuously in daemon mode"""
        print(f"{GREEN}Starting daemon mode (press Ctrl+C to stop)...{NC}\n")
        
        while self.running:
            try:
                self.process_cycle()
                
                if self.running:
                    print(f"{CYAN}Waiting {self.interval} seconds before next cycle...{NC}\n")
                    time.sleep(self.interval)
                    
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Keyboard interrupt received{NC}")
                self.running = False
                break
            except Exception as e:
                print(f"\n{RED}Error in processing cycle: {e}{NC}")
                import traceback
                traceback.print_exc()
                
                if self.running:
                    print(f"{YELLOW}Waiting {self.interval} seconds before retry...{NC}\n")
                    time.sleep(self.interval)
        
        print(f"\n{GREEN}Service daemon stopped gracefully{NC}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Nice2Know Service Daemon - Automated Mail Processing'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run continuously in daemon mode'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Processing interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode - show what would be done without executing'
    )
    
    args = parser.parse_args()
    
    try:
        service = Nice2KnowService(
            interval=args.interval,
            dry_run=args.dry_run
        )
        
        if args.daemon:
            service.run_daemon()
        else:
            service.run_once()
        
        return 0
        
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{NC}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
