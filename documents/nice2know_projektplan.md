# nice2know - Projektplan (Aktualisiert)

**Version:** 1.3  
**Datum:** 17. November 2025  
**Status:** Phase 1 (Proof of Concept) ✅ Abgeschlossen | Phase 2 (MVP) 🚧 In Arbeit

---

## 1. Executive Summary

**nice2know** ist ein intelligentes Knowledge-Management-System, das E-Mail-basierten IT-Support automatisch in eine durchsuchbare, strukturierte Wissensdatenbank transformiert. Mittels lokaler OLLAMA-KI-Analyse werden Probleme, Lösungen und betroffene IT-Assets aus E-Mails extrahiert und als JSON-Dokumente persistiert.

### Projektstatus (Stand: 17.11.2025)

**Phase 1 (PoC) ist abgeschlossen:**
- ✅ IMAP-Mail-Abruf implementiert
- ✅ Mail-Parsing (Headers, Body, Attachments)
- ✅ OLLAMA-Integration funktionsfähig
- ✅ JSON-Generierung für Problem, Solution, Asset
- ✅ Prompt-Engineering und Schema-Validierung
- ✅ Quality-Analyzer für JSON-Qualitätsprüfung
- ✅ Confirmation-Mail-System mit HTML-Templates
- ✅ Zwei-Stufen-Workflow (Fetch + Extract)

**Phase 2 (MVP) startet:**
- 🚧 PostgreSQL-Integration steht an
- 📋 Magic-Link-Backend für Web-Editing
- 📋 Attachment-Analyse (OCR/PDF) geplant
- 📋 REST-API in Planung

---

## 2. Architektur-Übersicht (Aktueller Stand)

### 2.1 Implementierte Komponenten

```
┌─────────────────────────────────────────────────────────────────┐
│                    nice2know System (Phase 1 Complete)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐         ┌──────────────────┐                  │
│  │ run_agent.py │────────▶│  IMAP Fetcher    │                  │
│  │ (Step 1)     │         │  - Fetch mails   │                  │
│  │ ✅ Fertig    │         │  - Save to /mails│                  │
│  └──────────────┘         │  ✅ Fertig       │                  │
│                           └────────┬─────────┘                  │
│                                    │                            │
│                                    ▼                            │
│  ┌──────────────┐         ┌──────────────────┐                  │
│  │run_extract.py│────────▶│  Mail Parser     │                  │
│  │ (Step 2)     │         │  - Headers       │                  │
│  │ ✅ Fertig    │         │  - Body          │                  │
│  └──────────────┘         │  - Attachments   │                  │
│                           │  ✅ Fertig       │                  │
│                           └────────┬─────────┘                  │
│                                    │                            │
│                                    ▼                            │
│                           ┌──────────────────┐                  │
│                           │ Attachment Store │                  │
│                           │  /images/        │                  │
│                           │  /documents/     │                  │
│                           │  /logs/          │                  │
│                           │  ✅ Fertig       │                  │
│                           └────────┬─────────┘                  │
│                                    │                            │
│                                    ▼                            │
│               ┌───────────────────────────────────┐             │
│               │      OLLAMA LLM Engine            │             │
│               │      (Local AI Processing)        │             │
│               │                                   │             │
│               │  Prompts (✅ Fertig):             │             │
│               │  ├─ extract_problem.txt           │             │
│               │  ├─ extract_solution.txt          │             │
│               │  └─ extract_asset.txt             │             │
│               │                                   │             │
│               │  Schemas (✅ Fertig):             │             │
│               │  ├─ problem_schema.json           │             │
│               │  ├─ solution_schema.json          │             │
│               │  └─ asset_schema.json             │             │
│               └────────┬──────────────────────────┘             │
│                        │                                        │
│                        ▼                                        │
│               ┌──────────────────┐                              │
│               │  JSON Generator  │                              │
│               │  ✅ Fertig       │                              │
│               │                  │                              │
│               │  • Problem JSON  │                              │
│               │  • Solution JSON │                              │
│               │  • Asset JSON    │                              │
│               └────────┬─────────┘                              │
│                        │                                        │
│                        ▼                                        │
│               ┌──────────────────┐                              │
│               │ Quality Analyzer │───┐                          │
│               │  ✅ NEW!         │   │                          │
│               │                  │   │                          │
│               │ • Complete fields│   │                          │
│               │ • Missing fields │   │                          │
│               │ • Unclear values │   │                          │
│               │ • Score 0-100%   │   │                          │
│               └────────┬─────────┘   │                          │
│                        │             │                          │
│                        ▼             ▼                          │
│               ┌────────────────────────────┐                    │
│               │  File Storage              │                    │
│               │  ✅ Fertig                 │                    │
│               │                            │                    │
│               │  /processed/ ─────────────┐│                    │
│               │    (success JSONs)        ││                    │
│               │  /failed/                 ││                    │
│               │    (failed extractions)   ││                    │
│               │  /sent/  ✅ NEW!          ││                    │
│               │    (archived mails)       ││                    │
│               └───────────────────────────┘│                    │
│                                            │                    │
│                                            ▼                    │
│  ┌────────────────┐         ┌────────────────────────┐         │
│  │run_send_       │────────▶│ Confirmation Mail      │         │
│  │response.py     │         │  ✅ NEW v2!            │         │
│  │ (Step 3)       │         │                        │         │
│  │ ✅ Fertig      │         │ • HTML Template        │         │
│  └────────────────┘         │ • Quality Dashboard    │         │
│                             │ • Missing Fields List  │         │
│                             │ • Magic Links (prep.)  │         │
│                             │ • Confirmation Links   │         │
│                             └────────────────────────┘         │
│                                                                 │
│  Future: PostgreSQL Database (Phase 2) 📋                      │
│  ┌──────────────────────────────────────────────┐              │
│  │  problems | solutions | assets | cases       │              │
│  │  JSONB columns + GIN indexes                 │              │
│  └──────────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Workflow-Übersicht (Zwei-Stufen-Modell)

```
Stufe 1: Mail Fetching
┌──────────────────────────────────────────────────────────────┐
│ $ python run_agent.py                                        │
│                                                              │
│ 1. Connect to IMAP                                           │
│ 2. Fetch unread mails from INBOX                             │
│ 3. Save as .eml files → storage/mails/                       │
│ 4. Mark as read (optional)                                   │
│ 5. Close connection                                          │
└──────────────────────────────────────────────────────────────┘
                              ▼
