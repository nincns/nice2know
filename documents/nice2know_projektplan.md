# nice2know - Project Plan

**Version:** 1.1  
**Date:** November 15, 2025  
**Status:** Concept Phase  

---

## 1. Executive Summary

**nice2know** is an intelligent knowledge management system that automatically transforms email-based support communication into a searchable, structured knowledge base. Through AI-powered analysis using local OLLAMA models, problems, solutions, and affected IT assets are extracted and persisted in a multi-dimensional JSON structure.

### Core Objectives
- Automatic extraction of support knowledge from email conversations
- Structured storage using Problem-Solution-Asset model
- Reusability of solutions across asset categories
- Reduction of processing times through knowledge transfer
- Privacy-compliant local AI processing

---

## 2. Project Description

### 2.1 Initial Situation
IT support departments receive daily support requests via email. These contain valuable knowledge about:
- Recurring problems with IT systems
- Proven solution approaches
- System-specific configurations
- Error diagnostics and workarounds

Currently, this knowledge is lost after ticket resolution or is only retrievable through email search.

### 2.2 Project Vision
**nice2know** transforms every support case into structured knowledge:

```
Email → AI Analysis → Structured Data → Knowledge Base → Faster Solutions
```

### 2.3 Value Proposition
1. **For Supporters:** Fast access to proven solutions
2. **For Assets:** Complete problem history per system
3. **For Organization:** Identification of systemic weaknesses
4. **For Onboarding:** New staff learn from real cases

### 2.4 Scope

#### In Scope
- Email import with attachment processing
- AI-based problem/solution extraction
- Asset identification and cataloging
- JSON export for database integration
- Linking of related cases
- Local OLLAMA integration for privacy

#### Out of Scope (Phase 1)
- Automatic ticket creation
- Real-time chat integration
- Predictive maintenance
- Automated solution suggestions during ticket processing

---

## 3. Data Flow Model

### 3.1 Overview

```
┌─────────────────┐
│   Email Box     │
│  (IMAP/API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mail Parser    │
│  - Headers      │
│  - Body         │
│  - Attachments  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     OLLAMA Processing Engine        │
│  ┌─────────────────────────────┐    │
│  │  1. Problem Extraction      │    │
│  │  2. Solution Identification │    │
│  │  3. Asset Recognition       │    │
│  │  4. Context Analysis        │    │
│  └─────────────────────────────┘    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     JSON Generator                  │
│  ┌──────────┬──────────┬─────────┐  │
│  │ Problem  │ Solution │  Asset  │  │
│  │   JSON   │   JSON   │  JSON   │  │
│  └──────────┴──────────┴─────────┘  │
│           │                         │
│           ▼                         │
│     ┌──────────┐                    │
│     │   Case   │                    │
│     │   JSON   │                    │
│     └──────────┘                    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    PostgreSQL Database (JSONB)      │
│  ┌─────────────────────────────┐    │
│  │  - Problems Table           │    │
│  │  - Solutions Table          │    │
│  │  - Assets Table             │    │
│  │  - Cases Table              │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### 3.2 Detailed Data Flow

#### Phase 1: Email Ingestion
```
Input: Email (MIME Format)
├── Headers (From, To, Subject, Date, Message-ID)
├── Body (Plain Text / HTML)
└── Attachments []
    ├── Screenshots (PNG, JPG) → OCR
    ├── Logs (TXT, LOG) → Text Extraction
    ├── Documents (PDF, DOCX) → Text Extraction
    └── Other → Store reference
```

#### Phase 2: OLLAMA Analysis
```
Input: Parsed Mail Content + Attachments
Process:
  1. Context Analysis (Which system? Which problem?)
  2. Problem Extraction (Symptoms, error messages, context)
  3. Solution Identification (Steps, outcome, validation)
  4. Asset Mapping (Which system is affected?)
  5. Categorization (Severity, type, reusability score)
Output: Structured Data (Pre-JSON)
```

#### Phase 3: JSON Generation
```
Input: Structured Data
Process:
  1. Generate Problem JSON (lightweight)
  2. Generate Solution JSON(s) (detailed, steps)
  3. Identify/Create Asset JSON (if new)
  4. Create Case JSON (linking)
  5. Validation (schema check, ID consistency)
