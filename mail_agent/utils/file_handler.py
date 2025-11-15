#!/usr/bin/env python3
"""
Nice2Know Mail Agent - File Operations
"""
import os
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger()

class FileHandler:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create all required directories"""
        dirs = [
            self.base_path / 'mails',
            self.base_path / 'attachments' / 'images',
            self.base_path / 'attachments' / 'documents',
            self.base_path / 'attachments' / 'logs',
            self.base_path / 'processed'
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {d}")
    
    def save_mail(self, mail_id: str, content: bytes, extension: str = 'eml') -> Path:
        """Save raw email to disk"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{self._sanitize_filename(mail_id)}.{extension}"
        filepath = self.base_path / 'mails' / filename
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved mail: {filepath.name}")
        return filepath
    
    def save_attachment(self, filename: str, content: bytes, category: str = 'documents') -> Path:
        """Save attachment to categorized directory"""
        safe_filename = self._sanitize_filename(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Add hash to prevent duplicates
        file_hash = hashlib.md5(content).hexdigest()[:8]
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{timestamp}_{file_hash}_{name}{ext}"
        
        filepath = self.base_path / 'attachments' / category / unique_filename
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved attachment: {category}/{unique_filename} ({len(content)} bytes)")
        return filepath
    
    def move_to_processed(self, mail_path: Path) -> Path:
        """Move processed mail to archive"""
        dest = self.base_path / 'processed' / mail_path.name
        mail_path.rename(dest)
        logger.debug(f"Moved to processed: {mail_path.name}")
        return dest
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove/replace unsafe characters"""
        unsafe_chars = '<>:"/\\|?*'
        safe = filename
        for char in unsafe_chars:
            safe = safe.replace(char, '_')
        return safe[:200]  # Limit length
    
    @staticmethod
    def categorize_attachment(filename: str, mime_type: str = None) -> str:
        """Determine storage category based on file type"""
        ext = Path(filename).suffix.lower()
        
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'}
        log_exts = {'.log', '.txt'}
        
        if ext in image_exts or (mime_type and mime_type.startswith('image/')):
            return 'images'
        elif ext in doc_exts or (mime_type and mime_type.startswith('application/')):
            return 'documents'
        elif ext in log_exts:
            return 'logs'
        else:
            return 'documents'  # Default