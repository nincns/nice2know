# nice2know - Intelligent Knowledge Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: PoC](https://img.shields.io/badge/Status-Proof%20of%20Concept-yellow.svg)](https://github.com)

**nice2know** transformiert E-Mail-basierten IT-Support automatisch in eine durchsuchbare, strukturierte Wissensdatenbank. Mittels lokaler OLLAMA-KI werden aus Support-E-Mails Probleme, Lösungen und betroffene IT-Assets extrahiert und als JSON-Dokumente persistiert.

---

## 🎯 Aktueller Funktionsumfang

### ✅ Implementiert (Phase 1 - Proof of Concept)

- **IMAP Mail-Abruf**: Automatischer Empfang von E-Mails aus Postfach
- **Mail-Parsing**: Extraktion von Headers, Body und Metadaten
- **Anhang-Verwaltung**: Kategorisierte Speicherung von E-Mail-Anhängen
- **OLLAMA-Integration**: Lokale KI-Verarbeitung (datenschutzkonform, kostenfrei)
- **JSON-Generierung**: 
  - Problem-JSON (kompakt, suchoptimiert)
  - Solution-JSON (detailliert, wiederverwendbar)
  - Asset-JSON (IT-System-Katalog)
- **Prompt-Engineering**: Optimierte Prompts für präzise Extraktion
- **Schema-Validierung**: JSON-Schema-Templates für konsistente Datenstruktur

### 🚧 In Entwicklung (Phase 2 - Vorbereitet)

- **PostgreSQL-Integration**: Schema vorhanden, Implementierung folgt
- **Anhang-Analyse**: OCR und Textextraktion aus Bildern/PDFs
- **Case-JSON**: Verknüpfung von Problem-Solution-Asset
- **Web-API**: REST-Endpunkte für CRUD-Operationen

### 📋 Geplant (Phase 3)

- Full-Text-Suche mit PostgreSQL
- Web-UI für Knowledge-Base-Zugriff
- Automatische Lösungsvorschläge
- Metriken und Auswertungen

---

## 🏗️ Systemarchitektur (Aktuell)


flowchart TD

    IMAP["IMAP Mailbox"] -->|IMAP/SSL| FETCHER

    subgraph FETCHER["Mail Fetcher"]
        F_PATH["mail_agent/agents/imap_fetcher.py"]
        F1[IMAP Connect]
        F2[Fetch Unseen]
    end

    FETCHER --> PARSER

    subgraph PARSER["Mail Parser"]
        P_PATH["mail_agent/agents/mail_parser.py"]
        P1[Headers]
        P2[Body (Text)]
        P3[Attachments]
    end

    PARSER --> ATTACH

    subgraph ATTACH["Attachment Store"]
        A_PATH["mail_agent/agents/attachment_handler.py"]
        A1[/images/]
        A2[/documents/]
        A3[/logs/]
    end

    ATTACH --> LLM

    subgraph LLM["OLLAMA LLM Engine"]
        L_PATH["mail_agent/agents/llm_request.py"]

        subgraph PROMPTS["Prompts"]
            PR1[extract_problem.txt]
            PR2[extract_solution.txt]
            PR3[extract_asset.txt]
        end

        subgraph SCHEMAS["Schemas"]
            S1[problem_schema.json]
            S2[solution_schema.json]
            S3[asset_schema.json]
        end
    end

    LLM --> JSONGEN

    subgraph JSONGEN["JSON Generator"]
        J1[Problem JSON]
        J2[Solution JSON]
        J3[Asset JSON]
    end

    JSONGEN --> STORAGE

    subgraph STORAGE["File Storage (Staging)"]
        ST_PATH["mail_agent/storage/processed/"]
        ST1[Next step: PostgreSQL (Work in Progress)]
    end

---

## 🚀 Quick Start

### Voraussetzungen

- Python 3.8+
- OLLAMA installiert und laufend
- IMAP-fähiges E-Mail-Konto