Output: 3-4 JSON files per case
```

#### Phase 4: Persistence
```
Input: Validated JSONs
Process:
  1. Upsert Asset (if exists: update)
  2. Insert Problem
  3. Insert Solution(s)
  4. Insert Case (with references)
  5. Update Cross-References
Output: Database Records + IDs
```

### 3.3 Attachment Processing Strategy

| File Type | Processing | Storage Location | Integration |
|----------|-------------|------------------|-------------|
| PNG/JPG | OCR (Tesseract) | Object Storage | Text → Problem Context |
| PDF | Text Extraction | Object Storage | Separate KB Article or Problem Annex |
| TXT/LOG | Direct Parsing | Inline in JSON | Array in `error_messages` |
| DOCX | Text Extraction | Object Storage | Separate KB Article |
| Other | Metadata Only | Object Storage | Manual Review Flag |

---

## 4. System Architecture

### 4.1 Components

```
┌──────────────────────────────────────────────────────────┐
│                     nice2know System                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐        ┌──────────────────┐          │
│  │  Mail Fetcher  │───────▶│  Queue Manager   │          │
│  │  (IMAP/API)    │        │  (RabbitMQ)      │          │
│  └────────────────┘        └─────────┬────────┘          │
│                                       │                  │
│                                       ▼                  │
│                            ┌──────────────────┐          │
│                            │  Worker Pool     │          │
│                            │  - Mail Parser   │          │
│                            │  - OLLAMA Proc   │          │
│                            │  - JSON Gen      │          │
│                            └─────────┬────────┘          │
│                                      │                   │
│                                      ▼                   │
│  ┌──────────────────────────────────────────-──┐         │
│  │         Storage Layer                       │         │
│  ├──────────────────┬──────────────────────────┤         │
│  │  JSON Files      │   PostgreSQL DB          │         │
│  │  (Staging)       │   (JSONB Tables)         │         │
│  └──────────────────┴──────────────────────────┘         │
│                                                          │
│  ┌─────────────────────────────────────────-───┐         │
│  │         API Layer                           │         │
│  │  - REST API (CRUD Operations)               │         │
│  │  - Search API (Full-Text, Faceted)          │         │
│  │  - Analytics API (Metrics, Trends)          │         │
│  └─────────────────────────────────────────-───┘         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Technology Stack

| Layer | Technology | Rationale |
|-------|-------------|-----------|
| Mail Fetcher | Python + IMAPlib | Standard, robust |
| Queue | RabbitMQ | Reliable, open source |
| **AI Processing** | **OLLAMA (local)** | **Privacy, no costs, no rate limits** |
| Worker Pool | Python + Celery | Scalable, established |
| **Database** | **PostgreSQL + JSONB** | **Relational integrity + JSON flexibility** |
| Object Storage | MinIO / S3 | Attachments |
| API | FastAPI (Python) | Fast, modern async support |
| Frontend | React + TypeScript | (Optional, Phase 2) |

---

## 5. JSON Data Structure

### 5.1 Overview of JSON Types

nice2know uses **4 separate JSON structures** per support case:

1. **Problem JSON** - Lightweight, fast search
2. **Solution JSON** - Detailed, reusable
3. **Asset JSON** - IT systems catalog
4. **Case JSON** - Orchestration and linking

### 5.2 Versioning

All JSONs use semantic versioning:
```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem"
}
```

---

## 6. Problem JSON

### 6.1 Purpose
Captures the **problem statement** from the email in compact form. Optimized for fast full-text search and categorization.

