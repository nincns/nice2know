#!/usr/bin/env python3
"""
Nice2Know Mail Agent - IMAP Fetcher
"""
import imaplib
from typing import List, Tuple
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.credentials import get_credentials

logger = get_logger()

class IMAPFetcher:
    def __init__(self, config: dict):
        self.config = config
        self.imap_config = config['imap']
        # Load secrets directly with new structure
        creds = get_credentials()
        mail_secrets = creds._secrets.get('mail', {})
        self.credentials = {
            'username': mail_secrets.get('imap_username', ''),
            'password': mail_secrets.get('imap_password', '')
        }
        self.connection = None
    
    def connect(self) -> bool:
        """Establish IMAP connection"""
        try:
            if self.imap_config['use_ssl']:
                self.connection = imaplib.IMAP4_SSL(
                    self.imap_config['host'],
                    self.imap_config['port']
                )
            else:
                self.connection = imaplib.IMAP4(
                    self.imap_config['host'],
                    self.imap_config['port']
                )
            
            # Credentials from secrets.json
            self.connection.login(
                self.credentials['username'],
                self.credentials['password']
            )
            
            logger.info(f"✓ Connected to {self.imap_config['host']}:{self.imap_config['port']}")
            return True
            
        except Exception as e:
            logger.error(f"✗ IMAP connection failed: {e}")
            return False
    
    def select_mailbox(self, mailbox: str = None) -> bool:
        """Select mailbox/folder"""
        if not self.connection:
            logger.error("No active IMAP connection")
            return False
        
        mailbox = mailbox or self.imap_config.get('mailbox', 'INBOX')
        
        try:
            status, messages = self.connection.select(mailbox)
            if status == 'OK':
                count = int(messages[0])
                logger.info(f"Selected mailbox '{mailbox}' ({count} messages)")
                return True
            else:
                logger.error(f"Failed to select mailbox '{mailbox}'")
                return False
        except Exception as e:
            logger.error(f"Mailbox selection error: {e}")
            return False
    
    def fetch_messages(self, limit: int = None, unseen_only: bool = True) -> List[Tuple[str, bytes]]:
        """
        Fetch emails from mailbox
        Returns: List of (message_id, raw_email_bytes)
        """
        if not self.connection:
            logger.error("No active IMAP connection")
            return []
        
        try:
            # Search criteria
            search_criteria = 'UNSEEN' if unseen_only else 'ALL'
            status, message_ids = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                logger.warning("No messages found")
                return []
            
            id_list = message_ids[0].split()
            
            if not id_list:
                logger.info("No messages to fetch")
                return []
            
            # Apply limit
            if limit and limit > 0:
                id_list = id_list[-limit:]  # Get most recent N messages
            
            logger.info(f"Fetching {len(id_list)} message(s)...")
            
            messages = []
            for num in id_list:
                try:
                    status, msg_data = self.connection.fetch(num, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        message_id = num.decode('utf-8')
                        messages.append((message_id, raw_email))
                        logger.debug(f"Fetched message ID {message_id}")
                    else:
                        logger.warning(f"Failed to fetch message {num}")
                except Exception as e:
                    logger.error(f"Error fetching message {num}: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Message fetch error: {e}")
            return []
    
    def mark_as_read(self, message_id: str):
        """Mark message as read/seen"""
        try:
            self.connection.store(message_id, '+FLAGS', '\\Seen')
            logger.debug(f"Marked message {message_id} as read")
        except Exception as e:
            logger.error(f"Failed to mark message {message_id} as read: {e}")
    
    def move_to_folder(self, message_id: str, target_folder: str = 'processed'):
        """Move message to another IMAP folder"""
        try:
            # Copy to target folder
            result = self.connection.copy(message_id, target_folder)
            if result[0] == 'OK':
                # Mark original as deleted (but don't expunge yet)
                self.connection.store(message_id, '+FLAGS', '\\Deleted')
                logger.info(f"Moved message {message_id} to '{target_folder}'")
                return True
            else:
                logger.warning(f"Failed to copy message {message_id} to '{target_folder}'")
                return False
        except Exception as e:
            logger.error(f"Failed to move message {message_id}: {e}")
            return False
    
    def expunge_deleted(self):
        """Permanently remove messages marked as deleted"""
        try:
            self.connection.expunge()
            logger.info("✓ Expunged deleted messages")
        except Exception as e:
            logger.warning(f"Failed to expunge: {e}")
    
    def _ensure_folder(self, folder_name: str):
        """Create IMAP folder if it doesn't exist"""
        try:
            # List existing folders
            status, folders = self.connection.list()
            folder_names = [f.decode().split('"')[-2] for f in folders]
            
            if folder_name not in folder_names:
                logger.info(f"Creating IMAP folder '{folder_name}'...")
                self.connection.create(folder_name)
                logger.info(f"✓ Created folder '{folder_name}'")
        except Exception as e:
            logger.warning(f"Could not ensure folder '{folder_name}': {e}")
    
    def disconnect(self):
        """Close IMAP connection"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("✓ IMAP connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
