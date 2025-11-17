# nice2know - Intelligent Knowledge Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active Development](https://img.shields.io/badge/Status-Active%20Development-green.svg)](https://github.com)

**nice2know** transformiert E-Mail-basierten IT-Support automatisch in eine durchsuchbare, strukturierte Wissensdatenbank. Mittels lokaler OLLAMA-KI werden aus Support-E-Mails Probleme, Lösungen und betroffene IT-Assets extrahiert und als JSON-Dokumente persistiert.

---

## 🎯 Aktueller Funktionsumfang

### ✅ Implementiert (Phase 1 - Foundation)

#### Mail-Processing Pipeline
- **IMAP Mail-Abruf**: Automatischer Empfang von E-Mails aus Postfach
- **Mail-Parsing**: Extraktion von Headers, Body und Metadaten
- **Anhang-Verwaltung**: Kategorisierte Speicherung (images/documents/logs)
- **Automatische Mail-Archivierung**: Verschiebt verarbeitete Mails in IMAP-Ordner
- **Zwei-Stufen-Workflow**: 
  - `run_agent.py`: Fetcht Mails von IMAP → `storage/mails/`
  - `run_extract.py`: Verarbeitet Mails durch OLLAMA → JSON-Generierung

#### KI-gestützte Extraktion
- **OLLAMA-Integration**: Lokale KI-Verarbeitung (datenschutzkonform, kostenfrei)
- **3-fache JSON-Generierung**: 
  - **Problem-JSON**: Kompakt, suchoptimiert
  - **Solution-JSON**: Detailliert, wiederverwendbar  
  - **Asset-JSON**: IT-System-Katalog
- **Prompt-Engineering**: Optimierte Prompts mit Demo-Daten für präzise Extraktion
- **Schema-Validierung**: JSON-Schema-Templates für konsistente Datenstruktur

#### Qualitätssicherung & Fehlerbehandlung
- **Fehler-Tracking**: Fehlgeschlagene Extractions in `failed/` Ordner
- **Erfolgs-Archivierung**: Vollständige JSONs in `processed/`
- **Retry-Mechanismus**: Manuelle Nachbearbeitung möglich
- **Quality-Analyzer**: 
  - Analysiert alle generierten JSONs auf Vollständigkeit
  - Erkennt fehlende Pflichtfelder
  - Identifiziert unklare Werte (z.B. "unknown", "n/a")
  - Berechnet Completeness-Score (0-100%)
  - Kategorisiert Felder nach "critical", "important", "optional"

#### Bestätigungsmails (v2)
- **Automatische Confirmation**: HTML-Mail mit allen extrahierten Daten
- **Qualitäts-Dashboard**: Zeigt Vollständigkeit (✓ complete, ⚠ missing, ❓ unclear)
- **Dreifach-Ansicht**: Problem, Solution, Asset in strukturierten Sektionen
- **Interaktive Links**: 
  - Edit-Link (Magic Link) zum Ergänzen fehlender Felder
  - Confirm-Link zur sofortigen Bestätigung
- **Fehlende-Felder-Liste**: Zeigt Anchor-Links zu allen unvollständigen Feldern
- **Template-Engine**: Chevron/Mustache für flexible HTML-Generierung
- **Error-Handling**: Fallback bei Mail-Versand-Fehlern

#### Konfigurationsmanagement
- **Dynamische Config-Loading**: Automatische Pfadauflösung basierend auf Script-Location
- **Einheitliche Config-Struktur**: `config/mail_config.json` und `config/secrets.json`
- **ZeroTier-Support**: Funktioniert über verschlüsselte Netzwerk-Verbindungen
- **Permission-Management**: Korrekte Berechtigungen für PHP/www-data-Zugriff

### 🚧 In Entwicklung (Phase 2)

- **PostgreSQL-Integration**: Schema vorhanden, Import-Funktionalität in Entwicklung
- **Magic-Link-Backend**: Web-Interface zum Editieren extrahierter Daten
- **Anhang-Analyse**: OCR und Textextraktion aus Bildern/PDFs
- **REST-API**: FastAPI für CRUD-Operationen
- **OLLAMA GPU-Acceleration**: Umstellung von CPU auf GPU zur Vermeidung von Timeouts

---

## 📂 Projektstruktur