### 6.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_0cb386ae2c684a53a69e8a4a786a298e",
  "mail_id": "0cb386ae-2c68-4a53-a69e-8a4a786a298e",
  "asset_id": "asset_mailsystem_01",
  "timestamp": "2025-11-15T10:35:57.424Z",
  "reporter": {
    "name": "John Smith",
    "email": "john.smith@company.com",
    "department": "IT Support"
  },
  "problem": {
    "title": "Mail system not accepting incoming emails",
    "description": "System rejects email acceptance. Senders receive bounce messages.",
    "symptoms": [
      "Incoming mails are rejected",
      "Mail history missing"
    ],
    "error_messages": [
      "SMTP 550 - Mailbox unavailable",
      "Local spam model blocking delivery"
    ],
    "affected_functionality": [
      "Email Reception",
      "Mail-to-Knowledge-System Integration"
    ]
  },
  "classification": {
    "category": "email",
    "subcategory": "incoming_mail",
    "severity": "high",
    "priority": "quick_win",
    "affected_users": "all",
    "business_impact": "critical"
  },
  "context": {
    "time_of_occurrence": "2025-11-15T11:35:00Z",
    "frequency": "continuous",
    "environment": "production",
    "related_changes": []
  },
  "status": "resolved",
  "resolution_date": "2025-11-15T14:20:00Z"
}
```

### 6.3 Key Descriptions

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `schema_version` | String | Yes | Version number of JSON schema |
| `type` | String | Yes | Always "n2k_problem" |
| `id` | String | Yes | Unique problem ID (prob_...) |
| `mail_id` | String | Yes | Reference to original email (from Email Message-ID) |
| `asset_id` | String | Yes | Reference to affected asset |
| `timestamp` | ISO8601 | Yes | Timestamp of problem report |
| `reporter.name` | String | Yes | Name of reporter |
| `reporter.email` | String | Yes | Email of reporter |
| `reporter.department` | String | No | Department (for statistics) |
| `problem.title` | String | Yes | Brief, concise problem description (max 200 chars) |
| `problem.description` | String | Yes | Detailed description |
| `problem.symptoms` | Array[String] | Yes | List of observable symptoms |
| `problem.error_messages` | Array[String] | No | Error messages (logs, screenshots via OCR) |
| `problem.affected_functionality` | Array[String] | No | Which functions are affected? |
| `classification.category` | Enum | Yes | Main category (see 6.4) |
| `classification.subcategory` | String | No | Fine-grained category |
| `classification.severity` | Enum | Yes | low, medium, high, critical |
| `classification.priority` | String | No | E.g., "quick_win" from original email |
| `classification.affected_users` | String | No | Number/group of affected users |
| `classification.business_impact` | Enum | No | low, medium, high, critical |
| `context.time_of_occurrence` | ISO8601 | No | When did the problem occur? |
| `context.frequency` | Enum | No | once, intermittent, continuous |
| `context.environment` | Enum | No | production, staging, development |
| `context.related_changes` | Array[String] | No | Recent changes to the system |
| `status` | Enum | Yes | open, in_progress, resolved, closed |
| `resolution_date` | ISO8601 | No | When was the problem solved? |

### 6.4 Categories (Enumerations)

#### category
```
- email (Email Systems)
- identity (LDAP, Active Directory, SSO)
- network (Switches, Firewalls, VPN)
- application (Business Apps, ERP, LMS)
- infrastructure (Server, Storage, Backup)
- client (Workstations, Mobile Devices)
- security (Malware, Access Issues)
- other
```

---

## 7. Solution JSON

### 7.1 Purpose
Documents **solution approaches** in reusable form. Can be applicable to multiple problems. Contains detailed step-by-step instructions.

### 7.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
  "problem_ids": [
    "prob_0cb386ae2c684a53a69e8a4a786a298e"
  ],
  "asset_id": "asset_mailsystem_01",
  "timestamp": "2025-11-15T14:20:00Z",
  "solution": {
    "title": "Enable email import to knowledge base",
    "type": "configuration",
    "approach": "workaround",
    "description": "Integration of mail system with knowledge base through import function. Normal mail flow remains intact, additionally conversations are automatically imported into knowledge database.",
    "prerequisites": [
      "Access to mail system configuration",
      "Knowledge base must be reachable",
      "API token for knowledge base"
    ],
    "steps": [
      {
        "step_number": 1,
        "action": "Configure knowledge base import API",
        "details": "Add API endpoint /api/import/mail in mail system config",
        "command": "echo 'KB_IMPORT_URL=https://kb.example.com/api/import/mail' >> /etc/mail/config.env",
        "expected_result": "Config file contains new variable",
        "estimated_duration": "2 min"
      },
      {
        "step_number": 2,
        "action": "Adjust mail routing",
        "details": "Forward incoming mails additionally to KB import",
        "command": null,
        "expected_result": "Mails are duplicated (normal delivery + KB import)",
        "estimated_duration": "5 min"
      },
      {
        "step_number": 3,
        "action": "Send test mail",
        "details": "Send test email to system and verify KB import",
        "command": null,
        "expected_result": "Mail appears in both mailbox and knowledge base",
        "estimated_duration": "3 min"
      }
    ],
    "validation": {
      "success_criteria": [
        "Mails are delivered regularly",
        "KB import runs automatically",
        "No errors in mail logs"
      ],
      "test_procedure": "Send test mail and search in KB after 5 minutes",
      "rollback_plan": "Remove import URL from config, restart mail service"
    },
    "outcome": {
      "tested": true,
      "successful": true,
      "side_effects": [
        "Additional storage consumption for KB data"
      ],
      "performance_impact": "minimal"
    }
  },
  "metadata": {
    "author": "Support Team",
    "source": "Support-Case 0cb386ae",
    "reusability_score": 0.85,
    "complexity": "low",
    "estimated_time": "10 min",
    "required_skills": [
      "Mail server administration",
      "Basic API integration knowledge"
    ]
  },
  "related_solutions": [],
  "tags": [
    "mail",
    "knowledge-base",
    "integration",
    "quick-win"
  ]
}
```

