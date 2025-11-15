#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Attachment Handler
"""
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.file_handler import FileHandler

logger = get_logger()

class AttachmentHandler:
    def __init__(self, file_handler: FileHandler, max_size_mb: int = 50):
        self.file_handler = file_handler
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def extract_attachments(self, attachments: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract and save all attachments
        Returns list of saved attachment metadata
        """
        saved = []
        
        for att in attachments:
            try:
                # Size check
                if att['size'] > self.max_size_bytes:
                    logger.warning(
                        f"Attachment '{att['filename']}' too large "
                        f"({att['size'] / 1024 / 1024:.2f} MB), skipping"
                    )
                    continue
                
                # Extract content
                content = att['part'].get_payload(decode=True)
                if not content:
                    logger.warning(f"Empty attachment: {att['filename']}")
                    continue
                
                # Categorize
                category = self.file_handler.categorize_attachment(
                    att['filename'], 
                    att['content_type']
                )
                
                # Save
                filepath = self.file_handler.save_attachment(
                    att['filename'], 
                    content, 
                    category
                )
                
                saved.append({
                    'original_name': att['filename'],
                    'saved_path': str(filepath),
                    'category': category,
                    'size': att['size'],
                    'mime_type': att['content_type']
                })
                
            except Exception as e:
                logger.error(f"Failed to extract attachment '{att.get('filename', 'unknown')}': {e}")
        
        logger.info(f"Extracted {len(saved)}/{len(attachments)} attachments")
        return saved
