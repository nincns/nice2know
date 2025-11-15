# nice2know

> Transform support emails into structured, searchable knowledge automatically.

**nice2know** is an intelligent knowledge management system that converts email-based support communication into a structured, multi-dimensional knowledge base using AI-powered analysis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/yourusername/nice2know)

---

## 🎯 What is nice2know?

nice2know automatically extracts structured knowledge from support emails by:

1. **Analyzing** email conversations using AI (LLM)
2. **Extracting** problems, solutions, and affected IT assets
3. **Structuring** information in a multi-dimensional JSON format
4. **Linking** related cases, problems, and solutions
5. **Building** a searchable knowledge base

### The Value Proposition

- 📧 **Automatic Knowledge Capture**: Every support email becomes structured knowledge
- 🔍 **Fast Problem Resolution**: Search previous solutions by symptom, error message, or asset
- 🔗 **Asset-Centric View**: See all problems and solutions for each IT system
- 📊 **Analytics Ready**: Track MTTR, common issues, and solution effectiveness
- 🎓 **Onboarding Tool**: New team members learn from real cases

---

## 🏗️ Architecture

```
┌─────────────┐
│   E-Mail    │
│   (IMAP)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Mail Parser │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ LLM Engine  │  ← Claude API
│ (Analysis)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│    JSON Generator               │
│  ┌─────────┬─────────┬────────┐ │
│  │ Problem │Solution │ Asset  │ │
│  └─────────┴─────────┴────────┘ │
│         └──────┬──────┘          │
│           ┌────▼────┐            │
│           │  Case   │            │
│           └─────────┘            │
└────────────────┬────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   Database    │
         │   (MongoDB)   │
         └───────────────┘
```

---

## 📦 Key Features

### 🤖 AI-Powered Extraction
- Automatic problem identification from email content
- Solution extraction with step-by-step procedures
- IT asset recognition and cataloging
- Context analysis (severity, frequency, impact)

### 🗂️ Multi-Dimensional Data Model
Four interconnected JSON structures:

1. **Problem JSON** - Lightweight problem descriptions
2. **Solution JSON** - Detailed, reusable solutions with validation
3. **Asset JSON** - IT asset catalog with problem/solution history
4. **Case JSON** - Complete support case orchestration

### 📎 Attachment Processing
- OCR for screenshots (extract error messages)
- Text extraction from PDFs and documents
- Log file parsing
- Automatic storage and indexing

### 🔗 Smart Linking
- Solutions can address multiple problems
- Assets maintain problem/solution history
- Cases track resolution paths including failed attempts
- Related asset dependencies

### 🔍 Search & Discovery
- Full-text search across all entities
- Asset-based filtering
- Tag-based discovery
- Severity and status filtering

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- IMAP-accessible email account
- Anthropic API key (for Claude)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nice2know.git
cd nice2know

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure
cp config.example.json config.json
# Edit config.json with your settings
```

### Configuration

Edit `config.json`:

```json
{
  "imap": {
    "host": "mail.example.com",
    "port": 993,
    "username": "support@example.com",
    "password": "your-password"
  },
  "llm": {
    "provider": "anthropic",
    "api_key": "your-api-key",
    "model": "claude-sonnet-4-20250514"
  },
  "database": {
    "uri": "mongodb://localhost:27017",
    "name": "nice2know"
  }
}
```

### Running

```bash
# Fetch and process emails
python mail_robot.py

# Or run in automatic mode (continuous processing)
python mail_robot.py --automatic

# Or use the interactive menu
python mail_robot.py
```

---

## 📖 Documentation

### Core Documentation

- **[Project Plan](docs/nice2know_projektplan.md)** - Complete project overview, architecture, and roadmap
- **[JSON Schema Reference](docs/nice2know_json_schema_referenz.md)** - Detailed documentation of all JSON keys and structures
- **[API Documentation](docs/api.md)** - REST API endpoints (coming soon)

### Data Structures

#### Example Problem JSON

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_abc123...",
  "asset_id": "asset_mailsystem_01",
  "problem": {
    "title": "Mail system rejects incoming emails",
    "symptoms": [
      "Incoming mails are rejected",
      "Bounce messages with SMTP 550"
    ],
    "error_messages": ["SMTP 550 - Mailbox unavailable"]
  },
  "classification": {
    "category": "email",
    "severity": "high"
  },
  "status": "resolved"
}
```