### 7.3 Key Descriptions

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `schema_version` | String | Yes | Version number of JSON schema |
| `type` | String | Yes | Always "n2k_solution" |
| `id` | String | Yes | Unique solution ID (sol_...) |
| `problem_ids` | Array[String] | Yes | List of all problems this solution addresses |
| `asset_id` | String | Yes | Asset for which this solution applies |
| `timestamp` | ISO8601 | Yes | Timestamp of solution documentation |
| `solution.title` | String | Yes | Concise solution title |
| `solution.type` | Enum | Yes | configuration, bugfix, workaround, update, other |
| `solution.approach` | Enum | Yes | permanent_fix, workaround, temporary |
| `solution.description` | String | Yes | Detailed description of solution |
| `solution.prerequisites` | Array[String] | No | What must be present/fulfilled? |
| `solution.steps` | Array[Object] | Yes | Step-by-step instructions (see 7.4) |
| `solution.validation.success_criteria` | Array[String] | No | How to recognize success? |
| `solution.validation.test_procedure` | String | No | How to test the solution? |
| `solution.validation.rollback_plan` | String | No | What to do if it goes wrong? |
| `solution.outcome.tested` | Boolean | Yes | Was the solution actually tested? |
| `solution.outcome.successful` | Boolean | No | Was the test successful? |
| `solution.outcome.side_effects` | Array[String] | No | Known side effects |
| `solution.outcome.performance_impact` | Enum | No | none, minimal, moderate, significant |
| `metadata.author` | String | No | Who documented the solution? |
| `metadata.source` | String | No | Where does the solution come from? |
| `metadata.reusability_score` | Float | No | 0.0-1.0, how reusable is the solution? |
| `metadata.complexity` | Enum | No | low, medium, high |
| `metadata.estimated_time` | String | No | Estimated implementation time |
| `metadata.required_skills` | Array[String] | No | Required skills |
| `related_solutions` | Array[String] | No | IDs of related solutions |
| `tags` | Array[String] | No | Free tags for search |

### 7.4 Step Object Structure

```json
{
  "step_number": 1,
  "action": "Brief description of action",
  "details": "Detailed explanation",
  "command": "Optional: Command to execute",
  "expected_result": "What should happen?",
  "estimated_duration": "Time estimate",
  "warnings": ["Optional warnings"]
}
```

---

## 8. Asset JSON

### 8.1 Purpose
Catalogs **IT assets** (systems, applications, infrastructure). Serves as link between problems and solutions. Enables asset-based analyses.