Stufe 2: JSON Extraction
┌──────────────────────────────────────────────────────────────┐
│ $ python run_extract.py                                      │
│                                                              │
│ 1. Load .eml files from storage/mails/                       │
│ 2. Parse mail (headers, body, attachments)                   │
│ 3. Send to OLLAMA (3x prompts)                               │
│ 4. Generate Problem/Solution/Asset JSON                      │
│ 5. Validate & Save → storage/processed/                      │
│ 6. On error → storage/failed/                                │
└──────────────────────────────────────────────────────────────┘
                              ▼
Stufe 3: Quality Check & Confirmation
┌──────────────────────────────────────────────────────────────┐
│ $ python run_send_response.py <timestamp>                    │
│                                                              │
│ 1. Load JSONs from storage/processed/<timestamp>_*          │
│ 2. Run Quality Analyzer                                      │
│    - Identify complete/missing/unclear fields                │
│    - Calculate completeness score                            │
│ 3. Load HTML template                                        │
│ 4. Fill template with data + quality metrics                 │
│ 5. Send confirmation mail to reporter                        │
│ 6. Move mail to storage/sent/                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Neue Features (seit letztem Update)

### 4.1 Quality Analyzer (✅ NEU)

**Datei:** `mail_agent/utils/analyze_json_quality.py`

**Funktionalität:**
- Analysiert alle generierten JSONs auf Vollständigkeit
- Kategorisiert Felder in:
  - **Complete** ✓: Feld hat gültigen Wert
  - **Missing** ⚠: Feld ist null, leer oder fehlt
  - **Unclear** ❓: Wert ist generisch ("unknown", "n/a", "TBD")
- Berechnet Completeness-Score (0-100%)
- Unterscheidet nach Feld-Wichtigkeit:
  - **Critical**: Pflichtfelder (title, description)
  - **Important**: Wichtige Felder (severity, affected_users)
  - **Optional**: Nice-to-have (department, version)

**Output-Struktur:**
```python
{
    'complete': ['problem_title', 'problem_description', 'severity'],
    'missing': ['affected_users', 'reporter_department'],
    'unclear': ['symptoms'],
    'summary': {
        'completeness_percent': 75.0,
        'complete_count': 8,
        'missing_count': 3,
        'unclear_count': 1,
        'critical_missing': 0
    }
}
```

