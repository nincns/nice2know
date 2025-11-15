#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Email Parser
"""
import email
from email import policy
from email.header import decode_header
from datetime import datetime
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger()

class MailParser:
    def __init__(self):
        pass
    
    def parse(self, raw_email: bytes) -> Dict[str, Any]:
        """
        Parse raw email bytes into structured data
        Returns dict with metadata and content
        """
        try:
            msg = email.message_from_bytes(raw_email, policy=policy.default)
            
            parsed = {
                'message_id': self._extract_message_id(msg),
                'from': self._decode_header(msg.get('From', '')),
                'to': self._decode_header(msg.get('To', '')),
                'cc': self._decode_header(msg.get('Cc', '')),
                'subject': self._decode_header(msg.get('Subject', '')),
                'date': self._parse_date(msg.get('Date', '')),
                'body': self._extract_body(msg),
                'attachments': self._extract_attachments(msg),
                'headers': dict(msg.items()),
                'raw_size': len(raw_email)
            }
            
            logger.info(f"Parsed mail: {parsed['subject'][:50]}... ({len(parsed['attachments'])} attachments)")
            return parsed
            
        except Exception as e:
            logger.error(f"Mail parsing failed: {e}")
            return None
    
    @staticmethod
    def _extract_message_id(msg) -> str:
        """Extract unique Message-ID header"""
        msg_id = msg.get('Message-ID', '').strip('<>')
        if not msg_id:
            # Fallback: generate from date + subject hash
            import hashlib
            raw = f"{msg.get('Date', '')}{msg.get('Subject', '')}"
            msg_id = f"generated-{hashlib.md5(raw.encode()).hexdigest()}"
        return msg_id
    
    @staticmethod
    def _decode_header(header_value: str) -> str:
        """Decode MIME encoded headers"""
        if not header_value:
            return ''
        
        decoded_parts = []
        for part, encoding in decode_header(header_value):
            if isinstance(part, bytes):
                try:
                    decoded = part.decode(encoding or 'utf-8', errors='replace')
                except:
                    decoded = part.decode('utf-8', errors='replace')
            else:
                decoded = part
            decoded_parts.append(decoded)
        
        return ' '.join(decoded_parts)
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse email date to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _extract_body(self, msg) -> Dict[str, str]:
        """Extract plain text and HTML body"""
        body = {
            'plain': '',
            'html': ''
        }
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = part.get_content_disposition()
                
                if disposition == 'attachment':
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        text = payload.decode(charset, errors='replace')
                        
                        if content_type == 'text/plain':
                            body['plain'] += text
                        elif content_type == 'text/html':
                            body['html'] += text
                except Exception as e:
                    logger.warning(f"Failed to extract body part: {e}")
        else:
            # Non-multipart message
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    text = payload.decode(charset, errors='replace')
                    content_type = msg.get_content_type()
                    
                    if content_type == 'text/plain':
                        body['plain'] = text
                    elif content_type == 'text/html':
                        body['html'] = text
            except Exception as e:
                logger.warning(f"Failed to extract body: {e}")
        
        return body
    
    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """Extract attachment metadata (not content yet)"""
        attachments = []
        
        for part in msg.walk():
            disposition = part.get_content_disposition()
            
            if disposition in ['attachment', 'inline']:
                filename = part.get_filename()
                if filename:
                    filename = self._decode_header(filename)
                else:
                    # Generate filename from content type
                    ext = part.get_content_type().split('/')[-1]
                    filename = f"unnamed.{ext}"
                
                attachments.append({
                    'filename': filename,
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload(decode=True) or b''),
                    'part': part  # Store part object for later extraction
                })
        
        return attachments