```
nice2know/
├── mail_agent/
│   ├── agents/                          # ✅ Kernkomponenten
│   │   ├── imap_fetcher.py              # IMAP-Mail-Abruf
│   │   ├── mail_parser.py               # E-Mail-Parsing
│   │   ├── attachment_handler.py        # Anhang-Verwaltung
│   │   └── llm_request.py               # OLLAMA-Integration
│   │
│   ├── catalog/                         # ✅ Prompt- & Schema-Bibliothek
│   │   ├── prompts/
│   │   │   ├── extract_problem.txt      # Problem-Extraktion
│   │   │   ├── extract_solution.txt     # Solution-Extraktion
│   │   │   └── extract_asset.txt        # Asset-Identifikation
│   │   │
│   │   ├── json_store/                  # JSON-Schema-Templates
│   │   │   ├── problem_schema.json
│   │   │   ├── solution_schema.json
│   │   │   └── asset_schema.json
│   │   │
│   │   └── mail/                        # ✅ Mail-Templates
│   │       ├── added_knowledge_mail.html # Confirmation Mail Template
│   │       └── mail_variables.json       # Template-Variablen
│   │
│   ├── config/                          # ✅ Konfiguration
│   │   ├── mail_config.json             # IMAP/SMTP-Einstellungen
│   │   └── secrets.json                 # Credentials (gitignored)
│   │
│   ├── storage/                         # ✅ Dateisystem-Storage
│   │   ├── mails/                       # Roh-E-Mails (.eml)
│   │   ├── attachments/
│   │   │   ├── images/
│   │   │   ├── documents/
│   │   │   └── logs/
│   │   ├── processed/                   # ✅ Erfolgreiche JSONs
│   │   ├── failed/                      # ✅ Fehlgeschlagene Extractions
│   │   └── sent/                        # ✅ Archivierte verarbeitete Mails
│   │
│   ├── utils/                           # ✅ Hilfsfunktionen
│   │   ├── logger.py                    # Strukturiertes Logging
│   │   ├── file_handler.py              # Datei-Operationen
│   │   ├── credentials.py               # Secrets-Manager
│   │   └── quality_analyzer.py          # ✅ JSON-Qualitätsanalyse
│   │
│   ├── run_agent.py                     # ✅ Mail-Fetching
│   ├── run_extract.py                   # ✅ JSON-Extraktion
│   ├── run_send_response.py             # ✅ Confirmation Mails
│   └── test_mail.py                     # IMAP/SMTP-Test
│
├── documents/                           # 📚 Dokumentation
│   ├── nice2know_json_schema_referenz.md
│   └── nice2know_projektplan.md
│
├── setup.sh                             # Environment-Setup
├── requirements.txt                     # Python-Dependencies
└── README.md                            # Diese Datei
```

---

## 🚀 Installation & Setup

### Voraussetzungen

- **Python 3.8+**
- **OLLAMA** (lokal installiert, llama3:8b oder llama3.2:latest)
- **IMAP/SMTP Mail-Server** (Zugangsdaten erforderlich)
- Optional: **PostgreSQL 14+** (für Phase 2)

### Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/nice2know.git
cd nice2know

# Setup-Script ausführen
chmod +x setup.sh
./setup.sh

# Oder manuell:
cd mail_agent
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Konfiguration

#### 1. Mail-Konfiguration (`config/mail_config.json`)

```json
{
    "imap": {
        "server": "mail.example.com",
        "port": 993,
        "use_ssl": true,
        "mailbox": "INBOX"
    },
    "smtp": {
        "server": "mail.example.com",
        "port": 587,
        "use_starttls": true,
        "from_address": "support@example.com"
    }
}
```

#### 2. Zugangsdaten (`config/secrets.json`)

```json
{
    "imap": {
        "username": "your-email@example.com",
        "password": "your-password"
    },
    "smtp": {
        "username": "your-email@example.com",
        "password": "your-password"
    }
}
```

⚠️ **Wichtig:** `secrets.json` ist in `.gitignore` und wird NIE committet!

#### 3. OLLAMA-Check

```bash
# Prüfen ob OLLAMA läuft
curl http://localhost:11434/api/tags

# Modell laden (falls nicht vorhanden)
ollama pull llama3.2:latest
```

---

## 💻 Verwendung

### Standard-Workflow

```bash
# Schritt 1: Mails von IMAP abrufen
python run_agent.py

# Schritt 2: Mails durch OLLAMA verarbeiten
python run_extract.py

# Schritt 3: Confirmation-Mails versenden
python run_send_response.py
```

### Einzelne Komponenten testen

```bash
# IMAP/SMTP-Verbindung testen
python test_mail.py

# Einzelne Mail verarbeiten
python agents/llm_request.py \
  --pre_prompt catalog/prompts/extract_problem.txt \
  --mailbody storage/mails/test.eml \
  --json catalog/json_store/problem_schema.json \
  --export storage/processed/problem.json
```

---

## 📊 JSON-Schema-Übersicht

### Problem JSON

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_uuid...",
  "mail_id": "msg_uuid...",
  "problem": {
    "title": "Kurzbeschreibung",
    "description": "Detaillierte Beschreibung",
    "symptoms": ["Symptom 1", "Symptom 2"],
    "affected_users": "Anzahl betroffener Nutzer",
    "severity": "high",
    "frequency": "continuous"
  },
  "asset_id": "asset_uuid...",
  "status": "open"
}
```

### Solution JSON

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_uuid...",
  "problem_ids": ["prob_uuid..."],
  "solution": {
    "approach": "Lösungsansatz",
    "steps": ["Schritt 1", "Schritt 2"],
    "tools_used": ["Tool 1", "Tool 2"],
    "complexity": "medium",
    "effectiveness": "Beurteilung der Wirksamkeit"
  },
  "metadata": {
    "reusability_score": 0.8
  }
}
```

