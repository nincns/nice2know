#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Credential Manager
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

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
        """
        Get credential for a service
        
        Args:
            service: Service name (e.g., 'imap', 'smtp', 'llm')
            key: Optional key within service (e.g., 'username', 'password')
        
        Returns:
            If key is None: entire service dict
            If key is provided: specific value
        """
        if not self._secrets:
            raise RuntimeError("Secrets not loaded!")
        
        if service not in self._secrets:
            raise KeyError(f"Service '{service}' not found in secrets")
        
        service_data = self._secrets[service]
        
        # Return entire service if no key specified
        if key is None:
            return service_data
        
        # Return specific key
        if key not in service_data:
            raise KeyError(f"Key '{key}' not found in service '{service}'")
        
        return service_data[key]
    
    def get_imap_credentials(self) -> Dict[str, str]:
        """Convenience method for IMAP credentials"""
        return self.get('imap')
    
    def get_smtp_credentials(self) -> Dict[str, Any]:
        """Convenience method for SMTP credentials"""
        return self.get('smtp')
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Convenience method for LLM configuration"""
        return self.get('llm')
    
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