**Erkennungsregeln:**
- **Missing**: `null`, `""`, nicht vorhanden, leere Arrays
- **Unclear**: `"unknown"`, `"n/a"`, `"not specified"`, `"TBD"`, `"unclear"`, `"keine Angabe"`

---

### 4.2 Confirmation Mail System v2 (✅ NEU)

**Datei:** `mail_agent/run_send_response.py`

**Features:**
1. **HTML-Template-Engine** (Chevron/Mustache-ähnlich)
   - Template: `catalog/mail/added_knowledge_mail.html`
   - Variablen: `{{reporter_name}}`, `{{QUALITY_SUMMARY}}`, etc.

2. **Quality Dashboard**
   - Zeigt Completeness-Score prominent
   - Statistik: ✓ Complete, ⚠ Missing, ❓ Unclear
   - Fehlende-Felder-Liste mit Anchor-Links

3. **Dreifach-Ansicht** (Problem/Solution/Asset)
   - Jede Sektion hat eigene Farbe & Icon
   - Felder sind visuell markiert (✓/⚠/❓)
   - Klickbare Anchor-Links zu Feldern

4. **Interaktive Links**
   - **Edit-Link** (Magic Link): `https://domain.com/edit?token=...`
   - **Confirm-Link**: Sofortige Bestätigung ohne Änderungen
   - Links sind vorbereitet, Backend folgt in Phase 2

5. **Mail Archivierung**
   - Nach erfolgreichem Versand → `storage/sent/`
   - Verhindert Doppel-Verarbeitung

**Verwendung:**
```bash
# Sende Confirmation für Zeitstempel
python run_send_response.py 20251117_143052

# Script findet automatisch:
# - storage/processed/20251117_143052_problem.json
# - storage/processed/20251117_143052_solution.json
# - storage/processed/20251117_143052_asset.json
# - storage/mails/20251117_143052.eml
```

---

### 4.3 Konfigurationsmanagement (✅ VERBESSERT)

**Änderung:** Dynamische Pfadauflösung

**Problem vorher:**
- Hardcoded Paths: `/opt/nice2know/mail_agent/...`
- Funktioniert nicht bei lokalem Development
- Fehler bei unterschiedlichen Installationen

**Lösung:**
```python
def find_mail_agent_root(start_path: Path) -> Path:
    """Find mail_agent root by looking for key directories"""
    current = start_path
    for _ in range(5):
        if (current / 'agents').exists() and \
           (current / 'catalog').exists() and \
           (current / 'config').exists():
            return current
        if current.parent != current:
            current = current.parent
    return start_path

WORKING_DIR = find_mail_agent_root(Path(__file__).resolve().parent)
```

**Vorteil:**
- Funktioniert sowohl lokal als auch auf Server
- Keine manuellen Pfad-Anpassungen nötig
- Automatische Erkennung der Projektstruktur

---

### 4.4 Dateistruktur (Aktualisiert)