### Installation

1. **Repository klonen**
bash
git clone https://github.com/yourusername/nice2know.git
cd nice2know


2. **Python Virtual Environment**
bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate


3. **OLLAMA-Modell installieren**
bash
ollama pull llama3.2:latest
# oder alternatives Modell


4. **Konfiguration**
bash
cd mail_agent
cp config/secrets.json.example config/secrets.json
nano config/secrets.json  # Zugangsdaten eintragen


5. **Verbindung testen**
bash
python test_mail.py  # Testet IMAP + SMTP
python agents/llm_request.py --test  # Testet OLLAMA


6. **Mail Agent starten**
bash
python run_agent.py --dry-run  # Test ohne Speichern
python run_agent.py            # Produktivbetrieb


---

## 📋 Konfiguration

### config/secrets.json

json
{
  "imap": {
    "username": "support@example.com",
    "password": "your-password"
  },
  "llm": {
    "provider": "ollama",
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3.2:latest"
    }
  }
}


### config/mail_config.json

json
{
  "imap": {
    "host": "mail.example.com",
    "port": 993,
    "use_ssl": true,
    "mailbox": "INBOX"
  },
  "processing": {
    "fetch_limit": 50,
    "fetch_unseen_only": true,
    "save_raw_eml": true,
    "extract_attachments": true
  },
  "storage": {
    "base_path": "./storage",
    "max_attachment_size_mb": 50
  }
}


---

## 📊 JSON-Datenstruktur

nice2know erzeugt **3 separate JSON-Strukturen** pro Support-Fall:

### 1. Problem JSON (Kompakt, suchoptimiert)

json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_abc123...",
  "mail_id": "abc123...",
  "asset_id": "asset_outlook_eah_01",
  "timestamp": "2025-11-15T14:53:24Z",
  "reporter": {
    "name": "Max Mustermann",
    "email": "max@example.com"
  },
  "problem": {
    "title": "Outlook Senden-Button fehlt",
    "description": "Menüband minimiert, Senden-Button nicht sichtbar",
    "symptoms": [
      "Senden-Button nicht sichtbar",
      "Menüband minimiert"
    ],
    "error_messages": []
  },
  "classification": {
    "category": "client",
    "severity": "medium"
  },
  "status": "resolved"
}


### 2. Solution JSON (Detailliert, wiederverwendbar)

json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_xyz789...",
  "problem_ids": ["prob_abc123..."],
  "asset_id": "asset_outlook_eah_01",
  "timestamp": "2025-11-15T14:53:24Z",
  "solution": {
    "title": "Outlook Menüband wiederherstellen",
    "type": "configuration",
    "approach": "permanent_fix",
    "description": "Durch STRG+F1 wird das minimierte Menüband wiederhergestellt",
    "prerequisites": [],
    "steps": [
      {
        "step_number": 1,
        "action": "Menüband öffnen",
        "details": "STRG + F1 drücken oder Pfeil-Symbol klicken",
        "command": "STRG + F1",
        "expected_result": "Menüband wird sichtbar",
        "estimated_duration": "30 sec"
      }
    ]
  },
  "metadata": {
    "complexity": "low",
    "estimated_time": "2 min",
    "reusability_score": 0.8
  }
}


### 3. Asset JSON (IT-System-Katalog)

json
{
  "schema_version": "1.0.0",
  "type": "n2k_asset",
  "id": "asset_outlook_eah_01",
  "created_at": "2025-11-15T14:00:00Z",
  "updated_at": "2025-11-15T14:53:24Z",
  "asset": {
    "name": "Microsoft Outlook",
    "display_name": "Outlook Email Client",
    "type": "mail_client",
    "category": "client",
    "status": "active",
    "criticality": "medium"
  },
  "technical": {
    "software": "Microsoft Outlook",
    "platform": "Windows",
    "deployment": "cloud"
  },
  "knowledge": {
    "known_problems": ["prob_abc123..."],
    "available_solutions": ["sol_xyz789..."],
    "total_incidents": 1
  }
}


