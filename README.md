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

#### KI-gestützte Extraktion
- **OLLAMA-Integration**: Lokale KI-Verarbeitung (datenschutzkonform, kostenfrei)
- **3-fache JSON-Generierung**: 
  - **Problem-JSON**: Kompakt, suchoptimiert
  - **Solution-JSON**: Detailliert, wiederverwendbar
  - **Asset-JSON**: IT-System-Katalog
- **Prompt-Engineering**: Optimierte Prompts für präzise Extraktion
- **Schema-Validierung**: JSON-Schema-Templates für konsistente Datenstruktur

#### Qualitätssicherung & Fehlerbehandlung
- **Fehler-Tracking**: Fehlgeschlagene Extractions in `failed/` Ordner
- **Erfolgs-Archivierung**: Vollständige JSONs in `processed/`
- **Retry-Mechanismus**: Manuelle Nachbearbeitung möglich
- **Quality-Analyzer**: Erkennt fehlende/unklare Felder

#### Bestätigungsmails
- **Automatische Confirmation**: HTML-Mail mit extrahierten Daten
- **Qualitäts-Indikatoren**: Zeigt Vollständigkeit der Extraktion
- **Edit-Links**: Ermöglicht Nutzer-Korrekturen (vorbereitet)

### 🚧 In Entwicklung (Phase 2)

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

## 🏗️ Systemarchitektur

### 2-Schritt-Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     SCHRITT 1: run_agent.py                 │
│                     Mail Collection & Storage                │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   IMAP Mailbox   │
└────────┬─────────┘
         │ (IMAP/SSL)
         ▼
┌──────────────────┐
│   Mail Fetcher   │  ← Holt ungelesene Mails
│  - Connect       │
│  - Fetch         │
│  - Parse         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Storage: mails/  │  ← Speichert .eml Dateien
│  Attachments     │  ← Kategorisiert Anhänge
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ IMAP: processed/ │  ← Verschiebt Mail auf Server
└──────────────────┘


┌─────────────────────────────────────────────────────────────┐
│                   SCHRITT 2: run_extract.py                 │
│                   JSON Extraction & Classification           │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Storage: mails/  │  ← Liest alle .eml Dateien
│  (unprocessed)   │     (älteste zuerst)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────┐
│       OLLAMA LLM Engine          │  
│  - extract_problem.txt           │
│  - extract_solution.txt          │
│  - extract_asset.txt             │
│                                  │
│  Timeout: 300s (5 min)           │
└────────┬─────────────────────────┘
         │
         ├─── Erfolg (alle 3 JSONs) ────────────┐
         │                                       ▼
         │                            ┌──────────────────┐
         │                            │ processed/       │
         │                            │  - Mail (.eml)   │
         │                            │  - problem.json  │
         │                            │  - solution.json │
         │                            │  - asset.json    │
         │                            └──────────────────┘
         │
         └─── Fehler (Timeout/Parse) ───────────┐
                                                 ▼
                                      ┌──────────────────┐
                                      │ failed/          │
                                      │  - Mail (.eml)   │
                                      │  (manuelle       │
                                      │   Nacharbeit)    │
                                      └──────────────────┘
```

---

## 🚀 Quick Start

### Voraussetzungen

- **Python 3.8+**
- **OLLAMA** installiert und laufend
- **IMAP-fähiges E-Mail-Konto**
- **GPU empfohlen** für OLLAMA (CPU möglich, aber langsam)

### Installation

1. **Repository klonen**
```bash
git clone https://github.com/nincns/nice2know.git
cd nice2know
```

2. **Python Virtual Environment**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

3. **OLLAMA-Modell installieren**
```bash
# Empfohlen: llama3:8b (schnell, präzise)
ollama pull llama3:8b

# Alternative: llama3.2 (neuere Version)
ollama pull llama3.2:latest

