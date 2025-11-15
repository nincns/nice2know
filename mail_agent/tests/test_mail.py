#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Comprehensive Mail Connection Test
Tests both IMAP (receiving) and SMTP (sending) connections
"""
import os
import sys
import json
import imaplib
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.utils import formataddr

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def load_config():
    """Load configuration from mail_config.json and secrets.json"""
    # Script is in tests/, config is in parent directory
    script_dir = Path(__file__).resolve().parent
    config_base_dir = script_dir.parent / 'config'
    
    # mail_config.json is in config/connections/
    mail_config_path = config_base_dir / 'connections' / 'mail_config.json'
    # secrets.json is in config/
    secrets_path = config_base_dir / 'secrets.json'
    
    if not mail_config_path.exists():
        print(f"{RED}✗ mail_config.json not found at {mail_config_path}!{NC}")
        sys.exit(1)
    
    if not secrets_path.exists():
        print(f"{RED}✗ secrets.json not found at {secrets_path}!{NC}")
        sys.exit(1)
    
    with open(mail_config_path, 'r') as f:
        mail_config = json.load(f)
    
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    
    return mail_config, secrets

def test_imap_connection(mail_config, secrets):
    """Test IMAP connection (receiving mails)"""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Testing IMAP Connection (Mail Receiving){NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")
    
    imap_config = mail_config.get('imap', {})
    imap_creds = secrets.get('imap', {})
    
    host = imap_config.get('host', '')
    port = imap_config.get('port', 993)
    use_ssl = imap_config.get('use_ssl', True)
    username = imap_creds.get('username', '')
    password = imap_creds.get('password', '')
    
    print(f"Configuration:")
    print(f"  Host:     {host}:{port}")
    print(f"  SSL:      {use_ssl}")
    print(f"  Username: {username}")
    print(f"  Password: {'*' * len(password) if password else '(not set)'}")
    print()
    
    if not username or not password:
        print(f"{RED}✗ IMAP credentials missing!{NC}")
        return False
    
    try:
        print(f"Attempting connection to {host}:{port}...")
        
        if use_ssl:
            imap = imaplib.IMAP4_SSL(host, port, timeout=10)
        else:
            imap = imaplib.IMAP4(host, port, timeout=10)
        
        print(f"{GREEN}✓ TCP connection established{NC}")
        
        print(f"Attempting login as {username}...")
        imap.login(username, password)
        print(f"{GREEN}✓ Authentication successful{NC}")
        
        print(f"Selecting INBOX...")
        status, messages = imap.select('INBOX')
        if status == 'OK':
            count = int(messages[0])
            print(f"{GREEN}✓ INBOX selected ({count} messages){NC}")
        
        imap.logout()
        print(f"{GREEN}✓ Connection closed cleanly{NC}")
        
        print(f"\n{GREEN}{'=' * 60}{NC}")
        print(f"{GREEN}✓ IMAP TEST PASSED{NC}")
        print(f"{GREEN}{'=' * 60}{NC}")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"{RED}✗ IMAP Error: {e}{NC}")
        return False
    except ConnectionRefusedError:
        print(f"{RED}✗ Connection refused - Port {port} not accessible{NC}")
        print(f"{YELLOW}  Check if IMAP is enabled on the server{NC}")
        return False
    except TimeoutError:
        print(f"{RED}✗ Connection timeout - Server not reachable{NC}")
        return False
    except Exception as e:
        print(f"{RED}✗ Unexpected error: {e}{NC}")
        return False

def test_smtp_connection(mail_config, secrets, send_test_mail=False):
    """Test SMTP connection (sending mails)"""
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Testing SMTP Connection (Mail Sending){NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")
    
    # Try to get SMTP config, fallback to IMAP host
    imap_config = mail_config.get('imap', {})
    smtp_creds = secrets.get('smtp', {})
    imap_creds = secrets.get('imap', {})
    
    # SMTP host (from secrets or derived from IMAP)
    host = smtp_creds.get('host', imap_config.get('host', ''))
    port = smtp_creds.get('port', 587)
    use_ssl = smtp_creds.get('use_ssl', False)
    use_starttls = smtp_creds.get('use_starttls', True)
    username = smtp_creds.get('username', imap_creds.get('username', ''))
    password = smtp_creds.get('password', imap_creds.get('password', ''))
    from_address = smtp_creds.get('from_address', username)
    from_name = smtp_creds.get('from_name', 'Nice2Know System')
    
    print(f"Configuration:")
    print(f"  Host:      {host}:{port}")
    print(f"  SSL:       {use_ssl}")
    print(f"  STARTTLS:  {use_starttls}")
    print(f"  Username:  {username}")
    print(f"  Password:  {'*' * len(password) if password else '(not set)'}")
    print(f"  From:      {from_name} <{from_address}>")
    print()
    
    if not username or not password:
        print(f"{RED}✗ SMTP credentials missing!{NC}")
        return False
    
    try:
        print(f"Attempting connection to {host}:{port}...")
        
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
            print(f"{GREEN}✓ SSL connection established{NC}")
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            print(f"{GREEN}✓ TCP connection established{NC}")
            
            if use_starttls:
                print(f"Upgrading to TLS...")
                server.starttls()
                print(f"{GREEN}✓ STARTTLS successful{NC}")
        
        print(f"Attempting login as {username}...")
        server.login(username, password)
        print(f"{GREEN}✓ Authentication successful{NC}")
        
        if send_test_mail:
            print(f"\n{YELLOW}Send test mail?{NC}")
            recipient = input(f"  Recipient address (or Enter to skip): ").strip()
            
            if recipient:
                msg = MIMEText(
                    f"This is a test email from Nice2Know Mail Agent.\n\n"
                    f"SMTP Server: {host}:{port}\n"
                    f"Sender: {from_address}\n\n"
                    f"If you received this, your SMTP configuration is working!",
                    'plain',
                    'utf-8'
                )
                msg['Subject'] = 'Nice2Know SMTP Test'
                msg['From'] = formataddr((from_name, from_address))
                msg['To'] = recipient
                
                print(f"Sending test mail to {recipient}...")
                server.sendmail(from_address, [recipient], msg.as_string())
                print(f"{GREEN}✓ Test mail sent successfully{NC}")
        
        server.quit()
        print(f"{GREEN}✓ Connection closed cleanly{NC}")
        
        print(f"\n{GREEN}{'=' * 60}{NC}")
        print(f"{GREEN}✓ SMTP TEST PASSED{NC}")
        print(f"{GREEN}{'=' * 60}{NC}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"{RED}✗ Authentication failed: {e}{NC}")
        print(f"{YELLOW}  Check username/password in secrets.json{NC}")
        return False
    except ConnectionRefusedError:
        print(f"{RED}✗ Connection refused - Port {port} not accessible{NC}")
        print(f"{YELLOW}  Possible reasons:{NC}")
        print(f"{YELLOW}    - Firewall blocking port {port}{NC}")
        print(f"{YELLOW}    - SMTP not running on this port{NC}")
        print(f"{YELLOW}    - Try port 465 (SMTP/SSL) or 25 (plain SMTP){NC}")
        return False
    except TimeoutError:
        print(f"{RED}✗ Connection timeout - Server not reachable{NC}")
        return False
    except smtplib.SMTPException as e:
        print(f"{RED}✗ SMTP Error: {e}{NC}")
        return False
    except Exception as e:
        print(f"{RED}✗ Unexpected error: {e}{NC}")
        return False

def main():
    """Main test runner"""
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Nice2Know Mail Agent - Connection Test{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    
    try:
        mail_config, secrets = load_config()
    except Exception as e:
        print(f"{RED}✗ Failed to load configuration: {e}{NC}")
        sys.exit(1)
    
    # Test IMAP
    imap_ok = test_imap_connection(mail_config, secrets)
    
    # Test SMTP
    smtp_ok = test_smtp_connection(mail_config, secrets, send_test_mail=True)
    
    # Summary
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}Test Summary{NC}")
    print(f"{BLUE}{'=' * 60}{NC}")
    print(f"  IMAP (Receiving): {GREEN + '✓ OK' + NC if imap_ok else RED + '✗ FAILED' + NC}")
    print(f"  SMTP (Sending):   {GREEN + '✓ OK' + NC if smtp_ok else RED + '✗ FAILED' + NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")
    
    if imap_ok and smtp_ok:
        print(f"{GREEN}✓ All tests passed! Your mail configuration is correct.{NC}")
        sys.exit(0)
    else:
        print(f"{RED}✗ Some tests failed. Check the configuration above.{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