---

## 🔧 Workflow (Aktuell)


1. E-Mail empfangen (IMAP)
   ↓
2. Mail parsen (Header, Body, Anhänge)
   ↓
3. Anhänge kategorisiert speichern (/images, /documents, /logs)
   ↓
4. Mail-Body + System-Prompt an OLLAMA
   ↓
5. OLLAMA analysiert E-Mail:
   ├─ Problem extrahieren (extract_problem.txt)
   ├─ Lösung extrahieren (extract_solution.txt)
   └─ Asset identifizieren (extract_asset.txt)
   ↓
6. JSON-Generierung mit Schema-Validierung
   ↓
7. JSON-Dateien speichern (mail_agent/storage/processed/)
   ↓
8. [NÄCHSTER SCHRITT] PostgreSQL-Import 🚧


---

## 📁 Projektstruktur


nice2know/
├── mail_agent/                      # Haupt-Modul
│   ├── agents/                      # Kernkomponenten
│   │   ├── imap_fetcher.py          # ✅ IMAP-Mail-Abruf
│   │   ├── mail_parser.py           # ✅ E-Mail-Parsing
│   │   ├── attachment_handler.py    # ✅ Anhang-Verwaltung
│   │   └── llm_request.py           # ✅ OLLAMA-Integration
│   │
│   ├── catalog/                     # Prompt- und Schema-Bibliothek
│   │   ├── prompts/                 # LLM-Prompts
│   │   │   ├── extract_problem.txt  # ✅ Problem-Extraktion
│   │   │   ├── extract_solution.txt # ✅ Lösungs-Extraktion
│   │   │   └── extract_asset.txt    # ✅ Asset-Identifikation
│   │   │
│   │   └── json_store/              # JSON-Schema-Templates
│   │       ├── problem_schema.json  # ✅ Problem-Struktur
│   │       ├── solution_schema.json # ✅ Solution-Struktur
│   │       └── asset_schema.json    # ✅ Asset-Struktur
│   │
│   ├── config/                      # Konfiguration
│   │   ├── mail_config.json         # IMAP/SMTP-Einstellungen
│   │   └── secrets.json             # Credentials (nicht in Git!)
│   │
│   ├── storage/                     # Dateisystem-Storage
│   │   ├── mails/                   # Roh-E-Mails (.eml)
│   │   ├── attachments/             # Kategorisierte Anhänge
│   │   │   ├── images/              # Screenshots, Fotos
│   │   │   ├── documents/           # PDFs, Docs
│   │   │   └── logs/                # Log-Dateien
│   │   └── processed/               # ✅ Generierte JSONs
│   │
│   ├── utils/                       # Hilfsfunktionen
│   │   ├── logger.py                # Logging
│   │   ├── file_handler.py          # Datei-Ops
│   │   └── credentials.py           # Credentials-Manager
│   │
│   ├── run_agent.py                 # ✅ Hauptprogramm
│   └── test_mail.py                 # ✅ Connection-Test
│
├── documents/                       # Projektdokumentation
│   ├── nice2know_json_schema_referenz.md  # JSON-Schema-Doku
│   └── nice2know_projektplan.md           # Projektplan
│
├── setup.sh                         # Python-Environment-Setup
├── requirements.txt                 # Python-Dependencies
└── README.md                        # Diese Datei


---

## 🧪 Verwendungsbeispiele

### LLM Request (manuell)

bash
# Problem aus E-Mail extrahieren
python agents/llm_request.py \
  --pre_prompt catalog/prompts/extract_problem.txt \
  --mailbody storage/mails/test.eml \
  --json catalog/json_store/problem_schema.json \
  --export storage/processed/problem.json

# Solution extrahieren
python agents/llm_request.py \
  --pre_prompt catalog/prompts/extract_solution.txt \
  --mailbody storage/mails/test.eml \
  --json catalog/json_store/solution_schema.json \
  --export storage/processed/solution.json