# GPU-Check
ollama list
# Sollte zeigen: Modell läuft auf GPU, nicht CPU
```

4. **Konfiguration**
```bash
cd mail_agent

# Secrets erstellen
cp config/secrets.json.example config/secrets.json
nano config/secrets.json  # IMAP/SMTP Zugangsdaten eintragen

# Mail-Config anpassen
nano config/connections/mail_config.json  # Host/Port anpassen
```

5. **Verbindung testen**
```bash
python tests/test_mail.py  # Testet IMAP + SMTP

cd agents
python llm_request.py --test  # Testet OLLAMA
```

6. **Pipeline starten**
```bash
# Schritt 1: Mails holen
python run_agent.py

# Schritt 2: JSONs extrahieren
python run_extract.py
```

---

## 📋 Konfiguration

### config/secrets.json

```json
{
  "mail": {
    "imap_username": "support@example.com",
    "imap_password": "your-imap-password",
    "smtp_username": "support@example.com",
    "smtp_password": "your-smtp-password"
  },
  "llm": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "llama3:8b"
    }
  }
}
```

### config/connections/mail_config.json

```json
{
  "imap": {
    "host": "mail.example.com",
    "port": 993,
    "use_ssl": true,
    "mailbox": "INBOX"
  },
  "smtp": {
    "host": "mail.example.com",
    "port": 25,
    "use_ssl": false,
    "use_starttls": true,
    "from_address": "support@example.com",
    "from_name": "Nice2Know System"
  }
}
```

### config/connections/application.json

```json
{
  "app_name": "Nice2Know",
  "version": "1.0.0",
  "storage": {
    "base_path": "./storage",
    "max_attachment_size_mb": 50
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mail_agent.log"
  },
  "filters": {
    "mark_as_read": false,
    "move_to_processed": true,
    "processed_folder": "processed"
  }
}
```

---

## 📊 JSON-Datenstruktur

nice2know erzeugt **3 separate JSON-Strukturen** pro Support-Fall:

### 1. Problem JSON (Kompakt, suchoptimiert)

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_abc123...",
  "mail_id": "abc123...",
  "asset_id": "asset_outlook_eah_01",
  "timestamp": "2025-11-15T14:53:24Z",
  "reporter": {
    "name": "Max Mustermann",
    "email": "max@example.com",
    "department": "IT"
  },
  "problem": {
    "title": "Outlook Senden-Button fehlt",
    "description": "Menüband minimiert, Senden-Button nicht sichtbar",
    "symptoms": [
      "Senden-Button nicht sichtbar",
      "Menüband minimiert"
    ],
    "error_messages": [],
    "context": "Outlook Mail-Client"
  },
  "classification": {
    "category": "client",
    "severity": "medium",
    "affected_users": "single user"
  },
  "status": "resolved"
}
```

### 2. Solution JSON (Detailliert, wiederverwendbar)

```json
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
    ],
    "warnings": [],
    "alternatives": []
  },
  "metadata": {
    "complexity": "low",
    "estimated_time": "2 min",
    "success_rate": 1.0,
    "reusability_score": 0.8
  }
}
```

### 3. Asset JSON (IT-System-Katalog)

```json
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
    "description": "E-Mail-Client für Windows",
    "status": "active",
    "criticality": "medium"
  },
  "technical": {
    "software": "Microsoft Outlook",
    "version": "2021",
    "platform": "Windows",
    "deployment": "cloud"
  },
  "knowledge": {
    "known_problems": ["prob_abc123..."],
    "available_solutions": ["sol_xyz789..."],
    "total_incidents": 1
  }
}
```

---

## 🔧 Workflow

### Kompletter Durchlauf

