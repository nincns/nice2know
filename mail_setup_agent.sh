#!/bin/bash
# ==============================================================================
# Nice2Know Mail Agent - Setup Script
# Creates directory structure and initial files
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIL_AGENT_DIR="${PROJECT_ROOT}/mail_agent"

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}Nice2Know Mail Agent - Setup${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# ==============================================================================
# Function: Create directory
# ==============================================================================
create_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✓${NC} Created directory: ${dir#$PROJECT_ROOT/}"
    else
        echo -e "${YELLOW}⊙${NC} Directory exists: ${dir#$PROJECT_ROOT/}"
    fi
}

# ==============================================================================
# 1. Create base directory structure
# ==============================================================================
echo -e "\n${BLUE}[1/6]${NC} Creating directory structure..."

create_dir "$MAIL_AGENT_DIR"
create_dir "$MAIL_AGENT_DIR/config"
create_dir "$MAIL_AGENT_DIR/agents"
create_dir "$MAIL_AGENT_DIR/storage"
create_dir "$MAIL_AGENT_DIR/storage/mails"
create_dir "$MAIL_AGENT_DIR/storage/attachments"
create_dir "$MAIL_AGENT_DIR/storage/attachments/images"
create_dir "$MAIL_AGENT_DIR/storage/attachments/documents"
create_dir "$MAIL_AGENT_DIR/storage/attachments/logs"
create_dir "$MAIL_AGENT_DIR/storage/processed"
create_dir "$MAIL_AGENT_DIR/utils"
create_dir "$MAIL_AGENT_DIR/tests"
create_dir "$MAIL_AGENT_DIR/logs"
create_dir "$MAIL_AGENT_DIR/systemd"

# ==============================================================================
# 2. Create Python __init__.py files
# ==============================================================================
echo -e "\n${BLUE}[2/6]${NC} Creating Python package files..."

cat > "$MAIL_AGENT_DIR/__init__.py" << 'EOF'
"""Nice2Know Mail Agent"""
__version__ = "1.0.0"
EOF
echo -e "${GREEN}✓${NC} Created __init__.py"

cat > "$MAIL_AGENT_DIR/agents/__init__.py" << 'EOF'
"""Mail Agent Components"""
from .imap_fetcher import IMAPFetcher
from .mail_parser import MailParser
from .attachment_handler import AttachmentHandler

__all__ = ["IMAPFetcher", "MailParser", "AttachmentHandler"]
EOF
echo -e "${GREEN}✓${NC} Created agents/__init__.py"

cat > "$MAIL_AGENT_DIR/utils/__init__.py" << 'EOF'
"""Utility Functions"""
from .logger import get_logger
from .file_handler import FileHandler
from .credentials import get_credentials

__all__ = ["get_logger", "FileHandler", "get_credentials"]
EOF
echo -e "${GREEN}✓${NC} Created utils/__init__.py"

# ==============================================================================
# 3. Create main Python files (dummy/templates)
# ==============================================================================
echo -e "\n${BLUE}[3/6]${NC} Creating Python source files (templates)..."

cat > "$MAIL_AGENT_DIR/agents/imap_fetcher.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - IMAP Fetcher
TODO: Implement IMAP mail fetching logic
"""
EOF
echo -e "${GREEN}✓${NC} Created agents/imap_fetcher.py"

cat > "$MAIL_AGENT_DIR/agents/mail_parser.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Email Parser
TODO: Implement email parsing logic
"""
EOF
echo -e "${GREEN}✓${NC} Created agents/mail_parser.py"

cat > "$MAIL_AGENT_DIR/agents/attachment_handler.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Attachment Handler
TODO: Implement attachment extraction logic
"""
EOF
echo -e "${GREEN}✓${NC} Created agents/attachment_handler.py"

cat > "$MAIL_AGENT_DIR/utils/logger.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Logger Setup
TODO: Implement logging configuration
"""
EOF
echo -e "${GREEN}✓${NC} Created utils/logger.py"

cat > "$MAIL_AGENT_DIR/utils/file_handler.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - File Operations
TODO: Implement file handling utilities
"""
EOF
echo -e "${GREEN}✓${NC} Created utils/file_handler.py"

cat > "$MAIL_AGENT_DIR/utils/credentials.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Credential Manager
TODO: Implement secure credential loading
"""
EOF
echo -e "${GREEN}✓${NC} Created utils/credentials.py"

cat > "$MAIL_AGENT_DIR/run_agent.py" << 'EOF'
#!/usr/bin/env python3
"""
Nice2Know Mail Agent - Main Runner
TODO: Implement main execution logic
"""

import sys

def main():
    print("Nice2Know Mail Agent - Not yet implemented")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x "$MAIL_AGENT_DIR/run_agent.py"
echo -e "${GREEN}✓${NC} Created run_agent.py (executable)"

# ==============================================================================
# 4. Create configuration files
# ==============================================================================
echo -e "\n${BLUE}[4/6]${NC} Creating configuration files..."

cat > "$MAIL_AGENT_DIR/config/mail_config.json" << 'EOF'
{
  "imap": {
    "host": "imap.example.com",
    "port": 993,
    "use_ssl": true,
    "mailbox": "INBOX"
  },
  "filters": {
    "subject_contains": [],
    "from_domains": [],
    "mark_as_read": true,
    "delete_after_fetch": false
  },
  "storage": {
    "base_path": "./storage",
    "mails_dir": "mails",
    "attachments_dir": "attachments",
    "processed_dir": "processed",
    "max_attachment_size_mb": 50
  },
  "processing": {
    "fetch_limit": 50,
    "fetch_unseen_only": true,
    "save_raw_eml": true,
    "extract_attachments": true
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mail_agent.log",
    "console": true
  }
}
EOF
echo -e "${GREEN}✓${NC} Created config/mail_config.json"

cat > "$MAIL_AGENT_DIR/config/secrets.json.example" << 'EOF'
{
  "imap": {
    "username": "support@example.com",
    "password": "your-secure-password-here"
  },
  "smtp": {
    "username": "support@example.com",
    "password": "your-smtp-password-here"
  },
  "ollama": {
    "api_key": "optional-if-secured"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "nice2know",
    "username": "n2k_user",
    "password": "your-db-password-here"
  }
}
EOF
echo -e "${GREEN}✓${NC} Created config/secrets.json.example"
echo -e "${YELLOW}⚠️  Copy to config/secrets.json and add your credentials!${NC}"

cat > "$MAIL_AGENT_DIR/config/.env.example" << 'EOF'
# Nice2Know Mail Agent - Environment Variables
# Copy this file to .env and fill in your actual values

# IMAP Configuration (alternative to secrets.json)
N2K_IMAP_USER=support@example.com
N2K_IMAP_PASS=your-password-here

# SMTP Configuration
N2K_SMTP_USER=support@example.com
N2K_SMTP_PASS=your-smtp-password-here

# PostgreSQL
N2K_DB_HOST=localhost
N2K_DB_PORT=5432
N2K_DB_NAME=nice2know
N2K_DB_USER=n2k_user
N2K_DB_PASS=your-db-password-here

# Storage
STORAGE_PATH=./storage
MAX_ATTACHMENT_MB=50

# Processing
FETCH_LIMIT=50
FETCH_UNSEEN_ONLY=true
MARK_AS_READ=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mail_agent.log
EOF
echo -e "${GREEN}✓${NC} Created config/.env.example"

cat > "$MAIL_AGENT_DIR/requirements.txt" << 'EOF'
# Nice2Know Mail Agent - Python Dependencies

# IMAP & Mail Parsing
imapclient==3.0.1
email-validator==2.1.0

# File Handling
python-magic==0.4.27
pillow==10.1.0

# Utilities
python-dotenv==1.0.0

# PostgreSQL (later)
# psycopg2-binary==2.9.9

# Optional: OCR Support
# pytesseract==0.3.10

# Optional: PDF Processing
# PyPDF2==3.0.1
# pdfplumber==0.10.3
EOF
echo -e "${GREEN}✓${NC} Created requirements.txt"

# ==============================================================================
# 5. Create .gitignore
# ==============================================================================
echo -e "\n${BLUE}[5/6]${NC} Creating .gitignore..."

cat > "$MAIL_AGENT_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
env/
ENV/
.venv

# Storage (exclude actual mail data)
storage/mails/*.eml
storage/attachments/**/*
storage/processed/*.eml
!storage/**/.gitkeep

# Logs
logs/*.log
*.log
!logs/.gitkeep

# Configuration & Credentials - CRITICAL!
config/secrets.json
config/mail_config.json
config/.env
.env
secrets.json
*.secret
*.credentials
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Temporary
*.tmp
*.bak
*.backup
~*
EOF
echo -e "${GREEN}✓${NC} Created .gitignore"

# ==============================================================================
# 6. Create additional files
# ==============================================================================
echo -e "\n${BLUE}[6/6]${NC} Creating additional files..."

cat > "$MAIL_AGENT_DIR/README.md" << 'EOF'
# Nice2Know Mail Agent

Automated email fetching and processing for the Nice2Know knowledge management system.

## Features

- ✅ IMAP/SSL mail fetching
- ✅ Automatic attachment extraction
- ✅ Categorized file storage
- ✅ Structured logging
- ✅ Dry-run mode for testing
- ✅ Secure credential management

## Setup
bash