# Asset identifizieren
python agents/llm_request.py \
  --pre_prompt catalog/prompts/extract_asset.txt \
  --mailbody storage/mails/test.eml \
  --json catalog/json_store/asset_schema.json \
  --export storage/processed/asset.json


### Mail Agent (automatisiert)

bash
# Dry-Run (nichts speichern)
python run_agent.py --dry-run

# Produktivbetrieb (1x ausführen)
python run_agent.py

# Loop-Modus (alle 60 Sekunden)
python run_agent.py --loop --interval 60


---

## 🗄️ Nächster Schritt: PostgreSQL-Migration

### Vorbereitung (bereits vorhanden)

Die Datenbank-Schemas sind bereits dokumentiert:
- `documents/nice2know_json_schema_referenz.md` (Detaillierte Feldbeschreibungen)
- `documents/nice2know_projektplan.md` (CREATE TABLE Statements)

### Migration Script (geplant)

python
# Pseudo-Code für PostgreSQL-Import
import psycopg2
import json

def import_json_to_postgres(json_file, table_name):
    """Import JSON from staging into PostgreSQL JSONB"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    if table_name == 'problems':
        cur.execute("""
            INSERT INTO problems (problem_id, mail_id, asset_id, data)
            VALUES (%s, %s, %s, %s)
        """, (data['id'], data['mail_id'], data['asset_id'], json.dumps(data)))
    
    conn.commit()


---

## 📊 Erfolgsmetriken (Ziel nach 6 Monaten)

- **Knowledge Capture**: >80% aller Support-E-Mails automatisch verarbeitet
- **Zeitersparnis**: 30% Reduktion bei wiederkehrenden Problemen
- **Lösungswiederverwendung**: 40% der Cases nutzen existierende Lösungen
- **Datenqualität**: <5% Extraktionsfehler (gemessen durch Human Review)

---

## 🔮 Roadmap

### ✅ Phase 1: Proof of Concept (Abgeschlossen)
- [x] IMAP E-Mail Fetcher
- [x] Mail-Parsing (Headers, Body, Attachments)
- [x] OLLAMA-Integration
- [x] JSON-Generierung (Problem, Solution, Asset)
- [x] Prompt-Engineering
- [x] Schema-Validierung

### 🚧 Phase 2: MVP (In Arbeit)
- [ ] **PostgreSQL-Integration** (nächster Sprint)
- [ ] Attachment-Processing (OCR, PDF-Text-Extraktion)
- [ ] Case-JSON-Generierung (Problem-Solution-Asset-Linking)
- [ ] REST-API (CRUD-Operationen)
- [ ] Full-Text-Suche

### 📋 Phase 3: Production (Geplant)
- [ ] Web-UI für Knowledge Base
- [ ] Automatische Lösungsvorschläge
- [ ] Metriken-Dashboard
- [ ] Continuous Learning (Feedback-Loop)

---

## 🤝 Beitragen

Contributions sind willkommen! Bitte Fork + Pull Request.

---

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 🙏 Danksagungen

- **OLLAMA Team** für das exzellente lokale LLM-Framework
- **PostgreSQL Community** für robuste Datenbank-Technologie
- Allen Contributors dieses Projekts

---

## ⚙️ Technische Anforderungen

- **Python**: 3.8+
- **OLLAMA**: Latest version mit mind. 8B-Parameter-Modell
- **RAM**: 16GB empfohlen (für OLLAMA)
- **Disk**: 50GB+ (für Modelle und Anhänge)
- **PostgreSQL**: 14+ (für Phase 2)

---

## 📧 Support

Bei Fragen bitte GitHub Issue erstellen.

---

**Status**: Proof of Concept (Phase 1) ✅  
**Nächster Meilenstein**: PostgreSQL-Integration 🚧  
**Letzte Aktualisierung**: 15. November 2025