### 8.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_asset",
  "id": "asset_mailsystem_01",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T14:20:00Z",
  "asset": {
    "name": "Mail System",
    "display_name": "Central Email System",
    "description": "Organization-wide email system for staff and users",
    "type": "mail_infrastructure",
    "category": "communication",
    "status": "active",
    "criticality": "high"
  },
  "technical": {
    "software": "Postfix",
    "version": "3.7.2",
    "platform": "Linux (Ubuntu 22.04 LTS)",
    "architecture": "x86_64",
    "deployment": "on-premise",
    "vendor": "Open Source",
    "license": "IBM Public License"
  },
  "integrations": [
    {
      "name": "LDAP",
      "purpose": "User Authentication",
      "asset_id": "asset_ldap_01"
    },
    {
      "name": "Spam Filter",
      "purpose": "Mail Security",
      "asset_id": "asset_spamfilter_01"
    }
  ],
  "ownership": {
    "department": "IT Support",
    "primary_contact": "Support Team",
    "email": "it-support@company.com",
    "escalation_contact": null
  },
  "documentation": {
    "wiki_url": "https://wiki.company.com/mailsystem",
    "api_docs": null,
    "runbook": "https://docs.company.com/runbooks/mail",
    "architecture_diagram": null
  },
  "maintenance": {
    "last_update": "2025-10-01",
    "update_frequency": "quarterly",
    "backup_schedule": "daily",
    "monitoring": true,
    "sla": "99.5%"
  },
  "knowledge": {
    "known_problems": [
      "prob_0cb386ae2c684a53a69e8a4a786a298e"
    ],
    "available_solutions": [
      "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0"
    ],
    "total_incidents": 12,
    "mean_time_to_resolve": "45 min",
    "common_issues": [
      "Spam filter false positives",
      "LDAP sync problems"
    ]
  },
  "related_assets": [
    "asset_ldap_01",
    "asset_storage_mail_01",
    "asset_backup_system_01"
  ],
  "tags": [
    "email",
    "communication",
    "critical-infrastructure"
  ]
}
```

### 8.3 Asset Types

```
Categories:
- communication
- identity
- infrastructure
- application
- network
- security
- storage
- client

Types (Selection):
- mail_infrastructure
- ldap_service
- active_directory
- web_server
- database_server
- file_server
- backup_system
- firewall
- switch
- vpn_gateway
- erp_system
- lms_system (Learning Management)
- crm_system
- workstation
- mobile_device
```

---

## 9. Case JSON

### 9.1 Purpose
Orchestrates the **complete support case**. Links problem, solution(s), and asset. Documents the resolution path including alternatives.

### 9.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_case",
  "id": "case_0cb386ae2c684a53a69e8a4a786a298e",
  "mail_id": "0cb386ae-2c68-4a53-a69e-8a4a786a298e",
  "created_at": "2025-11-15T10:35:57.424Z",
  "resolved_at": "2025-11-15T14:20:00Z",
  "case": {
    "title": "Mail system import error",
    "status": "resolved",
    "priority": "high",
    "reporter": {
      "name": "John Smith",
      "email": "john.smith@company.com"
    }
  },
  "mail_metadata": {
    "subject": "Re: Mail System Problems",
    "from": "john.smith@company.com",
    "to": "it-support@company.com",
    "date": "2025-11-15T11:35:00Z",
    "thread_id": "thread_abc123",
    "has_attachments": false,
    "attachments": []
  },
  "entities": {
    "problem_id": "prob_0cb386ae2c684a53a69e8a4a786a298e",
    "asset_id": "asset_mailsystem_01",
    "applied_solution_id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
    "alternative_solutions": []
  },
  "resolution_path": [
    {
      "step": 1,
      "timestamp": "2025-11-15T11:40:00Z",
      "action": "Problem analyzed",
      "actor": "Support Staff",
      "notes": "SMTP logs show rejection due to missing KB import"
    },
    {
      "step": 2,
      "timestamp": "2025-11-15T13:00:00Z",
      "action": "Solution identified",
      "actor": "Support Staff",
      "solution_id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
      "notes": "Enable KB import as solution"
    },
    {
      "step": 3,
      "timestamp": "2025-11-15T14:10:00Z",
      "action": "Solution implemented",
      "actor": "Support Staff",
      "outcome": "success"
    },
    {
      "step": 4,
      "timestamp": "2025-11-15T14:20:00Z",
      "action": "Solution validated",
      "actor": "Support Staff",
      "outcome": "success",
      "notes": "Test mail successfully imported into KB"
    }
  ],
  "conversation_context": {
    "thread_messages": 3,
    "participants": [
      "john.smith@company.com",
      "it-support@company.com"
    ],
    "conversation_summary": "Mail system rejected mails. Cause: Missing KB import feature. Solution: KB import enabled."
  },
  "metrics": {
    "time_to_first_response": "5 min",
    "time_to_resolution": "3h 45min",
    "reopened": false,
    "satisfaction_score": null
  },
  "tags": [
    "mail",
    "quick-win",
    "configuration"
  ]
}
```

---

## 10. ID Conventions