```
nice2know/
├── mail_agent/
│   ├── agents/                           # ✅ Kernkomponenten
│   │   ├── __init__.py
│   │   ├── imap_fetcher.py               # ✅ IMAP-Verbindung
│   │   ├── mail_parser.py                # ✅ E-Mail-Parsing
│   │   ├── attachment_handler.py         # ✅ Anhang-Verwaltung
│   │   └── llm_request.py                # ✅ OLLAMA-Integration
│   │
│   ├── catalog/                          # ✅ Ressourcen
│   │   ├── prompts/
│   │   │   ├── extract_problem.txt       # ✅ Problem-Prompt
│   │   │   ├── extract_solution.txt      # ✅ Solution-Prompt
│   │   │   └── extract_asset.txt         # ✅ Asset-Prompt
│   │   │
│   │   ├── json_store/                   # ✅ Schema-Templates
│   │   │   ├── problem_schema.json
│   │   │   ├── solution_schema.json
│   │   │   └── asset_schema.json
│   │   │
│   │   └── mail/                         # ✅ NEU: Mail-Templates
│   │       ├── added_knowledge_mail.html # Confirmation Template
│   │       └── mail_variables.json       # Template-Config
│   │
│   ├── config/                           # ✅ Konfiguration
│   │   ├── mail_config.json              # IMAP/SMTP-Einstellungen
│   │   └── secrets.json                  # Credentials (gitignored)
│   │
│   ├── storage/                          # ✅ Dateisystem-Storage
│   │   ├── mails/                        # Roh-E-Mails (.eml)
│   │   ├── attachments/
│   │   │   ├── images/                   # Screenshots
│   │   │   ├── documents/                # PDFs, Docs
│   │   │   └── logs/                     # Log-Dateien
│   │   ├── processed/                    # ✅ Erfolgreiche JSONs
│   │   ├── failed/                       # ✅ Fehlgeschlagene Extractions
│   │   └── sent/                         # ✅ NEU: Archivierte Mails
│   │
│   ├── utils/                            # ✅ Hilfsfunktionen
│   │   ├── __init__.py
│   │   ├── logger.py                     # Strukturiertes Logging
│   │   ├── file_handler.py               # Datei-Operationen
│   │   ├── credentials.py                # Secrets-Manager
│   │   └── analyze_json_quality.py       # ✅ NEU: Quality-Analyzer
│   │
│   ├── run_agent.py                      # ✅ Stufe 1: Mail Fetch
│   ├── run_extract.py                    # ✅ Stufe 2: JSON Extract
│   ├── run_send_response.py              # ✅ NEU: Stufe 3: Confirmation
│   └── test_mail.py                      # ✅ IMAP/SMTP-Test
│
├── documents/                            # 📚 Dokumentation
│   ├── nice2know_json_schema_referenz.md # ✅ Schema-Doku
│   └── nice2know_projektplan.md          # Dieser Plan
│
├── setup.sh                              # ✅ Environment-Setup
├── requirements.txt                      # ✅ Python-Dependencies
└── README.md                             # ✅ Projekt-Readme
```

---

## 5. Nächste Schritte (Phase 2 - MVP)

### 5.1 Sprint 1: PostgreSQL-Integration (Priorität 1)

**Ziel:** JSON-Daten aus File-Storage in PostgreSQL importieren

**Tasks:**
1. PostgreSQL-Setup
   - [ ] Datenbank erstellen (`createdb nice2know`)
   - [ ] Schema anlegen (siehe Kap. 5.2)
   - [ ] Indizes erstellen
   - [ ] Zugangsdaten in `secrets.json`

2. Import-Script entwickeln
   - [ ] `import_to_postgres.py` erstellen
   - [ ] JSON-Datei → JSONB-Mapping
   - [ ] Batch-Import für existing JSONs
   - [ ] Transaction-Handling

3. Run-Extract erweitern
   - [ ] Nach JSON-Generierung → DB-Import
   - [ ] Error-Handling bei DB-Fehlern
   - [ ] Rollback-Strategie

**Akzeptanzkriterien:**
- ✅ Alle 3 JSON-Typen lassen sich importieren
- ✅ JSONB-Queries funktionieren
- ✅ Indizes beschleunigen Suchen
- ✅ Existing JSONs im File-Storage migriert

**Zeitschätzung:** 1-2 Wochen

---

### 5.2 PostgreSQL-Schema (Bereit)

