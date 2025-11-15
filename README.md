# nice2know - Intelligent Knowledge Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

**nice2know** is an intelligent knowledge management system that automatically transforms email-based support communication into a searchable, structured knowledge base. Using AI-powered analysis with local OLLAMA models, it extracts problems, solutions, and affected IT assets, storing them in a multi-dimensional JSON structure.

---

## 🎯 Key Features

- **Automatic Extraction**: Converts support emails into structured knowledge
- **Problem-Solution-Asset Model**: Organizes information by problems, solutions, and IT assets
- **Solution Reusability**: Share solutions across different asset categories
- **Local AI Processing**: Uses OLLAMA for privacy-compliant, cost-free AI analysis
- **PostgreSQL Backend**: Reliable data storage with JSONB support
- **Full-Text Search**: Fast retrieval of relevant knowledge
- **Cross-Reference System**: Link related cases, problems, and solutions

---

## 🏗️ Architecture


┌──────────────┐
│  Email Box   │
│  (IMAP/API)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Mail Parser  │
│  - Headers   │
│  - Body      │
│  - Attach    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    OLLAMA    │
│  Processing  │
│              │
│ 1. Problem   │
│ 2. Solution  │
│ 3. Asset     │
│ 4. Context   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     JSON     │
│  Generator   │
│              │
│ • Problem    │
│ • Solution   │
│ • Asset      │
│ • Case       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
│   (JSONB)    │
│              │
│ • Problems   │
│ • Solutions  │
│ • Assets     │
│ • Cases      │
└──────────────┘


---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 14+
- OLLAMA (installed and running)
- IMAP-enabled email account

### Installation

1. **Clone the repository**
bash
git clone https://github.com/yourusername/nice2know.git
cd nice2know


2. **Set up virtual environment**
bash
chmod +x install_env.sh
./install_env.sh
source venv/bin/activate


3. **Install OLLAMA models**
bash
ollama pull llama3:8b
# or
ollama pull stablelm2:12b


4. **Configure PostgreSQL**
bash
# Create database
createdb nice2know

# Run schema setup
psql nice2know < schema.sql


5. **Configure email settings**
bash
cp config_mail.json.example config_mail.json
# Edit config_mail.json with your IMAP/SMTP credentials


6. **Start the system**
bash
# Interactive menu mode
python3 mail_robot.py

# Automatic mode (runs continuously)
python3 mail_robot.py --automatic


---

## 📋 Configuration

### config_mail.json

json
{
    "imap": {
        "host": "mail.example.com",
        "port": 993,
        "username": "support@example.com",
        "password": "your_password",
        "mailbox_inbox": "INBOX",
        "mailbox_proceed": "Processed"
    },
    "smtp": {
        "host": "mail.example.com",
        "port": 587,
        "username": "support@example.com",
        "password": "your_password",
        "use_tls": true,
        "from_address": "support@example.com"
    }
}


### OLLAMA Configuration

Edit the model settings in the Python scripts:
- `analyze_and_match.py`: Line 8 - `MODEL_NAME = "llama3:8b"`
- `generate_and_send_replies.py`: Line 13 - `MODEL_NAME = "llama3:8b"`

---

## 📊 Data Structure

nice2know uses **4 separate JSON structures** per support case:

### 1. Problem JSON
Captures the problem statement in compact form, optimized for fast full-text search.

json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_abc123...",
  "mail_id": "abc123...",
  "asset_id": "asset_mailsystem_01",
  "problem": {
    "title": "Mail system not accepting incoming emails",
    "description": "System rejects emails with SMTP 550 error",
    "symptoms": ["Incoming mails rejected", "Bounce messages"],
    "error_messages": ["SMTP 550 - Mailbox unavailable"]
  },
  "classification": {
    "category": "email",
    "severity": "high",
    "priority": "quick_win"
  },
  "status": "resolved"
}


### 2. Solution JSON
Documents solution approaches in reusable form with step-by-step instructions.

json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_xyz789...",
  "problem_ids": ["prob_abc123..."],
  "asset_id": "asset_mailsystem_01",
  "solution": {
    "title": "Enable mail import to knowledge base",
    "type": "configuration",
    "approach": "workaround",
    "steps": [
      {
        "step_number": 1,
        "action": "Configure KB import API",
        "command": "echo 'KB_IMPORT_URL=...' >> config.env",
        "expected_result": "Config updated"
      }
    ]
  },
  "metadata": {
    "reusability_score": 0.85,
    "complexity": "low",
    "estimated_time": "10 min"
  }
}


### 3. Asset JSON
Catalogs IT assets (systems, applications, infrastructure).

json
{
  "schema_version": "1.0.0",
  "type": "n2k_asset",
  "id": "asset_mailsystem_01",
  "asset": {
    "name": "Mail System",
    "display_name": "Central Email System",
    "type": "mail_infrastructure",
    "status": "active",
    "criticality": "high"
  },
  "technical": {
    "software": "Postfix",
    "version": "3.7.2",
    "platform": "Linux (Ubuntu 22.04 LTS)"
  },
  "knowledge": {
    "known_problems": ["prob_abc123..."],
    "available_solutions": ["sol_xyz789..."],
    "total_incidents": 12
  }
}


### 4. Case JSON
Orchestrates the complete support case, linking problem, solution(s), and asset.