```bash
# Schritt 1: Mails vom Server holen
python run_agent.py
# → Speichert .eml in storage/mails/
# → Extrahiert Attachments nach storage/attachments/
# → Verschiebt Mail auf Server in IMAP-Ordner "processed"

# Schritt 2: JSONs extrahieren (älteste zuerst)
python run_extract.py
# → Verarbeitet alle Mails in storage/mails/
# → Bei Erfolg: Mail + JSONs → storage/processed/
# → Bei Fehler: Mail → storage/failed/

# Optional: Nur neueste Mail
python run_extract.py --latest

# Optional: Max 5 Mails
python run_extract.py --limit 5
```

### Loop-Modus (Automatisierung)

```bash
# Agent läuft kontinuierlich (alle 60 Sekunden)
python run_agent.py --loop --interval 60

# In separatem Terminal: Extractor
watch -n 300 "cd /opt/nice2know/mail_agent && python run_extract.py"
# → Alle 5 Minuten neue Mails verarbeiten
```

### Dry-Run (Testen ohne Änderungen)

```bash
# Testet Mail-Abruf ohne Speichern
python run_agent.py --dry-run
```

---

## 📁 Projektstruktur

```
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
│   │   ├── json_store/              # JSON-Schema-Templates
│   │   │   ├── problem_schema.json  # ✅ Problem-Struktur
│   │   │   ├── solution_schema.json # ✅ Solution-Struktur
│   │   │   └── asset_schema.json    # ✅ Asset-Struktur
│   │   │
│   │   └── mail/                    # Mail-Templates
│   │       └── added_knowledge_mail.html  # ✅ Confirmation Mail
│   │
│   ├── config/                      # Konfiguration
│   │   ├── connections/             # Verbindungs-Configs
│   │   │   ├── mail_config.json     # IMAP/SMTP-Einstellungen
│   │   │   └── application.json     # App-Einstellungen
│   │   └── secrets.json             # Credentials (nicht in Git!)
│   │
│   ├── storage/                     # Dateisystem-Storage
│   │   ├── mails/                   # ⚙️  Unverarbeitete Mails
│   │   ├── processed/               # ✅ Erfolgreiche Extractions
│   │   ├── failed/                  # ❌ Fehlgeschlagene Extractions
│   │   └── attachments/             # Kategorisierte Anhänge
│   │       ├── images/              # Screenshots, Fotos
│   │       ├── documents/           # PDFs, Docs
│   │       └── logs/                # Log-Dateien
│   │
│   ├── utils/                       # Hilfsfunktionen
│   │   ├── logger.py                # Logging
│   │   ├── file_handler.py          # Datei-Ops
│   │   ├── credentials.py           # Credentials-Manager
│   │   └── analyze_json_quality.py  # ✅ Qualitäts-Analyse
│   │
│   ├── tests/                       # Test-Scripts
│   │   ├── test_mail.py             # ✅ Connection-Test
│   │   └── send_confirmation_mail.py # ✅ Bestätigungsmail-Test
│   │
│   ├── run_agent.py                 # ✅ Mail Collection
│   └── run_extract.py               # ✅ JSON Extraction
│
├── documents/                       # Projektdokumentation
│   ├── nice2know_json_schema_referenz.md
│   └── nice2know_projektplan.md
│
├── setup.sh                         # Environment-Setup
├── requirements.txt                 # Python-Dependencies
└── README.md                        # Diese Datei
```

---

## 🧪 Verwendungsbeispiele

### LLM Request (manuell)

```bash
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
```

### Bestätigungsmail senden

```bash
# Sendet HTML-Mail mit extrahierten Daten
python tests/send_confirmation_mail.py
# → Lädt neueste JSONs aus processed/
# → Analysiert Qualität
# → Sendet Bestätigungsmail an Reporter
```

---

## ⚡ Performance & Ressourcen

### OLLAMA GPU vs CPU

**GPU (empfohlen):**
- LLM-Extraktion: ~10-30 Sekunden pro Mail
- Timeout: 300 Sekunden (mehr als ausreichend)

**CPU (langsam):**
- LLM-Extraktion: 2-5 Minuten pro Mail
- Timeout-Risiko bei komplexen Mails
- → **Lösung**: OLLAMA mit GPU-Support neu installieren

