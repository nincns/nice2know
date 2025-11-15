#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Main Runner
"""
import json
import sys
import argparse
from pathlib import Path
from agents.imap_fetcher import IMAPFetcher
from agents.mail_parser import MailParser
from agents.attachment_handler import AttachmentHandler
from utils.logger import get_logger
from utils.file_handler import FileHandler

logger = get_logger()

def load_config(config_path: str = None) -> dict:
    """Load mail agent configuration"""
    if not config_path:
        config_path = Path(__file__).parent / 'config' / 'mail_config.json'
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_agent(config: dict, dry_run: bool = False):
    """Main agent execution"""
    logger.info("=" * 60)
    logger.info("Nice2Know Mail Agent - Starting")
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
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing message {msg_id}: {e}", exc_info=True)
    
    # Cleanup
    fetcher.disconnect()
    
    logger.info("=" * 60)
    logger.info(f"Processed {processed_count}/{len(messages)} messages")
    logger.info("Mail Agent finished")
    logger.info("=" * 60)
    
    return 0

def main():
    parser = argparse.ArgumentParser(description='Nice2Know Mail Agent')
    parser.add_argument('--config', help='Path to mail_config.json', default=None)
    parser.add_argument('--dry-run', action='store_true', help='Fetch but don\'t save')
    parser.add_argument('--loop', action='store_true', help='Run continuously')
    parser.add_argument('--interval', type=int, default=60, help='Loop interval in seconds')
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error("Configuration file not found. Please create config/mail_config.json")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return 1
    
    if args.loop:
        import time
        logger.info(f"Running in loop mode (interval: {args.interval}s)")
        while True:
            run_agent(config, args.dry_run)
            logger.info(f"Sleeping for {args.interval} seconds...")
            time.sleep(args.interval)
    else:
        return run_agent(config, args.dry_run)

if __name__ == '__main__':
    sys.exit(main())
