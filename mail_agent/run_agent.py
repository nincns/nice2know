#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Main Runner
"""
import json
import sys
import argparse
import time
from pathlib import Path
from agents.imap_fetcher import IMAPFetcher
from agents.mail_parser import MailParser
from agents.attachment_handler import AttachmentHandler
from utils.logger import get_logger
from utils.file_handler import FileHandler

logger = get_logger()

def find_mail_agent_root(start_path: Path) -> Path:
    """Find mail_agent root directory"""
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

def load_config(config_path: str = None) -> dict:
    """Load mail agent configuration"""
    script_dir = Path(__file__).resolve().parent
    mail_agent_root = find_mail_agent_root(script_dir)
    config_dir = mail_agent_root / 'config' / 'connections'
    
    # Load mail connection config
    if not config_path:
        mail_config_path = config_dir / 'mail_config.json'
    else:
        mail_config_path = Path(config_path)
    
    if not mail_config_path.exists():
        logger.error(f"Mail config not found: {mail_config_path}")
        sys.exit(1)
    
    with open(mail_config_path, 'r', encoding='utf-8') as f:
        mail_config = json.load(f)
    
    # Load application config for storage/logging/processing settings
    app_config_path = config_dir / 'application.json'
    
    if not app_config_path.exists():
        logger.error(f"Application config not found: {app_config_path}")
        sys.exit(1)
    
    with open(app_config_path, 'r', encoding='utf-8') as f:
        app_config = json.load(f)
    
    # Resolve storage base_path (handle relative paths)
    storage_base_path = app_config.get('storage', {}).get('base_path', './storage')
    
    if not Path(storage_base_path).is_absolute():
        # Relative path - resolve from mail_agent_root
        storage_base_path = str(mail_agent_root / storage_base_path)
    
    # Merge configs: mail connection settings + application settings
    config = {
        'imap': mail_config.get('imap', {}),
        'smtp': mail_config.get('smtp', {}),
        'storage': {
            'base_path': storage_base_path,
            'max_attachment_size_mb': app_config.get('storage', {}).get('max_attachment_size_mb', 50)
        },
        'logging': app_config.get('logging', {}),
        'app_name': app_config.get('app_name', 'Nice2Know'),
        'version': app_config.get('version', '1.0.0'),
        # Add default processing/filters if not in app_config
        'processing': {
            'fetch_limit': 10,
            'fetch_unseen_only': True,
            'save_raw_eml': True,
            'extract_attachments': True
        },
        'filters': app_config.get('filters', {
            'mark_as_read': False,
            'move_to_processed': True,
            'processed_folder': 'processed'
        })
    }
    
    # Store root path for reference
    config['_mail_agent_root'] = str(mail_agent_root)
    
    return config

def run_agent(config: dict, dry_run: bool = False):
    """Main agent execution"""
    logger.info("=" * 60)
    logger.info(f"{config.get('app_name', 'Nice2Know')} Mail Agent - Starting")
    logger.info(f"Version: {config.get('version', '1.0.0')}")
    logger.info("=" * 60)
    logger.info(f"Storage path: {config['storage']['base_path']}")
    logger.info(f"Dry run mode: {dry_run}")
    logger.info("=" * 60)
    
    # Initialize components
    file_handler = FileHandler(config['storage']['base_path'])
    fetcher = IMAPFetcher(config)
    parser = MailParser()
    att_handler = AttachmentHandler(
        file_handler,
        config['storage']['max_attachment_size_mb']
    )
    
    # Connect to mail server
    if not fetcher.connect():
        logger.error("Failed to connect to mail server. Exiting.")
        return 1
    
    if not fetcher.select_mailbox():
        logger.error("Failed to select mailbox. Exiting.")
        fetcher.disconnect()
        return 1
    
    # Fetch messages
    messages = fetcher.fetch_messages(
        limit=config['processing']['fetch_limit'],
        unseen_only=config['processing']['fetch_unseen_only']
    )
    
    if not messages:
        logger.info("No messages to process")
        fetcher.disconnect()
        return 0
    
    # Process each message
    processed_count = 0
    target_folder = config['filters'].get('processed_folder', 'processed')
    folder_ensured = False
    
    for msg_id, raw_email in messages:
        logger.info(f"\n--- Processing message {msg_id} ---")
        
        try:
            # Parse email
            parsed = parser.parse(raw_email)
            if not parsed:
                logger.error(f"Failed to parse message {msg_id}")
                continue
            
            # Save raw EML if configured
            if config['processing']['save_raw_eml'] and not dry_run:
                file_handler.save_mail(
                    parsed['message_id'],
                    raw_email
                )
            
            # Extract attachments
            if config['processing']['extract_attachments'] and parsed['attachments']:
                if not dry_run:
                    saved_attachments = att_handler.extract_attachments(parsed['attachments'])
                    logger.info(f"Saved {len(saved_attachments)} attachment(s)")
                else:
                    logger.info(f"[DRY RUN] Would extract {len(parsed['attachments'])} attachment(s)")
            
            # Mark as read if configured
            if config['filters']['mark_as_read'] and not dry_run:
                fetcher.mark_as_read(msg_id)
            
            # Move to processed folder if configured
            if config['filters'].get('move_to_processed', False) and not dry_run:
                # Ensure folder exists (only once)
                if not folder_ensured:
                    fetcher._ensure_folder(target_folder)
                    folder_ensured = True
                fetcher.move_to_folder(msg_id, target_folder)
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {e}", exc_info=True)
    
    # Cleanup
    fetcher.disconnect()
    
    logger.info("=" * 60)
    logger.info(f"Processing complete. Processed {processed_count} message(s)")
    logger.info("=" * 60)
    
    return 0

def main():
    parser = argparse.ArgumentParser(description='Nice2Know Mail Agent')
    parser.add_argument('--config', help='Path to mail config JSON file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode - fetch but do not save or modify')
    parser.add_argument('--loop', action='store_true',
                       help='Run continuously in loop mode')
    parser.add_argument('--interval', type=int, default=60,
                       help='Loop interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        
        if args.loop:
            logger.info(f"Starting loop mode (interval: {args.interval}s)")
            logger.info("Press Ctrl+C to stop")
            
            while True:
                try:
                    run_agent(config, args.dry_run)
                    logger.info(f"Waiting {args.interval} seconds before next run...")
                    time.sleep(args.interval)
                except KeyboardInterrupt:
                    logger.info("\nLoop interrupted by user")
                    break
        else:
            return run_agent(config, args.dry_run)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
