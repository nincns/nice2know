# In das Projekt wechseln
cd /opt/nice2know

# Die Datei erstellen
cat > mail_agent/utils/web_config_utils.py << 'EOF'
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
        
        return config
    except Exception as e:
        print(f"Error loading application config: {e}")
        return get_default_config()

def get_default_config() -> dict:
    """Return default configuration"""
    return {
        'base_url': 'http://10.147.17.50/n2k',
        'admin': {
            'email': 'support@nice2know.local'
        }
    }

def get_editor_url(mail_id: str) -> str:
    """
    Generate editor URL for a given mail_id (hex format from JSON)
    
    Args:
        mail_id: The hex mail_id from problem.json (e.g. '575496876c3645bc8bf5f79c1696c134')
    
    Returns:
        Full URL to the editor
    """
    config = load_application_config()
    base_url = config.get('base_url', 'http://10.147.17.50/n2k')
    
    # Ensure no trailing slash
    base_url = base_url.rstrip('/')
    
    return f"{base_url}/?mail_id={mail_id}"

def get_confirm_url(mail_id: str) -> str:
    """
    Generate confirmation URL for a given mail_id
    
    Args:
        mail_id: The hex mail_id from problem.json
    
    Returns:
        Full URL to the confirmation page
    """
    config = load_application_config()
    base_url = config.get('base_url', 'http://10.147.17.50/n2k')
    
    # Ensure no trailing slash
    base_url = base_url.rstrip('/')
    
    return f"{base_url}/confirm.php?mail_id={mail_id}"

def get_support_email() -> str:
    """
    Get support email from configuration
    
    Returns:
        Support email address
    """
    config = load_application_config()
    return config.get('admin', {}).get('email', 'support@nice2know.local')

# For testing
if __name__ == '__main__':
    print("Testing web_config_utils...")
    print("=" * 60)
    
    config = load_application_config()
    print(f"Base URL: {config.get('base_url')}")
    print(f"Support Email: {config.get('admin', {}).get('email')}")
    print()
    
    test_mail_id = "575496876c3645bc8bf5f79c1696c134"
    print(f"Test Mail ID: {test_mail_id}")
    print(f"Editor URL: {get_editor_url(test_mail_id)}")
    print(f"Confirm URL: {get_confirm_url(test_mail_id)}")
    print(f"Support Email: {get_support_email()}")
EOF

# Testen
cd /opt/nice2know
python mail_agent/utils/web_config_utils.py

# Dann run_send_response.py testen
python mail_agent/run_send_response.py
