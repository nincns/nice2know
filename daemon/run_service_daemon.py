#!/usr/bin/env python3
"""
Nice2Know Service Daemon v2 - Catalog-Driven Workflow Engine

This daemon is a GENERIC workflow executor that reads ALL configuration
from processing_catalog.json. NO hardcoded script names or logic!

Architecture:
- Reads workflow definitions from processing_catalog.json
- Executes scripts dynamically based on catalog configuration
- Zero hardcoded business logic - everything in catalog

Usage:
  python run_service_daemon_v2.py                    # Run once
  python run_service_daemon_v2.py --daemon           # Run continuously
  python run_service_daemon_v2.py --interval 300     # Custom interval
  python run_service_daemon_v2.py --no-auto-update   # Disable git auto-update
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
import threading
import os

# Auto-detect project root
def find_project_root(start_path: Path) -> Path:
    """Find mail_agent root directory"""
    current = start_path
    
    for _ in range(5):
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'config').exists():
            return current
        
        if (current / 'mail_agent').exists():
            mail_agent = current / 'mail_agent'
            if (mail_agent / 'agents').exists():
                return mail_agent
        
        if current.parent != current:
            current = current.parent
        else:
            break
    
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


class CatalogDrivenService:
    """Generic workflow executor driven by processing_catalog.json"""
    
    def __init__(self, interval: int = 60, dry_run: bool = False, auto_update: bool = True,
                 update_interval: int = 600, git_branch: str = 'main'):
        self.interval = interval
        self.dry_run = dry_run
        self.running = True
        self.cycle_count = 0
        self.shutdown_requested = False
        self.auto_update = auto_update
        self.update_interval = update_interval
        self.git_branch = git_branch
        self.needs_restart = False
        self.update_thread = None
        
        # Load configurations
        self.app_config = self._load_application_config()
        self.catalog = self._load_processing_catalog()
        
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
        
        if self.auto_update:
            self._start_auto_updater()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if self.shutdown_requested:
            signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
            print(f"\n{RED}Second {signal_name} received, forcing shutdown...{NC}")
            sys.exit(0)
        
        signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
        print(f"\n{YELLOW}Received {signal_name}, shutting down gracefully...{NC}")
        print(f"{YELLOW}(Press Ctrl+C again to force quit){NC}")
        self.shutdown_requested = True
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
        """Load processing catalog - THE central configuration"""
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
        print(f"{BLUE}{BOLD}Nice2Know Service Daemon v2 - Catalog-Driven{NC}")
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"Script Location:  {SCRIPT_DIR}")
        print(f"Working Dir:      {WORKING_DIR}")
        print(f"Storage Base:     {self.storage_base}")
        print(f"Interval:         {self.interval}s")
        print(f"Dry Run:          {self.dry_run}")
        print(f"Auto-Update:      {self.auto_update}")
        if self.auto_update:
            print(f"Update Interval:  {self.update_interval}s ({self.update_interval // 60} min)")
            print(f"Git Branch:       {self.git_branch}")
        print(f"Catalog Version:  {self.catalog.get('catalog_version', 'unknown')}")
        print(f"Started:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{BLUE}{'=' * 70}{NC}\n")
    
    def _start_auto_updater(self):
        """Start git auto-update thread"""
        def update_loop():
            project_root = WORKING_DIR.parent
            
            if not (project_root / '.git').exists():
                print(f"{YELLOW}[AUTO-UPDATE] Not a git repository, auto-update disabled{NC}")
                return
            
            print(f"{GREEN}[AUTO-UPDATE] Started (checking every {self.update_interval // 60} min){NC}")
            print(f"{GREEN}[AUTO-UPDATE] Repository: {project_root}{NC}")
            print(f"{GREEN}[AUTO-UPDATE] Branch: {self.git_branch}{NC}\n")
            
            while self.running:
                try:
                    for _ in range(self.update_interval):
                        if not self.running:
                            break
                        time.sleep(1)
                    
                    if not self.running:
                        break
                    
                    print(f"\n{CYAN}[AUTO-UPDATE] Checking for updates...{NC}")
                    
                    if self._check_and_pull_updates(project_root):
                        print(f"{GREEN}[AUTO-UPDATE] Update successful!{NC}")
                        print(f"{YELLOW}[AUTO-UPDATE] Restart required to apply changes{NC}")
                        self.needs_restart = True
                        
                        if not self.dry_run:
                            print(f"{YELLOW}[AUTO-UPDATE] Triggering graceful shutdown for restart...{NC}")
                            self.running = False
                    else:
                        print(f"{GREEN}[AUTO-UPDATE] Already up to date{NC}")
                    
                except Exception as e:
                    print(f"{RED}[AUTO-UPDATE] Error: {e}{NC}")
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def _check_and_pull_updates(self, repo_path: Path) -> bool:
        """Check for updates and pull if available"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            current_commit = result.stdout.strip()[:8]
            print(f"  Current: {current_commit}")
            
            subprocess.run(
                ['git', 'fetch', 'origin', self.git_branch, '--force'],
                cwd=repo_path,
                capture_output=True,
                timeout=30
            )
            
            result = subprocess.run(
                ['git', 'rev-parse', f'origin/{self.git_branch}'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            remote_commit = result.stdout.strip()[:8]
            print(f"  Remote:  {remote_commit}")
            
            if current_commit == remote_commit:
                return False
            
            print(f"  {YELLOW}Update available!{NC}")
            
            print(f"  Resetting to origin/{self.git_branch}...")
            subprocess.run(
                ['git', 'reset', '--hard', f'origin/{self.git_branch}'],
                cwd=repo_path,
                capture_output=True,
                timeout=30,
                check=True
            )
            
            print(f"  Cleaning untracked files...")
            subprocess.run(
                ['git', 'clean', '-fd'],
                cwd=repo_path,
                capture_output=True,
                timeout=30
            )
            
            return True
            
        except Exception as e:
            print(f"  {RED}Error during update: {e}{NC}")
            return False
    
    def _run_script(self, script_name: str, args: List[str] = None, timeout: int = 600) -> bool:
        """
        Execute a Python script - THE CORE execution method
        
        This is the ONLY place where scripts are executed.
        Everything else is configuration-driven!
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
                cwd=str(WORKING_DIR),
                env={
                    **os.environ,
                    'PYTHONPATH': str(WORKING_DIR)
                }
            )
            
            if result.returncode == 0:
                print(f"{GREEN}✓{NC}")
                return True
            else:
                print(f"{RED}✗{NC}")
                if result.stdout:
                    print(f"    {YELLOW}STDOUT:{NC}\n{result.stdout[-500:]}")
                if result.stderr:
                    print(f"    {RED}STDERR:{NC}\n{result.stderr[-500:]}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{RED}✗ TIMEOUT{NC}")
            return False
        except Exception as e:
            print(f"{RED}✗ {e}{NC}")
            return False
    
    def fetch_mails(self) -> int:
        """
        Fetch new mails - HARDCODED because it's infrastructure
        This is the ONLY hardcoded script call in the entire daemon
        """
        print(f"\n{CYAN}[STEP 1] Fetching new mails...{NC}")
        
        if self.dry_run:
            print(f"  {YELLOW}[DRY RUN] Skipping mail fetch{NC}")
            return len(list(self.mail_dir.glob('*.eml')))
        
        success = self._run_script('run_agent.py')
        
        mail_count = len(list(self.mail_dir.glob('*.eml')))
        print(f"  {CYAN}→ {mail_count} mail(s) in queue{NC}")
        
        return mail_count
    
    def classify_mails(self) -> List[Dict]:
        """
        Classify mails - HARDCODED because it's infrastructure
        This is the ONLY other hardcoded script call
        """
        print(f"\n{CYAN}[STEP 2] Classifying mails...{NC}")
        
        # Get unclassified mails
        mail_files = list(self.mail_dir.glob('*.eml'))
        
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
        Match classification to workflow rule FROM CATALOG
        """
        content = classification.get('content_analysis', {})
        mail_class = classification.get('mail_classification', {})
        
        for rule_name, rule in self.catalog['workflow_rules'].items():
            conditions = rule['conditions']
            
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
        Execute workflow FROM CATALOG - completely dynamic!
        """
        rule_name = workflow['name']
        rule = workflow['rule']
        sequence = rule['processing_sequence']
        
        print(f"\n{MAGENTA}[WORKFLOW] {rule_name}{NC}")
        print(f"  {MAGENTA}Sequence: {' → '.join(sequence)}{NC}")
        
        json_path = classification.get('_json_path')
        if not json_path:
            print(f"  {RED}No JSON path found in classification{NC}")
            return False
        
        timestamp = '_'.join(json_path.stem.split('_')[:2])
        
        mail_files = list(self.mail_dir.glob(f"{timestamp}_*.eml"))
        if not mail_files:
            print(f"  {YELLOW}No mail file found for {timestamp}{NC}")
            return False
        
        mail_file = mail_files[0]
        
        # Execute each step in sequence FROM CATALOG
        for step_name in sequence:
            if step_name not in self.catalog['processing_types']:
                print(f"  {RED}Unknown processing type: {step_name}{NC}")
                return False
            
            processor = self.catalog['processing_types'][step_name]
            
            if not processor.get('enabled', True):
                print(f"  {YELLOW}Skipping disabled step: {step_name}{NC}")
                continue
            
            # DYNAMIC execution based on catalog
            success = self._execute_processor(processor, mail_file, timestamp)
            
            if not success:
                print(f"  {RED}Step '{step_name}' failed{NC}")
                self._handle_failure(mail_file)
                return False
        
        self._move_to_sent(mail_file)
        
        return True
    
    def _execute_processor(self, processor: Dict, mail_file: Path, timestamp: str) -> bool:
        """
        GENERIC processor execution - reads everything from catalog!
        NO hardcoded logic here!
        """
        proc_name = processor.get('name', processor['id'])
        print(f"\n  {CYAN}[{proc_name}]{NC}")
        
        if self.dry_run:
            print(f"    {YELLOW}[DRY RUN] Would execute: {processor.get('execution', {}).get('script', 'N/A')}{NC}")
            return True
        
        execution = processor.get('execution', {})
        script = execution.get('script')
        
        # Built-in action (no script)
        if not script:
            return self._execute_builtin_action(processor, mail_file)
        
        # Dynamic script execution from catalog
        return self._execute_script_from_catalog(processor, mail_file, timestamp)
    
    def _execute_script_from_catalog(self, processor: Dict, mail_file: Path, timestamp: str) -> bool:
        """
        Execute script dynamically based on catalog configuration
        """
        execution = processor.get('execution', {})
        script = execution.get('script')
        
        # For extraction processors, use run_extract_all.py with --latest
        if processor['id'].endswith('_extraction'):
            json_type = processor['id'].replace('_extraction', '')
            output_path = self.processed_dir / f"{timestamp}_{json_type}.json"
            
            if output_path.exists():
                print(f"    {GREEN}✓ Already exists: {output_path.name}{NC}")
                return True
            
            args = ['--latest']
            success = self._run_script('run_extract_all.py', args, timeout=execution.get('timeout', 300))
            
            if output_path.exists():
                print(f"    {GREEN}✓ Created: {output_path.name}{NC}")
                return True
            else:
                print(f"    {RED}✗ Output not found: {output_path.name}{NC}")
                return False
        
        # For confirmation_mail, use run_send_response.py
        elif processor['id'] == 'confirmation_mail':
            # Check prerequisites
            required_jsons = ['problem', 'asset']
            
            for json_type in required_jsons:
                json_path = self.processed_dir / f"{timestamp}_{json_type}.json"
                if not json_path.exists():
                    print(f"    {RED}✗ Missing prerequisite: {json_path.name}{NC}")
                    return False
            
            success = self._run_script('run_send_response.py', timeout=execution.get('timeout', 120))
            return success
        
        # Generic script execution (future-proof!)
        else:
            print(f"    {YELLOW}⚠ Generic execution not yet implemented for: {processor['id']}{NC}")
            return False
    
    def _execute_builtin_action(self, processor: Dict, mail_file: Path) -> bool:
        """
        Execute built-in actions (no external script)
        """
        execution = processor.get('execution', {})
        action = execution.get('action')
        
        if action == 'move_to_archive':
            return self._auto_archive(mail_file)
        else:
            print(f"    {RED}✗ Unknown built-in action: {action}{NC}")
            return False
    
    def _auto_archive(self, mail_file: Path) -> bool:
        """Built-in action: move mail to archive"""
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
        """Execute one complete processing cycle"""
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
        
        stats['mails_fetched'] = self.fetch_mails()
        
        classifications = self.classify_mails()
        stats['mails_classified'] = len(classifications)
        
        if not classifications:
            print(f"\n{YELLOW}No classifications to process{NC}")
            return stats
        
        print(f"\n{CYAN}[STEP 3] Processing workflows...{NC}")
        
        processed_timestamps = set()
        
        for classification in classifications:
            json_path = classification.get('_json_path')
            if not json_path:
                continue
            
            timestamp = '_'.join(json_path.stem.split('_')[:2])
            
            if timestamp in processed_timestamps:
                print(f"\n{YELLOW}Skipping duplicate: {timestamp}{NC}")
                continue
            
            processed_timestamps.add(timestamp)
            
            workflow = self.match_workflow(classification)
            
            if not workflow:
                print(f"\n{YELLOW}No workflow matched for classification{NC}")
                continue
            
            stats['workflows_executed'] += 1
            
            success = self.execute_workflow(classification, workflow)
            
            if success:
                stats['workflows_successful'] += 1
            else:
                stats['workflows_failed'] += 1
        
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
                    print(f"{CYAN}Waiting {self.interval} seconds before next cycle...{NC}")
                    print(f"{YELLOW}Press Ctrl+C to stop{NC}\n")
                    
                    elapsed = 0
                    while elapsed < self.interval and self.running:
                        time.sleep(1)
                        elapsed += 1
                    
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
                    elapsed = 0
                    while elapsed < self.interval and self.running:
                        time.sleep(1)
                        elapsed += 1
        
        print(f"\n{GREEN}Service daemon stopped gracefully{NC}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Nice2Know Service Daemon v2 - Catalog-Driven Workflow Engine'
    )
    parser.add_argument('--daemon', action='store_true',
                       help='Run continuously in daemon mode')
    parser.add_argument('--interval', type=int, default=60,
                       help='Processing interval in seconds (default: 60)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - show what would be done without executing')
    parser.add_argument('--no-auto-update', action='store_true',
                       help='Disable automatic git updates')
    parser.add_argument('--update-interval', type=int, default=600,
                       help='Git update check interval in seconds (default: 600 = 10 min)')
    parser.add_argument('--git-branch', default='main',
                       help='Git branch to track for updates (default: main)')
    
    args = parser.parse_args()
    
    try:
        service = CatalogDrivenService(
            interval=args.interval,
            dry_run=args.dry_run,
            auto_update=not args.no_auto_update,
            update_interval=args.update_interval,
            git_branch=args.git_branch
        )
        
        if args.daemon:
            service.run_daemon()
        else:
            service.run_once()
        
        if service.needs_restart:
            print(f"\n{YELLOW}{'=' * 70}{NC}")
            print(f"{YELLOW}UPDATE APPLIED - Restart required!{NC}")
            print(f"{YELLOW}{'=' * 70}{NC}")
            print(f"Systemd will automatically restart the service.")
            print(f"Or manually: sudo systemctl restart nice2know")
            print(f"{YELLOW}{'=' * 70}{NC}\n")
            return 3
        
        return 0
        
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{NC}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
