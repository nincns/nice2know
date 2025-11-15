#!/bin/bash
# ==============================================================================
# Nice2Know - Setup & Installation Script
# Sets up virtual environment and installs dependencies for mail_agent
# ==============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
REQUIREMENTS="$PROJECT_ROOT/requirements.txt"
MAIL_AGENT_DIR="$PROJECT_ROOT/mail_agent"

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}Nice2Know - Setup & Installation${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# ==============================================================================
# Check Python version
# ==============================================================================
echo -e "${BLUE}[1/5]${NC} Checking Python version..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "  Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}✗ Python 3.8+ required, found $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# ==============================================================================
# Check for requirements.txt
# ==============================================================================
echo -e "\n${BLUE}[2/5]${NC} Checking requirements.txt..."

if [ ! -f "$REQUIREMENTS" ]; then
    echo -e "${RED}✗ requirements.txt not found in $PROJECT_ROOT${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} requirements.txt found"

# ==============================================================================
# Create virtual environment
# ==============================================================================
echo -e "\n${BLUE}[3/5]${NC} Creating virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⊙${NC} Virtual environment already exists"
    read -p "  Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}  Removing old venv...${NC}"
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓${NC} Virtual environment recreated"
    else
        echo -e "${YELLOW}  Keeping existing venv${NC}"
    fi
else
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓${NC} Virtual environment created at $VENV_DIR"
fi

# ==============================================================================
# Activate virtual environment
# ==============================================================================
echo -e "\n${BLUE}[4/5]${NC} Activating virtual environment..."

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${RED}✗ Failed to find venv activation script${NC}"
    exit 1
fi

# ==============================================================================
# Install dependencies
# ==============================================================================
echo -e "\n${BLUE}[5/5]${NC} Installing Python dependencies..."

# Upgrade pip first
echo "  Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "  Installing packages from requirements.txt..."
pip install -r "$REQUIREMENTS"

echo -e "${GREEN}✓${NC} All dependencies installed"

# ==============================================================================
# Check mail_agent structure
# ==============================================================================
echo -e "\n${BLUE}Checking mail_agent structure...${NC}"

if [ ! -d "$MAIL_AGENT_DIR" ]; then
    echo -e "${YELLOW}⚠️  mail_agent directory not found${NC}"
    echo "  Run ./setup_mail_agent.sh first to create the structure"
else
    echo -e "${GREEN}✓${NC} mail_agent directory found"
    
    # Check for secrets.json
    if [ ! -f "$MAIL_AGENT_DIR/config/secrets.json" ]; then
        echo -e "${YELLOW}⚠️  secrets.json not configured${NC}"
        echo "  Next step: Configure credentials"
        echo "    cd mail_agent"
        echo "    cp config/secrets.json.example config/secrets.json"
        echo "    nano config/secrets.json"
    else
        echo -e "${GREEN}✓${NC} secrets.json configured"
    fi
fi

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "${BLUE}Virtual environment:${NC} $VENV_DIR"
echo -e "${BLUE}Python version:${NC}      $(python --version)"
echo -e "${BLUE}Pip version:${NC}         $(pip --version | cut -d' ' -f2)"
echo ""
echo -e "${BLUE}Installed packages:${NC}"
pip list | grep -E "(imapclient|pillow|psycopg2|python-dotenv|email-validator)" || echo "  (run 'pip list' to see all)"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Configure credentials:"
echo -e "     ${YELLOW}cd mail_agent${NC}"
echo -e "     ${YELLOW}cp config/secrets.json.example config/secrets.json${NC}"
echo -e "     ${YELLOW}nano config/secrets.json${NC}"
echo -e ""
echo -e "  2. Test SMTP connection:"
echo -e "     ${YELLOW}python mail_agent/test_mail.py${NC}"
echo -e ""
echo -e "  3. Run mail agent (dry-run):"
echo -e "     ${YELLOW}python mail_agent/run_agent.py --dry-run${NC}"
echo -e ""
echo -e "${BLUE}To activate venv manually:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