### Ressourcen-Anforderungen

- **RAM**: 16GB+ empfohlen (für OLLAMA)
- **GPU**: NVIDIA mit 8GB+ VRAM (optional, aber stark empfohlen)
- **Disk**: 50GB+ (für Modelle und Anhänge)
- **CPU**: 4+ Cores

---

## 🗄️ Nächster Schritt: PostgreSQL-Migration

### Vorbereitung (bereits vorhanden)

Die Datenbank-Schemas sind dokumentiert:
- `documents/nice2know_json_schema_referenz.md`
- `documents/nice2know_projektplan.md`

### Geplante Tabellen

```sql
-- Problems
CREATE TABLE problems (
    problem_id VARCHAR(64) PRIMARY KEY,
    mail_id VARCHAR(64),
    asset_id VARCHAR(64),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Solutions
CREATE TABLE solutions (
    solution_id VARCHAR(64) PRIMARY KEY,
    problem_ids TEXT[],
    asset_id VARCHAR(64),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets
CREATE TABLE assets (
    asset_id VARCHAR(64) PRIMARY KEY,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 Erfolgsmetriken (Ziel)

- **Knowledge Capture**: >80% aller Support-E-Mails automatisch verarbeitet
- **Zeitersparnis**: 30% Reduktion bei wiederkehrenden Problemen
- **Lösungswiederverwendung**: 40% der Cases nutzen existierende Lösungen
- **Datenqualität**: <5% Extraktionsfehler

---

## 🔮 Roadmap

### ✅ Phase 1: Foundation (Abgeschlossen)
- [x] IMAP/SMTP Mail-Processing
- [x] OLLAMA-Integration
- [x] JSON-Generierung (Problem, Solution, Asset)
- [x] 2-Schritt-Pipeline (Collect → Extract)
- [x] Fehlerbehandlung (failed/ vs processed/)
- [x] Confirmation Mails mit Qualitäts-Indikatoren

### 🚧 Phase 2: Data Layer (Aktuell)
- [ ] PostgreSQL-Integration
- [ ] Attachment-Processing (OCR, PDF-Text)
- [ ] Case-JSON (Problem-Solution-Asset-Linking)
- [ ] REST-API (CRUD-Operationen)
- [ ] Full-Text-Suche

### 📋 Phase 3: User Interface
- [ ] Web-UI für Knowledge Base
- [ ] Automatische Lösungsvorschläge
- [ ] Metriken-Dashboard
- [ ] Continuous Learning (Feedback-Loop)

---

## 🐛 Troubleshooting

### OLLAMA läuft auf CPU statt GPU

```bash
# GPU-Status prüfen
nvidia-smi

# OLLAMA neu installieren mit GPU-Support
curl -fsSL https://ollama.ai/install.sh | sh

# Modell neu laden
ollama pull llama3:8b
ollama list  # Sollte GPU zeigen
```

### LLM-Timeout bei Extraktion

**Lösung 1**: Timeout erhöhen in `run_extract.py`
```python
extract_json(mail_path, json_type, output_dir, timeout=600)  # 10 Minuten
```

**Lösung 2**: Kleineres Modell verwenden
```bash
ollama pull llama3.2:3b  # Schneller, weniger präzise
```

**Lösung 3**: GPU aktivieren (siehe oben)

### IMAP-Verbindung schlägt fehl

```bash
# Test Connection
python tests/test_mail.py

# Häufige Ursachen:
# - Firewall blockiert Ports 993/587
# - Falsche Credentials in secrets.json
# - 2FA aktiviert (App-Passwort nötig)
```

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

## 📧 Support

Bei Fragen bitte GitHub Issue erstellen oder Kontakt aufnehmen.

---

**Status**: Active Development (Phase 2) 🚧  
**Aktuelle Version**: 1.0.0-beta  
**Letzte Aktualisierung**: 15. November 2025