json
{
  "schema_version": "1.0.0",
  "type": "n2k_case",
  "id": "case_abc123...",
  "mail_id": "abc123...",
  "entities": {
    "problem_id": "prob_abc123...",
    "asset_id": "asset_mailsystem_01",
    "applied_solution_id": "sol_xyz789..."
  },
  "resolution_path": [
    {
      "step": 1,
      "timestamp": "2025-11-15T11:40:00Z",
      "action": "Problem analyzed",
      "outcome": "success"
    }
  ],
  "metrics": {
    "time_to_resolution": "3h 45min"
  }
}


---

## 🗄️ Database Schema

### PostgreSQL Tables

sql
-- Problems
CREATE TABLE problems (
    id SERIAL PRIMARY KEY,
    problem_id VARCHAR(100) UNIQUE NOT NULL,
    mail_id VARCHAR(100) NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Solutions
CREATE TABLE solutions (
    id SERIAL PRIMARY KEY,
    solution_id VARCHAR(100) UNIQUE NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(100) UNIQUE NOT NULL,
    asset_name VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cases
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(100) UNIQUE NOT NULL,
    mail_id VARCHAR(100) NOT NULL,
    problem_id VARCHAR(100) REFERENCES problems(problem_id),
    asset_id VARCHAR(100) REFERENCES assets(asset_id),
    applied_solution_id VARCHAR(100),
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);


---

## 🔧 Workflow

### Standard Processing Flow

1. **Email Arrival**: Fetch emails via IMAP
2. **Parsing**: Extract headers, body, attachments
3. **Queue Job**: Add to processing queue
4. **AI Analysis**: OLLAMA extracts problem, solution, asset
5. **JSON Generation**: Create 3-4 JSON documents
6. **Validation**: Schema and consistency checks
7. **Database Storage**: Insert into PostgreSQL
8. **Cross-Referencing**: Update asset knowledge links
9. **Optional**: Generate KB article

### Special Cases

- **Email without solution**: Problem recorded, case status = "open"
- **Multiple solution attempts**: Multiple solution JSONs, best one marked as applied
- **New asset**: Automatically created with minimal data, flagged for review
- **Email with attachments**: OCR/text extraction, stored in object storage

---

## 📁 Project Structure


nice2know/
├── analyze_and_match.py          # Email analysis and relevance matching
├── generate_and_send_replies.py  # Generate and send email responses
├── mail_robot.py                 # Main orchestration script
├── recieve_mail.py               # IMAP email fetcher
├── create_demo_sheets.py         # Generate demo product datasheets
├── config_mail.json              # Email configuration (not in repo)
├── prepromt_mail_analysis.txt    # Prompt for email analysis
├── prepromt_relevance_analysis.txt # Prompt for relevance matching
├── prepromt_mail_generation.txt  # Prompt for reply generation
├── pre_prompt_datasheet.txt      # Prompt for datasheet generation
├── requirements.txt              # Python dependencies
├── install_env.sh                # Environment setup script
├── schema.sql                    # PostgreSQL database schema
├── inbox/                        # Incoming emails (XML)
├── analyzed/                     # Analysis results
├── draft/                        # Match results
├── processed/                    # Processed emails
├── outbox/                       # Generated responses
├── send/                         # Sent responses
├── finished/                     # Completed cases
└── database/
    └── datasheets/               # Product/service data


---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔮 Roadmap

### Phase 1: Proof of Concept ✅
- [x] IMAP email fetcher
- [x] OLLAMA integration
- [x] Basic JSON generation
- [ ] PostgreSQL integration

### Phase 2: MVP
- [ ] Complete workflow automation
- [ ] Attachment processing (OCR)
- [ ] REST API
- [ ] Full-text search
- [ ] Web UI (optional)

### Phase 3: Production
- [ ] Performance optimization
- [ ] Monitoring & logging
- [ ] User documentation
- [ ] Automated testing

---

## 📊 Success Metrics

After 6 months of operation:
- **Knowledge Capture**: >80% of support emails automatically processed
- **Time Savings**: 30% reduction in time-to-resolution for recurring problems
- **Knowledge Reuse**: 40% of cases use existing solutions
- **Data Quality**: <5% extraction errors (measured by human review)
- **User Adoption**: 70% of support staff actively use KB

---

## ⚙️ Technical Requirements

- **Python**: 3.8 or higher
- **PostgreSQL**: 14 or higher
- **OLLAMA**: Latest version with at least one 8B+ parameter model
- **RAM**: 16GB recommended (for OLLAMA)
- **Disk**: 50GB+ (for models and attachments)

---

## 🐛 Troubleshooting

### OLLAMA not responding
bash
# Check if OLLAMA is running
curl http://localhost:11434/api/tags

# Restart OLLAMA
systemctl restart ollama


### Database connection errors
bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection
psql -h localhost -U username -d nice2know


### Email fetching issues
- Verify IMAP credentials in `config_mail.json`
- Check firewall rules for port 993 (IMAPS) and 587 (SMTP)
- Enable "Less secure app access" if using Gmail

---

## 📧 Support

For questions and support, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- OLLAMA team for the excellent local LLM framework
- PostgreSQL community for robust database technology
- All contributors to this project

---

**Made with ❤️ for better knowledge management**