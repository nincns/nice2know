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

class CredentialManager:
    _instance = None
    _secrets = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._secrets = self._load_secrets()
        self._initialized = True
    
    def _load_secrets(self) -> Dict[str, Any]:
        """Load secrets from secrets.json"""
        secrets_path = Path(__file__).parent.parent / 'config' / 'secrets.json'
        
        if secrets_path.exists():
            try:
                with open(secrets_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load secrets.json: {e}")
        
        return {}
    
    def get(self, service: str, key: str = None) -> Any:
        """Get credential for a service"""
        if not self._secrets:
            raise RuntimeError("Secrets not loaded!")
        
        if service not in self._secrets:
            raise KeyError(f"Service '{service}' not found in secrets")
        
        if key is None:
            return self._secrets[service]
        
        if key not in self._secrets[service]:
            raise KeyError(f"Key '{key}' not found in service '{service}'")
        
        return self._secrets[service][key]
    
    def get_imap_credentials(self) -> Dict[str, str]:
        """Convenience method for IMAP credentials"""
        return self.get('imap')
    
    def get_smtp_credentials(self) -> Dict[str, Any]:
        """Convenience method for SMTP credentials"""
        return self.get('smtp')
    
    def get_db_credentials(self) -> Dict[str, Any]:
        """Convenience method for PostgreSQL credentials"""
        return self.get('postgresql')

# Global instance
_credentials = None

def get_credentials() -> CredentialManager:
    """Get global credential manager instance"""
    global _credentials
    if _credentials is None:
        _credentials = CredentialManager()
    return _credentials
