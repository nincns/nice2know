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
        """
        Initialize FileHandler with storage base path
        
        Args:
            base_path: Absolute or relative path to storage directory
        """
        # Convert to Path object and resolve to absolute path
        self.base_path = Path(base_path).resolve()
        
        logger.info(f"FileHandler initialized with base_path: {self.base_path}")
        
        # Validate base path
        if not self.base_path.exists():
            logger.warning(f"Base path does not exist, will be created: {self.base_path}")
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create all required directories"""
        dirs = [
            self.base_path / 'mails',
            self.base_path / 'attachments' / 'images',
            self.base_path / 'attachments' / 'documents',
            self.base_path / 'attachments' / 'logs',
            self.base_path / 'processed',
            self.base_path / 'failed',
            self.base_path / 'sent'
        ]
        
        for d in dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {d}")
            except Exception as e:
                logger.error(f"Failed to create directory {d}: {e}")
                raise
    
    def save_mail(self, mail_id: str, content: bytes, extension: str = 'eml') -> Path:
        """
        Save raw email to disk
        
        Args:
            mail_id: Message ID (will be sanitized)
            content: Raw email content as bytes
            extension: File extension (default: eml)
        
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_mail_id = self._sanitize_filename(mail_id)
        filename = f"{timestamp}_{safe_mail_id}.{extension}"
        filepath = self.base_path / 'mails' / filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(content)
            
            logger.info(f"Saved mail: {filepath.name} ({len(content)} bytes)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save mail {filename}: {e}")
            raise
    
    def save_attachment(self, filename: str, content: bytes, category: str = 'documents') -> Path:
        """
        Save attachment to categorized directory
        
        Args:
            filename: Original attachment filename
            content: File content as bytes
            category: Category folder (images/documents/logs)
        
        Returns:
            Path to saved file
        """
        safe_filename = self._sanitize_filename(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Add hash to prevent duplicates
        file_hash = hashlib.md5(content).hexdigest()[:8]
        name, ext = os.path.splitext(safe_filename)
        unique_filename = f"{timestamp}_{file_hash}_{name}{ext}"
        
        # Validate category
        valid_categories = ['images', 'documents', 'logs']
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}', using 'documents'")
            category = 'documents'
        
        filepath = self.base_path / 'attachments' / category / unique_filename
        
        try:
            with open(filepath, 'wb') as f:
                f.write(content)
            
            logger.info(f"Saved attachment: {category}/{unique_filename} ({len(content)} bytes)")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save attachment {unique_filename}: {e}")
            raise
    
    def move_to_processed(self, mail_path: Path) -> Path:
        """
        Move processed mail to archive
        
        Args:
            mail_path: Path to mail file
        
        Returns:
            New path in processed folder
        """
        if not mail_path.exists():
            logger.error(f"Mail file not found: {mail_path}")
            raise FileNotFoundError(f"Mail file not found: {mail_path}")
        
        dest = self.base_path / 'processed' / mail_path.name
        
        try:
            mail_path.rename(dest)
            logger.debug(f"Moved to processed: {mail_path.name}")
            return dest
        except Exception as e:
            logger.error(f"Failed to move mail to processed: {e}")
            raise
    
    def move_to_failed(self, mail_path: Path) -> Path:
        """
        Move failed mail to failed folder
        
        Args:
            mail_path: Path to mail file
        
        Returns:
            New path in failed folder
        """
        if not mail_path.exists():
            logger.error(f"Mail file not found: {mail_path}")
            raise FileNotFoundError(f"Mail file not found: {mail_path}")
        
        dest = self.base_path / 'failed' / mail_path.name
        
        try:
            mail_path.rename(dest)
            logger.debug(f"Moved to failed: {mail_path.name}")
            return dest
        except Exception as e:
            logger.error(f"Failed to move mail to failed folder: {e}")
            raise
    
    def get_mails_directory(self) -> Path:
        """Get path to mails directory"""
        return self.base_path / 'mails'
    
    def get_processed_directory(self) -> Path:
        """Get path to processed directory"""
        return self.base_path / 'processed'
    
    def get_failed_directory(self) -> Path:
        """Get path to failed directory"""
        return self.base_path / 'failed'
    
    def get_attachments_directory(self, category: str = None) -> Path:
        """
        Get path to attachments directory
        
        Args:
            category: Optional category (images/documents/logs)
        
        Returns:
            Path to attachments or category folder
        """
        if category:
            return self.base_path / 'attachments' / category
        return self.base_path / 'attachments'
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Remove/replace unsafe characters from filename
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        unsafe_chars = '<>:"/\\|?*'
        safe = filename
        for char in unsafe_chars:
            safe = safe.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        safe = safe.strip('. ')
        
        # Limit length
        if len(safe) > 200:
            name, ext = os.path.splitext(safe)
            safe = name[:190] + ext
        
        # Ensure not empty
        if not safe:
            safe = 'unnamed'
        
        return safe
    
    @staticmethod
    def categorize_attachment(filename: str, mime_type: str = None) -> str:
        """
        Determine storage category based on file type
        
        Args:
            filename: Attachment filename
            mime_type: Optional MIME type
        
        Returns:
            Category name (images/documents/logs)
        """
        ext = Path(filename).suffix.lower()
        
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        doc_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                    '.txt', '.md', '.rtf', '.odt', '.ods', '.odp'}
        log_exts = {'.log', '.txt'}
        
        # Check MIME type first (more reliable)
        if mime_type:
            if mime_type.startswith('image/'):
                return 'images'
            elif mime_type.startswith('application/') or mime_type.startswith('text/'):
                # Could be document or log
                if ext in log_exts and 'log' in filename.lower():
                    return 'logs'
                return 'documents'
        
        # Fallback to extension
        if ext in image_exts:
            return 'images'
        elif ext in log_exts and 'log' in filename.lower():
            return 'logs'
        elif ext in doc_exts:
            return 'documents'
        else:
            return 'documents'  # Default

# Test/Debug functionality
if __name__ == '__main__':
    print("=" * 60)
    print("FileHandler - Test Mode")
    print("=" * 60)
    
    # Test with default path
    test_base = Path(__file__).parent.parent / 'storage'
    
    print(f"\nInitializing FileHandler with base: {test_base}")
    handler = FileHandler(str(test_base))
    
    print(f"\nDirectory structure:")
    print(f"  Mails:       {handler.get_mails_directory()}")
    print(f"  Processed:   {handler.get_processed_directory()}")
    print(f"  Failed:      {handler.get_failed_directory()}")
    print(f"  Attachments: {handler.get_attachments_directory()}")
    
    print(f"\nFilename sanitization tests:")
    test_names = [
        "normal_file.txt",
        "file with spaces.pdf",
        "file<>with:bad|chars?.doc",
        "../../../etc/passwd",
        "a" * 250 + ".txt"
    ]
    
    for name in test_names:
        safe = handler._sanitize_filename(name)
        print(f"  '{name}' -> '{safe}'")
    
    print(f"\nCategory detection tests:")
    test_files = [
        ("screenshot.png", "image/png", "images"),
        ("document.pdf", "application/pdf", "documents"),
        ("error.log", "text/plain", "logs"),
        ("unknown.xyz", None, "documents")
    ]
    
    for filename, mime, expected in test_files:
        result = handler.categorize_attachment(filename, mime)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {filename} ({mime}) -> {result} (expected: {expected})")
    
    print("\n" + "=" * 60)