### 10.1 ID Format

All IDs follow the schema: `{type}_{uuid}`

| Type | Prefix | Example |
|------|--------|----------|
| Problem | `prob_` | `prob_0cb386ae2c684a53a69e8a4a786a298e` |
| Solution | `sol_` | `sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0` |
| Asset | `asset_` | `asset_mailsystem_01` |
| Case | `case_` | `case_0cb386ae2c684a53a69e8a4a786a298e` |
| KB Article | `kb_art_` | `kb_art_001` |

### 10.2 ID Generation

- **Problem/Case**: Use email Message-ID (without special characters)
- **Solution**: UUID v4
- **Asset**: Manually assigned (speaking) or UUID for automatic creation

---

## 11. Database Schema

### 11.1 PostgreSQL Tables

```sql
-- Collection: problems
CREATE TABLE problems (
    id SERIAL PRIMARY KEY,
    problem_id VARCHAR(100) UNIQUE NOT NULL,
    mail_id VARCHAR(100) NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_problems_asset ON problems(asset_id);
CREATE INDEX idx_problems_mail ON problems(mail_id);
CREATE INDEX idx_problems_status ON problems((data->>'status'));
CREATE INDEX idx_problems_fulltext ON problems 
    USING GIN(to_tsvector('english', data->>'problem'));

-- Collection: solutions
CREATE TABLE solutions (
    id SERIAL PRIMARY KEY,
    solution_id VARCHAR(100) UNIQUE NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_solutions_asset ON solutions(asset_id);
CREATE INDEX idx_solutions_reusability ON solutions(
    (data->'metadata'->>'reusability_score')
);

-- Collection: assets
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(100) UNIQUE NOT NULL,
    asset_name VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_assets_type ON assets((data->'asset'->>'type'));
CREATE INDEX idx_assets_status ON assets((data->'asset'->>'status'));

-- Collection: cases
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

CREATE INDEX idx_cases_mail ON cases(mail_id);
CREATE INDEX idx_cases_status ON cases((data->'case'->>'status'));
```

---

## 12. Workflow & Processes

### 12.1 Standard Workflow

```
1. Email arrives
   ↓
2. Mail parser extracts data
   ↓
3. Queue: New job for OLLAMA worker
   ↓
4. OLLAMA worker analyzes email
   ├── Identifies problem
   ├── Identifies solution (if present)
   └── Identifies/Creates asset
   ↓
5. JSON generator creates 3-4 JSONs
   ↓
6. Validation (schema check)
   ↓
7. Storage in database
   ├── Problem → problems table
   ├── Solution → solutions table
   ├── Asset → assets table (upsert)
   └── Case → cases table
   ↓
8. Update cross-references
   ├── Asset.known_problems += problem_id
   └── Asset.available_solutions += solution_id
   ↓
9. Optional: Generate KB article
   ↓
10. Done ✓
```

### 12.2 Special Cases

#### Case 1: Email without solution
```
Problem is recorded, but:
- entities.applied_solution_id = null
- case.status = "open"
- No Solution JSON created
```

#### Case 2: Multiple solution attempts
```
- Multiple Solution JSONs (sol_1, sol_2, sol_3)
- resolution_path documents all attempts
- entities.applied_solution_id = most successful solution
- entities.alternative_solutions = [others]
```

#### Case 3: New asset
```
- Asset is automatically created
- Minimal data (name, type from OLLAMA analysis)
- ownership.department = "Unknown" → Manual review
- asset.status = "pending_verification"
```

#### Case 4: Email with attachments
```
- Attachments stored in object storage
- OCR/text extraction runs asynchronously
- mail_metadata.attachments populated
- Extracted text → problem.error_messages (if relevant)
```

---

## 13. API Endpoints

### 13.1 REST API

