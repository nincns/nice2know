#!/usr/bin/env python3
"""
Nice2Know - Web Configuration Utilities
Loads configuration from config/connections/application.json
"""
import json
from pathlib import Path

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

def load_application_config() -> dict:
    """Load application configuration from JSON"""
    try:
        script_dir = Path(__file__).resolve().parent
        mail_agent_root = find_mail_agent_root(script_dir)
        
        config_file = mail_agent_root / 'config' / 'connections' / 'application.json'
        
        if not config_file.exists():
            print(f"Warning: application.json not found at {config_file}")
            return get_default_config()
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Add mail_agent_root to config for path resolution
        config['_mail_agent_root'] = str(mail_agent_root)
        
        return config
    except Exception as e:
        print(f"Error loading application config: {e}")
        return get_default_config()

def get_default_config() -> dict:
    """Return default configuration"""
    return {
        'app_name': 'Nice2Know',
        'version': '1.0.0',
        'base_url': 'http://localhost/n2k',
        'admin': {
            'email': 'support@nice2know.local',
            'enable_registration': False
        },
        'storage': {
            'base_path': './storage',
            'max_attachment_size_mb': 50
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/mail_agent.log'
        },
        'filters': {
            'mark_as_read': False,
            'move_to_processed': True,
            'processed_folder': 'processed'
        }
    }

def get_storage_path() -> Path:
    """Get absolute storage path from config"""
    config = load_application_config()
    mail_agent_root = Path(config.get('_mail_agent_root', '.'))
    storage_base = config.get('storage', {}).get('base_path', './storage')
    
    # Resolve relative path
    if not Path(storage_base).is_absolute():
        storage_path = mail_agent_root / storage_base
    else:
        storage_path = Path(storage_base)
    
    return storage_path.resolve()

def get_editor_url(mail_id: str) -> str:
    """
    Generate editor URL for a given mail_id (hex format from JSON)
    
    Args:
        mail_id: The hex mail_id from problem.json
    
    Returns:
        Full URL to the editor
    """
    config = load_application_config()
    base_url = config.get('base_url', 'http://localhost/n2k')
    base_url = base_url.rstrip('/')
    return f"{base_url}/?mail_id={mail_id}"

def get_confirm_url(mail_id: str) -> str:
    """
    Generate confirmation URL for a given mail_id
    
    Args:
        mail_id: The hex mail_id from problem.json
    
    Returns:
        Full URL to confirm/view the processed knowledge entry
    """
    config = load_application_config()
    base_url = config.get('base_url', 'http://localhost/n2k')
    base_url = base_url.rstrip('/')
    return f"{base_url}/confirm.php?mail_id={mail_id}"

def get_support_email() -> str:
    """
    Get support/admin email from config
    
    Returns:
        Support email address
    """
    config = load_application_config()
    return config.get('admin', {}).get('email', 'support@nice2know.local')

def get_admin_email() -> str:
    """Get admin email from config (alias for get_support_email)"""
    return get_support_email()

def get_app_name() -> str:
    """Get application name from config"""
    config = load_application_config()
    return config.get('app_name', 'Nice2Know')

def get_max_attachment_size() -> int:
    """Get max attachment size in MB from config"""
    config = load_application_config()
    return config.get('storage', {}).get('max_attachment_size_mb', 50)

def get_processed_folder() -> str:
    """Get processed folder name from config"""
    config = load_application_config()
    return config.get('filters', {}).get('processed_folder', 'processed')

def get_logging_config() -> dict:
    """Get logging configuration"""
    config = load_application_config()
    return config.get('logging', {
        'level': 'INFO',
        'file': 'logs/mail_agent.log'
    })

# Example usage and testing
if __name__ == '__main__':
    print("=" * 60)
    print("Nice2Know - Configuration Test")
    print("=" * 60)
    
    config = load_application_config()
    
    print(f"\nApp Name:           {get_app_name()}")
    print(f"Version:            {config.get('version', 'unknown')}")
    print(f"Base URL:           {config.get('base_url', 'not set')}")
    print(f"Admin Email:        {get_admin_email()}")
    print(f"Support Email:      {get_support_email()}")
    print(f"Storage Path:       {get_storage_path()}")
    print(f"Max Attachment:     {get_max_attachment_size()} MB")
    print(f"Processed Folder:   {get_processed_folder()}")
    print(f"Logging Level:      {get_logging_config().get('level', 'INFO')}")
    
    print("\nURL Generation Test:")
    test_mail_id = "abc123def456"
    print(f"Editor URL:         {get_editor_url(test_mail_id)}")
    print(f"Confirm URL:        {get_confirm_url(test_mail_id)}")
    
    print("\n" + "=" * 60)