### Asset JSON

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_asset",
  "id": "asset_uuid...",
  "asset": {
    "name": "Microsoft Outlook",
    "description": "E-Mail-Client",
    "type": "mail_client",
    "category": "client",
    "status": "active",
    "criticality": "high"
  },
  "technical": {
    "software": "Microsoft Outlook",
    "version": "16.80",
    "platform": "macOS 14.5"
  }
}
```

---

## 🔍 Quality Analyzer

Der Quality Analyzer bewertet automatisch die Vollständigkeit aller generierten JSONs:

```python
from utils.quality_analyzer import QualityAnalyzer

analyzer = QualityAnalyzer()
quality = analyzer.analyze_json(json_data, json_type='problem')

# Ausgabe:
{
    'complete': ['title', 'description', 'severity'],
    'missing': ['affected_users', 'frequency'],
    'unclear': ['symptoms'],
    'summary': {
        'completeness_percent': 75.0,
        'complete_count': 3,
        'missing_count': 2,
        'unclear_count': 1,
        'critical_missing': 0
    }
}
```

**Erkennungsregeln:**
- **Missing**: Feld ist `null`, leerer String oder nicht vorhanden
- **Unclear**: Werte wie "unknown", "n/a", "not specified", "TBD"
- **Critical**: Pflichtfelder basierend auf JSON-Type

---

## 📧 Confirmation Mails

Nach erfolgreicher JSON-Generierung erhält der Absender eine HTML-Mail mit:

- **Quality Dashboard**: Zeigt Completeness-Score und fehlende Felder
- **Problem-Sektion**: Titel, Beschreibung, Symptome, Severity
- **Solution-Sektion**: Lösungsansatz, Schritte, Komplexität
- **Asset-Sektion**: Name, Typ, Kategorie, Technische Details
- **Edit-Link**: Magischer Link zum Ergänzen fehlender Daten
- **Confirm-Link**: Sofortige Bestätigung der Korrektheit

**Template-Location:** `catalog/mail/added_knowledge_mail.html`

---

## 🗄️ PostgreSQL-Integration (Coming Soon)

### Geplantes Schema

```sql
CREATE TABLE problems (
    id SERIAL PRIMARY KEY,
    problem_id VARCHAR(100) UNIQUE NOT NULL,
    mail_id VARCHAR(100) NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_problems_status ON problems((data->>'status'));
CREATE INDEX idx_problems_fulltext ON problems 
    USING GIN(to_tsvector('english', 
        COALESCE(data->'problem'->>'title', '') || ' ' ||
        COALESCE(data->'problem'->>'description', '')
    ));
```

---

## 🛠️ Technische Details

### OLLAMA-Parameter

```python
{
    "model": "llama3.2:latest",
    "temperature": 0.1,      # Deterministisch
    "top_p": 0.9,
    "format": "json",        # Erzwingt JSON-Output
    "stream": False
}
```

### Anhang-Kategorisierung

```python
{
    '.png, .jpg, .jpeg, .gif': 'images',
    '.pdf, .doc, .docx': 'documents',
    '.log, .txt': 'logs'
}
```

### Logging

- **Location**: `storage/logs/nice2know.log`
- **Format**: JSON-strukturiert mit Timestamps
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🔐 Sicherheit & Datenschutz

- ✅ **Lokale AI-Verarbeitung**: Keine Daten verlassen das System
- ✅ **Secrets-Management**: Credentials in gitignored `secrets.json`
- ✅ **SSL/TLS**: Verschlüsselte IMAP/SMTP-Verbindungen
- ✅ **File-Permissions**: Korrekte Berechtigungen für Multi-User-Umgebungen

---

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Committen (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Pull Request öffnen

---

## 📝 Roadmap

### Phase 2 (MVP) - In Arbeit

- [ ] PostgreSQL-Integration
- [ ] Magic-Link-Backend (PHP/Vue.js)
- [ ] OCR für Attachments
- [ ] REST-API (FastAPI)
- [ ] OLLAMA GPU-Optimization

### Phase 3 (Production)

- [ ] Web-Dashboard
- [ ] Multi-User-Support
- [ ] Advanced Search
- [ ] Analytics & Reporting
- [ ] Docker-Deployment

---

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

---

## 🙏 Danksagungen

- **OLLAMA** für die lokale LLM-Engine
- **Python-Community** für exzellente Mail-Libraries
- **EAH Jena** für den Use-Case und Testing

---

## 📧 Kontakt

**Projektverantwortlicher:** Steve Hentschke  
**Email:** steve.hentschke@eah-jena.de  
**GitHub:** [nice2know](https://github.com/yourusername/nice2know)

---

**Version:** 1.2  
**Letztes Update:** 17. November 2025  
**Status:** Phase 1 ✅ | Phase 2 🚧