#### Example Solution JSON

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_xyz789...",
  "problem_ids": ["prob_abc123..."],
  "asset_id": "asset_mailsystem_01",
  "solution": {
    "title": "Enable Knowledge Base Import",
    "type": "configuration",
    "steps": [
      {
        "step_number": 1,
        "action": "Configure KB Import API",
        "command": "echo 'KB_URL=...' >> config",
        "expected_result": "Config contains new variable"
      }
    ]
  },
  "metadata": {
    "reusability_score": 0.85,
    "complexity": "low"
  }
}
```

See [JSON Schema Reference](docs/nice2know_json_schema_referenz.md) for complete documentation.

---

## 🛠️ Development

### Project Structure

```
nice2know/
├── docs/                           # Documentation
│   ├── nice2know_projektplan.md
│   └── nice2know_json_schema_referenz.md
├── src/
│   ├── mail/                       # Email processing
│   │   ├── fetcher.py             # IMAP mail fetching
│   │   └── parser.py              # Email parsing
│   ├── llm/                        # LLM integration
│   │   ├── analyzer.py            # Email analysis
│   │   └── extractor.py           # Entity extraction
│   ├── json/                       # JSON generation
│   │   ├── problem.py
│   │   ├── solution.py
│   │   ├── asset.py
│   │   └── case.py
│   ├── db/                         # Database layer
│   │   └── mongodb.py
│   └── api/                        # REST API (coming soon)
├── schemas/                        # JSON Schema files
│   ├── n2k_problem_v1.0.0.json
│   ├── n2k_solution_v1.0.0.json
│   ├── n2k_asset_v1.0.0.json
│   └── n2k_case_v1.0.0.json
├── tests/                          # Unit tests
├── config.example.json             # Example configuration
├── requirements.txt
├── mail_robot.py                   # Main entry point
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_mail_parser.py
```

### Code Style

We use:
- **Black** for code formatting
- **pylint** for linting
- **mypy** for type checking

```bash
# Format code
black src/

# Lint
pylint src/

# Type check
mypy src/
```

---

## 🔌 API (Coming Soon)

### Planned Endpoints

```
GET    /api/v1/problems              # List all problems
GET    /api/v1/problems/{id}         # Get specific problem
GET    /api/v1/solutions             # List all solutions
GET    /api/v1/assets                # List all assets
GET    /api/v1/assets/{id}/problems  # Get all problems for an asset
GET    /api/v1/search?q={query}      # Full-text search
```

---

## 🗺️ Roadmap

### Phase 1: Proof of Concept ✅
- [x] Basic email fetching
- [x] LLM integration (Ollama/Claude)
- [x] JSON structure design
- [ ] MongoDB integration
- [ ] Schema validation

### Phase 2: MVP (Current)
- [ ] Attachment processing (OCR, PDF extraction)
- [ ] Queue system for scalability
- [ ] Worker pool implementation
- [ ] REST API development
- [ ] Web UI (basic)

### Phase 3: Production
- [ ] Advanced search & filtering
- [ ] Analytics dashboard
- [ ] Auto-suggestion during ticket creation
- [ ] Multi-tenant support
- [ ] Integration with ticket systems

### Future Ideas
- [ ] Predictive maintenance recommendations
- [ ] Automated solution testing
- [ ] Knowledge graph visualization
- [ ] Slack/Teams integration
- [ ] Mobile app

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests before committing
pytest
```

---

## 📊 Use Cases

### For IT Support Teams
- **Faster Resolution**: Search for similar problems and proven solutions
- **Knowledge Retention**: Capture expert knowledge automatically
- **Onboarding**: New team members learn from historical cases

### For IT Management
- **Analytics**: Track MTTR, problem frequency, asset reliability
- **Capacity Planning**: Identify problematic systems requiring upgrade
- **Process Improvement**: Analyze common issues and root causes

### For Organizations
- **Compliance**: Document all incidents with full audit trail
- **Cost Reduction**: Reduce escalations through better knowledge sharing
- **Service Quality**: Consistent problem resolution across team

---

## 🏢 Enterprise Features (Planned)

- **SSO Integration** (SAML, OAuth)
- **Role-Based Access Control** (RBAC)
- **Multi-Tenant Architecture**
- **SLA Management**
- **Custom Workflows**
- **Advanced Analytics & Reporting**
- **API Rate Limiting**
- **High Availability Deployment**

---

## 🔐 Security & Privacy

### Data Protection
- **Email Storage**: Original emails stored encrypted at rest
- **Anonymization**: PII can be automatically redacted
- **Access Control**: Role-based access to sensitive information
- **Audit Trail**: All access and modifications logged

### API Security
- **Authentication**: API key or OAuth 2.0
- **Rate Limiting**: Prevent abuse
- **Input Validation**: All inputs sanitized and validated
- **HTTPS Only**: All communication encrypted

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for the Claude API
- **MongoDB** for the flexible document database
- **EAH Jena** - Servicezentrum Informatik for the initial use case
- All contributors and early adopters

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nice2know/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nice2know/discussions)
- **Email**: support@nice2know.example.com
- **Documentation**: [https://docs.nice2know.example.com](https://docs.nice2know.example.com)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/nice2know&type=Date)](https://star-history.com/#yourusername/nice2know&Date)

---

## 💡 Related Projects

- [ticket-to-know](https://github.com/example/ticket-to-know) - Similar concept for Jira tickets
- [kb-generator](https://github.com/example/kb-generator) - General KB article generator
- [support-analytics](https://github.com/example/support-analytics) - Support metrics dashboard

---

**Built with ❤️ by the nice2know team**

*Making support knowledge accessible, searchable, and reusable.*