```sql
-- Problems Table
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
    USING GIN(to_tsvector('english', 
        COALESCE(data->'problem'->>'title', '') || ' ' ||
        COALESCE(data->'problem'->>'description', '')
    ));

-- Solutions Table
CREATE TABLE solutions (
    id SERIAL PRIMARY KEY,
    solution_id VARCHAR(100) UNIQUE NOT NULL,
    asset_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_solutions_asset ON solutions(asset_id);
CREATE INDEX idx_solutions_reusability ON solutions(
    ((data->'metadata'->>'reusability_score')::float)
);

-- Assets Table
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(100) UNIQUE NOT NULL,
    asset_name VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_assets_type ON assets((data->'asset'->>'type'));
CREATE INDEX idx_assets_category ON assets((data->'asset'->>'category'));
CREATE INDEX idx_assets_status ON assets((data->'asset'->>'status'));

-- Cases Table (Phase 2, später)
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

### 5.3 Sprint 2: Magic-Link-Backend (Priorität 2)

**Ziel:** Web-Interface zum Editieren extrahierter Daten

**Stack:** PHP + Vue.js (bereits im Projekt vorhanden)

**Tasks:**
1. Backend (PHP)
   - [ ] Token-Generierung für Magic Links
   - [ ] Token-Validierung & Expiry (48h)
   - [ ] JSON-Update-Endpunkt
   - [ ] Bestätigungs-Endpunkt

2. Frontend (Vue.js)
   - [ ] Edit-Formular für Problem/Solution/Asset
   - [ ] Pre-Fill mit JSON-Daten
   - [ ] Fehlende Felder hervorheben
   - [ ] Save & Confirm Buttons

3. Integration
   - [ ] Link-Generierung in `run_send_response.py`
   - [ ] Token in Datenbank speichern
   - [ ] Email-Versand mit korrekten URLs

**Zeitschätzung:** 2 Wochen

---

### 5.4 Sprint 3: Attachment-Analyse (Priorität 3)

**Ziel:** OCR und Text-Extraktion aus Anhängen

**Tasks:**
1. OCR-Integration (Tesseract)
   - [ ] Tesseract installieren
   - [ ] Python-Wrapper (`pytesseract`)
   - [ ] Bild → Text-Extraktion
   - [ ] Sprach-Erkennung (DE + EN)

2. PDF-Text-Extraktion
   - [ ] PyPDF2 oder pdfplumber
   - [ ] Text aus PDFs extrahieren
   - [ ] Layout-Preservation

3. Integration in Problem-JSON
   - [ ] Extrahierter Text → `problem.error_messages`
   - [ ] Attachment-Metadaten in Case-JSON

**Zeitschätzung:** 2 Wochen

---

### 5.5 Sprint 4: REST-API (Priorität 4)

**Ziel:** CRUD-Operationen über HTTP-Endpunkte

**Framework:** FastAPI (Python)

**Endpunkte:**
```
GET    /api/v1/problems
GET    /api/v1/problems/{id}
GET    /api/v1/solutions
GET    /api/v1/assets
GET    /api/v1/search?q={query}
POST   /api/v1/problems/{id}/confirm
PUT    /api/v1/problems/{id}
```

**Zeitschätzung:** 2 Wochen

---

## 6. Erfolgsmetriken (Tracking)

### 6.1 KPIs für Phase 1 (PoC) ✅

| Metrik | Ziel | Erreicht |
|--------|------|----------|
| E-Mails verarbeitbar | ✅ | ✅ 100% |
| JSON-Generierung | ✅ | ✅ 3/3 Typen |
| OLLAMA-Zuverlässigkeit | >90% | ✅ ~95% (manuell getestet) |
| Schema-Konformität | 100% | ✅ 100% (mit Validation) |
| Prompt-Engineering | Iterativ | ✅ 3 Iterationen |
| Quality-Analyzer | Funktional | ✅ Implementiert |
| Confirmation Mails | Versendbar | ✅ HTML-Template v2 |

### 6.2 KPIs für Phase 2 (MVP) 🚧

| Metrik | Ziel | Aktuell |
|--------|------|---------|
| PostgreSQL-Import | Funktionsfähig | 🚧 Offen |
| Magic-Link-Backend | Funktional | 📋 Geplant |
| Attachment-OCR | Text aus Bildern | 📋 Geplant |
| API-Endpunkte | 5+ RESTful | 📋 Geplant |
| Response-Zeit | <2s pro Query | 📋 Zu messen |
| User-Confirmation-Rate | >60% | 📋 Nicht gemessen |

### 6.3 KPIs für Produktivbetrieb (Phase 3) 📋

| Metrik | Ziel (nach 6 Monaten) | Status |
|--------|----------------------|--------|
| Knowledge Capture | >80% | 📋 Nicht gemessen |
| Zeitersparnis | 30% | 📋 Nicht gemessen |
| Lösungswiederverwendung | 40% | 📋 Nicht gemessen |
| Datenqualität | <5% Fehler | 📋 Nicht gemessen |
| User Adoption | 70% | 📋 Nicht gemessen |

---

## 7. Risiken & Mitigations (Aktualisiert)

| Risiko | Wahrscheinlichkeit | Impact | Status | Mitigation |
|--------|-------------------|--------|--------|------------|
| OLLAMA extrahiert falsche Daten | Medium | Hoch | ✅ Mitigiert | Human Review + Quality Analyzer |
| Schema-Änderungen brechen Kompatibilität | Niedrig | Hoch | ✅ Mitigiert | Semantic Versioning |
| Anhänge zu groß | Mittel | Mittel | ✅ Mitigiert | 50MB-Limit implementiert |
| Datenschutz-Bedenken | Mittel | Hoch | ✅ Mitigiert | Lokales OLLAMA (kein Cloud) |
| PostgreSQL-Performance | Niedrig | Mittel | 🚧 Offen | Indizes geplant |
| OCR-Fehlerquote | Mittel | Mittel | 📋 Offen | Multi-Language-Support |
| OLLAMA CPU-Timeout | Hoch | Mittel | 🚧 In Bearbeitung | GPU-Acceleration geplant |
| Mail-Versand-Fehler | Niedrig | Mittel | ✅ Mitigiert | Error-Handling + Logging |
| File-Permission-Konflikte | Mittel | Hoch | ✅ Gelöst | Dynamische Pfadauflösung |

---

## 8. Technologie-Entscheidungen (Dokumentiert)

### 8.1 Warum OLLAMA statt Cloud-LLMs?

**Entscheidung:** Lokales OLLAMA statt OpenAI/Claude

**Gründe:**
1. **Datenschutz**: Keine Daten verlassen das System
2. **Kosten**: Keine API-Gebühren (wichtig bei vielen E-Mails)
3. **Verfügbarkeit**: Keine Internet-Abhängigkeit
4. **Kontrolle**: Eigenes Modell-Training möglich

**Nachteil:**
- Geringere Qualität als GPT-4/Claude (aber ausreichend für Use-Case)
- Hardware-Anforderungen (GPU empfohlen)

---

### 8.2 Warum PostgreSQL statt MongoDB?

**Entscheidung:** PostgreSQL mit JSONB statt MongoDB

**Gründe:**
1. **JSONB-Support**: Flexibel wie MongoDB, aber mit SQL
2. **Indexes**: GIN-Indexes für schnelle JSON-Queries
3. **Transactions**: ACID-Garantien
4. **Tooling**: PgAdmin, DBeaver, etc.
5. **Relationen**: Können später hinzugefügt werden

---

### 8.3 Warum Zwei-Stufen-Workflow?

**Entscheidung:** `run_agent.py` + `run_extract.py` statt Monolith

**Gründe:**
1. **Separation of Concerns**: Mail-Fetching ≠ JSON-Extraktion
2. **Retry-Logik**: Failed Extractions ohne Re-Fetching
3. **Debugging**: Einfacheres Troubleshooting
4. **Performance**: OLLAMA kann offline laufen

---

## 9. Glossar

- **Asset**: IT-System, Anwendung oder Infrastruktur-Komponente
- **Case**: Vollständiger Support-Fall von Meldung bis Lösung (Phase 2)
- **Completeness Score**: Qualitätsmetrik (0-100%) für JSON-Vollständigkeit
- **JSONB**: PostgreSQL-binäres JSON-Datenformat
- **Magic Link**: Einmaliger Token-Link für Web-Editing ohne Login
- **OLLAMA**: Lokales Large Language Model Framework
- **OCR**: Optical Character Recognition (Text aus Bildern)
- **PoC**: Proof of Concept (Machbarkeitsnachweis)
- **Quality Analyzer**: Tool zur Bewertung von JSON-Qualität
- **Reusability Score**: Bewertung der Wiederverwendbarkeit einer Lösung (0.0-1.0)
- **Schema Version**: Versionsnummer des JSON-Formats (Semantic Versioning)
- **UUID**: Universally Unique Identifier

---

## 10. Changelog (Was ist neu seit v1.2?)

### Version 1.3 (17. November 2025)

**Neue Features:**
- ✅ Quality Analyzer implementiert (`utils/analyze_json_quality.py`)
- ✅ Confirmation Mail System v2 mit HTML-Templates
- ✅ Drei-Stufen-Workflow (Fetch → Extract → Confirm)
- ✅ Dynamische Konfigurationspfade
- ✅ Storage-Archivierung (`/sent/` Ordner)
- ✅ Fehlende-Felder-Visualisierung in Mails

**Verbesserungen:**
- ✅ Keine hardcoded Pfade mehr
- ✅ Besseres Error-Handling bei Mail-Versand
- ✅ Quality-Metriken in Confirmation-Mails
- ✅ Anchor-Links zu unvollständigen Feldern

**Dokumentation:**
- ✅ Architektur-Diagramm aktualisiert
- ✅ Workflow-Beschreibung erweitert
- ✅ Quality-Analyzer-Doku hinzugefügt
- ✅ Risikomanagement aktualisiert

---

**Dokument-Version**: 1.3  
**Letztes Update**: 17. November 2025  
**Nächstes Review**: 1. Dezember 2025 (nach Sprint 1 - PostgreSQL)  
**Status**: Phase 1 ✅ | Phase 2 🚧 | Phase 3 📋