```
# Problems
GET    /api/v1/problems              # List all problems
GET    /api/v1/problems/{id}         # Specific problem
POST   /api/v1/problems              # Create new problem
PUT    /api/v1/problems/{id}         # Update problem
DELETE /api/v1/problems/{id}         # Delete problem

# Solutions
GET    /api/v1/solutions
GET    /api/v1/solutions/{id}
POST   /api/v1/solutions
PUT    /api/v1/solutions/{id}
DELETE /api/v1/solutions/{id}

# Assets
GET    /api/v1/assets
GET    /api/v1/assets/{id}
POST   /api/v1/assets
PUT    /api/v1/assets/{id}
DELETE /api/v1/assets/{id}

# Cases
GET    /api/v1/cases
GET    /api/v1/cases/{id}
POST   /api/v1/cases
PUT    /api/v1/cases/{id}
DELETE /api/v1/cases/{id}

# Search
GET    /api/v1/search?q={query}&type={problem|solution|asset}
GET    /api/v1/search/advanced       # Faceted search

# Analytics
GET    /api/v1/analytics/assets/{id}/problems     # All problems of an asset
GET    /api/v1/analytics/assets/{id}/solutions    # All solutions of an asset
GET    /api/v1/analytics/trends                   # Trend analyses
```

---

## 14. Milestones & Timeline

### Phase 1: Proof of Concept (4 weeks)
- **Week 1-2**: Infrastructure setup
  - Mail fetcher implementation
  - OLLAMA integration
  - Basic JSON generator
- **Week 3**: Database schema
  - PostgreSQL setup
  - Table design
  - Create indexes
- **Week 4**: Testing & iteration
  - Process 10 test emails
  - Evaluate JSON quality
  - Schema adjustments

### Phase 2: MVP (8 weeks)
- **Week 5-6**: Complete workflow
  - Queue system
  - Worker pool
  - Error handling
- **Week 7-8**: Attachment processing
  - OCR integration
  - Storage system
  - PDF extraction
- **Week 9-10**: API development
  - REST endpoints
  - Authentication
  - Documentation (OpenAPI)
- **Week 11-12**: Testing & optimization
  - Process 100+ emails
  - Performance tuning
  - Bug fixes

### Phase 3: Production (4 weeks)
- **Week 13**: Production deployment
- **Week 14-15**: Monitoring & fine-tuning
- **Week 16**: Documentation & training

---

## 15. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| OLLAMA extracts incorrect data | Medium | High | Human review flag for low confidence |
| Schema changes break compatibility | Low | High | Versioning, migration scripts |
| Email attachments too large | Medium | Medium | Size limit, compression |
| Data privacy concerns | Medium | High | Anonymization of personal data |
| OLLAMA performance issues | Medium | Medium | Model optimization, hardware upgrade |

---

## 16. Success Metrics

### KPIs (after 6 months)
- **Knowledge capture**: >80% of all support emails automatically processed
- **Time savings**: 30% reduction in time-to-resolution for recurring problems
- **Knowledge reuse**: 40% of cases use existing solutions
- **Data quality**: <5% extraction errors (measured by human review)
- **User adoption**: 70% of support staff actively use KB

---

## 17. Next Steps

1. **Review & approval**: Discuss project plan with stakeholders
2. **Technology evaluation**: Test OLLAMA model quality
3. **Resource planning**: Developers, servers, budget
4. **Proof of concept**: Manually process first 10 emails
5. **Iterative refinement**: Adjust JSON schema based on reality

---

## Appendix A: Example Data Flow

### Input: Support Email
```
From: john.smith@company.com
To: support@company.com
Subject: Mail system not accepting mails
Date: November 15, 2025, 11:35 AM

Hello team,

Our mail system is rejecting incoming emails.
Senders receive bounce messages with "SMTP 550".
The local spam model seems to be involved.

Suggestion: Enable knowledge base import so that
such cases are automatically captured.

Regards,
John
```

### Output: 4 JSON Files

1. **prob_0cb386ae...json** (Problem)
2. **sol_a7b9c3d4...json** (Solution)
3. **asset_mailsystem_01.json** (Asset, possibly update)
4. **case_0cb386ae...json** (Case)

*(Detailed JSONs see chapters 6-9)*

---

## Appendix B: Glossary

- **Asset**: IT system, application, or infrastructure component
- **Case**: A complete support case from report to solution
- **OLLAMA**: Local large language model framework
- **OCR**: Optical Character Recognition (text from images)
- **Reusability Score**: Rating of how often a solution can be reused
- **Resolution Path**: Chronological sequence of solution finding
- **Schema Version**: Version number of JSON format
- **UUID**: Universally Unique Identifier
- **JSONB**: PostgreSQL binary JSON data type

---

**Document Version**: 1.1  
**Last Update**: November 15, 2025  
**Next Review**: December 1, 2025