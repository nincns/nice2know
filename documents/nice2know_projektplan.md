# nice2know - Projektplan (Aktualisiert)

**Version:** 1.2  
**Datum:** 15. November 2025  
**Status:** Phase 1 (Proof of Concept) ✅ Abgeschlossen | Phase 2 (MVP) 🚧 In Arbeit

---

## 1. Executive Summary

**nice2know** ist ein intelligentes Knowledge-Management-System, das E-Mail-basierten IT-Support automatisch in eine durchsuchbare, strukturierte Wissensdatenbank transformiert. Mittels lokaler OLLAMA-KI-Analyse werden Probleme, Lösungen und betroffene IT-Assets aus E-Mails extrahiert und als JSON-Dokumente persistiert.

### Projektstatus (Stand: 15.11.2025)

**Phase 1 (PoC) ist abgeschlossen:**
- ✅ IMAP-Mail-Abruf implementiert
- ✅ Mail-Parsing (Headers, Body, Attachments)
- ✅ OLLAMA-Integration funktionsfähig
- ✅ JSON-Generierung für Problem, Solution, Asset
- ✅ Prompt-Engineering und Schema-Validierung

**Phase 2 (MVP) startet:**
- 🚧 PostgreSQL-Integration steht an
- 📋 Attachment-Analyse (OCR/PDF) geplant
- 📋 REST-API in Planung

---

## 2. Architektur-Übersicht (Aktueller Stand)

### 2.1 Implementierte Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                    nice2know System (PoC)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────────┐              │
│  │ IMAP Fetcher │────────▶│  Mail Parser     │              │
│  │              │         │  - Headers       │              │
│  │ ✅ Fertig    │         │  - Body          │              │
│  └──────────────┘         │  - Attachments   │              │
│                           │  ✅ Fertig       │              │
│                           └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│                           │ Attachment Store │              │
│                           │  /images/        │              │
│                           │  /documents/     │              │
│                           │  /logs/          │              │
│                           │  ✅ Fertig       │              │
│                           └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│               ┌───────────────────────────────────┐         │
│               │      OLLAMA LLM Engine            │         │
│               │                                   │         │
│               │  Prompts (✅ Fertig):             │         │
│               │  ├─ extract_problem.txt           │         │
│               │  ├─ extract_solution.txt          │         │
│               │  └─ extract_asset.txt             │         │
│               │                                   │         │
│               │  Schemas (✅ Fertig):             │         │
│               │  ├─ problem_schema.json           │         │
│               │  ├─ solution_schema.json          │         │
│               │  └─ asset_schema.json             │         │
│               └────────┬──────────────────────────┘         │
│                        │                                    │
│                        ▼                                    │
│               ┌──────────────────┐                          │
│               │  JSON Generator  │                          │
│               │  ✅ Fertig       │                          │
│               │                  │                          │
│               │  • Problem JSON  │                          │
│               │  • Solution JSON │                          │
│               │  • Asset JSON    │                          │
│               └────────┬─────────┘                          │
│                        │                                    │
│                        ▼                                    │
│               ┌──────────────────┐                          │
│               │  File Storage    │                          │
│               │  (Staging)       │                          │
│               │  ✅ Fertig       │                          │
│               └────────┬─────────┘                          │
│                        │                                    │
│                        ▼                                    │
│               ┌──────────────────┐                          │
│               │   PostgreSQL     │                          │
│               │   (JSONB)        │                          │
│               │   🚧 Nächster    │                          │
│               │      Sprint      │                          │
│               └──────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technologie-Stack (Implementiert)

| Komponente | Technologie | Status | Datei |
|------------|-------------|--------|-------|
| Mail Fetcher | Python + IMAPlib | ✅ Fertig | `agents/imap_fetcher.py` |
| Mail Parser | Python + email lib | ✅ Fertig | `agents/mail_parser.py` |
| Attachment Handler | Python + FileHandler | ✅ Fertig | `agents/attachment_handler.py` |
| **LLM Engine** | **OLLAMA (lokal)** | ✅ Fertig | `agents/llm_request.py` |
| JSON Generator | Python + Schema-Validation | ✅ Fertig | In LLM-Integration |
| File Storage | Filesystem (categorized) | ✅ Fertig | `storage/processed/` |
| **Database** | **PostgreSQL + JSONB** | 🚧 Geplant | Schema dokumentiert |
| Object Storage | Filesystem (attachments) | ✅ Fertig | `storage/attachments/` |

---

## 3. Datenfluss (Aktuell Implementiert)

### 3.1 E-Mail-Verarbeitung (End-to-End)

```
┌─────────────────┐
│  IMAP Mailbox   │
└────────┬────────┘
         │ [imap_fetcher.py]
         ▼
┌─────────────────┐
│  Raw E-Mail     │
│  (.eml Format)  │
└────────┬────────┘
         │ [mail_parser.py]
         ▼
┌──────────────────────────────┐
│  Parsed Mail Data            │
│  ├─ message_id               │
│  ├─ from / to / subject      │
│  ├─ body (plain + html)      │
│  └─ attachments[] metadata   │
└────────┬─────────────────────┘
         │
         ├──────────┬──────────────────┐
         │          │                  │
         ▼          ▼                  ▼
   [Save Raw]  [Attachments]     [LLM Processing]
    storage/   storage/           llm_request.py
    mails/     attachments/
                /images/
                /documents/
                /logs/
```

### 3.2 LLM-Verarbeitung (Kern-Pipeline)

```
Input: E-Mail Body + Metadaten
├─ Mail-ID: abc123...
├─ Subject: "Outlook Senden-Button fehlt"
└─ Body: "Das Menüband ist minimiert..."

         │
         ▼
┌──────────────────────────────────────┐
│  OLLAMA LLM Processing               │
│  (3 parallele Extraktionen)          │
│                                      │
│  1. Problem-Extraktion               │
│     Prompt: extract_problem.txt      │
│     Schema: problem_schema.json      │
│     → Output: prob_abc123.json       │
│                                      │
│  2. Solution-Extraktion              │
│     Prompt: extract_solution.txt     │
│     Schema: solution_schema.json     │
│     → Output: sol_xyz789.json        │
│                                      │
│  3. Asset-Identifikation             │
│     Prompt: extract_asset.txt        │
│     Schema: asset_schema.json        │
│     → Output: asset_outlook_01.json  │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  JSON-Validierung                    │
│  - Schema-Konformität prüfen         │
│  - ID-Generierung (mail_id-basiert)  │
│  - Timestamp setzen                  │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  File Storage (Staging)              │
│  storage/processed/                  │
│  ├─ 20251115_145429_problem.json     │
│  ├─ 20251115_145429_solution.json    │
│  └─ 20251115_145429_asset.json       │
└──────────────────────────────────────┘
         │
         ▼
    [PostgreSQL Import]
         🚧
    Nächster Sprint
```

---

## 4. JSON-Schema-Implementierung

### 4.1 Übersicht der JSON-Typen

| JSON-Typ | Zweck | Größe | Status |
|----------|-------|-------|--------|
| **Problem JSON** | Problembeschreibung | ~2-5 KB | ✅ Implementiert |
| **Solution JSON** | Lösungsdokumentation | ~5-15 KB | ✅ Implementiert |
| **Asset JSON** | IT-Asset-Katalog | ~3-10 KB | ✅ Implementiert |
| **Case JSON** | Problem-Solution-Linking | ~3-7 KB | 📋 Geplant (Phase 2) |

### 4.2 Prompt-Engineering (Implementiert)

**Strategien für präzise Extraktion:**

1. **Strukturierte System-Prompts**
   - Klare Rollenbeschreibung ("You are a technical support analyst")
   - Explizite Anweisungen ("Extract ONLY valid JSON")
   - Negativbeispiele ("Do NOT include explanations")

2. **Schema als Beispiel**
   - JSON-Schema wird als Template in Prompt eingebettet
   - LLM verwendet Schema als Vorlage
   - Verhindert Struktur-Abweichungen

3. **Post-Processing**
   - Mail-ID-basierte ID-Generierung
   - Timestamp-Normalisierung (ISO8601 UTC)
   - Array-Normalisierung ([] statt [null])

**Beispiel: Problem-Extraktion**

```
Prompt-Struktur (extract_problem.txt):

1. Rollenbeschreibung
   "You are a technical support analyst..."

2. Aufgabe
   "TASK: Extract the technical problem from the email"

3. Extraktionsrichtlinien
   "- Identify core issue
    - Extract symptoms
    - Determine severity"

4. JSON-Schema-Template
   "EXPECTED JSON STRUCTURE:
    {schema_json}"

5. Antwortformat
   "Return ONLY valid JSON. NO explanations."
```

---

## 5. Implementierte Features (Details)

### 5.1 IMAP Mail Fetcher

**Datei:** `mail_agent/agents/imap_fetcher.py`

**Features:**
- ✅ IMAP/SSL-Verbindung
- ✅ Credentials aus `secrets.json`
- ✅ Mailbox-Auswahl (INBOX, custom)
- ✅ Ungelesene Mails filtern
- ✅ Limit-Parameter (z.B. 50 neueste)
- ✅ Mark-as-read optional
- ✅ Connection-Cleanup

**Verwendung:**
```python
fetcher = IMAPFetcher(config)
fetcher.connect()
fetcher.select_mailbox('INBOX')
messages = fetcher.fetch_messages(limit=50, unseen_only=True)
```

### 5.2 Mail Parser

**Datei:** `mail_agent/agents/mail_parser.py`

**Features:**
- ✅ MIME-Header-Decoding (UTF-8, Base64)
- ✅ Message-ID-Extraktion
- ✅ Body-Extraktion (plain + HTML)
- ✅ Attachment-Metadata (Dateiname, Typ, Größe)
- ✅ Encoding-Error-Handling
- ✅ Multipart-Message-Support

**Output-Struktur:**
```python
{
    'message_id': 'abc123...',
    'from': 'user@example.com',
    'to': 'support@example.com',
    'subject': 'Outlook Problem',
    'date': '2025-11-15T10:35:57Z',
    'body': {
        'plain': '...',
        'html': '...'
    },
    'attachments': [
        {
            'filename': 'screenshot.png',
            'content_type': 'image/png',
            'size': 245678,
            'part': <email.message.Message object>
        }
    ]
}
```

### 5.3 Attachment Handler

**Datei:** `mail_agent/agents/attachment_handler.py`

**Features:**
- ✅ Automatische Kategorisierung (images, documents, logs)
- ✅ Größen-Limit (konfigurierbar, Standard 50MB)
- ✅ MD5-Hash für Duplikat-Erkennung
- ✅ Timestamp-basierte Dateinamen
- ✅ Sichere Dateinamen (Sanitization)

**Kategorisierungs-Logik:**
```python
{
    '.png, .jpg, .jpeg, .gif, .bmp, .webp': 'images',
    '.pdf, .doc, .docx, .txt, .md, .rtf': 'documents',
    '.log, .txt': 'logs',
    'default': 'documents'
}
```

### 5.4 LLM Request (OLLAMA-Integration)

**Datei:** `mail_agent/agents/llm_request.py`

**Features:**
- ✅ OLLAMA-Connection-Test
- ✅ Prompt-Engineering (System + User Prompt)
- ✅ JSON-Schema-Enforcement (`format: "json"`)
- ✅ Post-Processing (ID-Generierung, Cleanup)
- ✅ Error-Handling (JSON-Parse-Fehler)
- ✅ Mail-ID-basierte ID-Generierung

**Verwendung:**
```bash
python agents/llm_request.py \
  --pre_prompt catalog/prompts/extract_problem.txt \
  --mailbody storage/mails/test.eml \
  --json catalog/json_store/problem_schema.json \
  --export storage/processed/problem.json
```

**LLM-Parameter:**
```python
{
    "model": "llama3.2:latest",
    "temperature": 0.1,      # Deterministisch
    "top_p": 0.9,
    "format": "json",        # Erzwingt JSON-Output
    "stream": False
}
```

---

## 6. Prompt-Katalog (Implementiert)

### 6.1 Problem-Extraktion

**Datei:** `mail_agent/catalog/prompts/extract_problem.txt`

**Extrahiert:**
- Problem-Titel (kurz, prägnant)
- Detaillierte Beschreibung
- Beobachtbare Symptome
- Fehlermeldungen (wenn vorhanden)
- Severity (low, medium, high, critical)

**Besonderheiten:**
- Business-Impact-Assessment
- Unterscheidung zwischen Symptom und Root Cause
- Reporter-Daten-Extraktion aus Mail-Header

### 6.2 Solution-Extraktion

**Datei:** `mail_agent/catalog/prompts/extract_solution.txt`

**Extrahiert:**
- Lösungs-Titel
- Lösungs-Typ (configuration, bugfix, workaround)
- Schritt-für-Schritt-Anleitung
- Voraussetzungen
- Erfolgskriterien
- Reusability-Score

**Besonderheiten:**
- Erzwingt Array[Object] für Steps (nicht Array[String])
- Post-Processing für Mail-ID-basierte IDs
- Komplexitäts-Einschätzung (low, medium, high)

### 6.3 Asset-Identifikation

**Datei:** `mail_agent/catalog/prompts/extract_asset.txt`

**Extrahiert:**
- Asset-Name (z.B. "Microsoft Outlook")
- Asset-Typ (z.B. "mail_client")
- Kategorie (z.B. "client")
- Technische Details (Software, Version, Plattform)
- Criticality-Assessment

**Besonderheiten:**
- Verhindert Pipe-Symbole in type/category (EXAKT EINEN Wert wählen)
- Flache Arrays ([] statt [[]])
- Ownership-Extraktion aus Mail-Header

---

## 7. Dateistruktur (Implementiert)

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
│   ├── catalog/                          # ✅ Prompt- & Schema-Bibliothek
│   │   ├── prompts/
│   │   │   ├── extract_problem.txt       # ✅ Problem-Prompt
│   │   │   ├── extract_solution.txt      # ✅ Solution-Prompt
│   │   │   └── extract_asset.txt         # ✅ Asset-Prompt
│   │   │
│   │   └── json_store/
│   │       ├── problem_schema.json       # ✅ Problem-Template
│   │       ├── solution_schema.json      # ✅ Solution-Template
│   │       └── asset_schema.json         # ✅ Asset-Template
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
│   │   └── processed/                    # ✅ Generierte JSONs
│   │
│   ├── utils/                            # ✅ Hilfsfunktionen
│   │   ├── __init__.py
│   │   ├── logger.py                     # Strukturiertes Logging
│   │   ├── file_handler.py               # Datei-Operationen
│   │   └── credentials.py                # Secrets-Manager
│   │
│   ├── run_agent.py                      # ✅ Hauptprogramm
│   └── test_mail.py                      # ✅ IMAP/SMTP-Test
│
├── documents/                            # Dokumentation
│   ├── nice2know_json_schema_referenz.md # ✅ Schema-Doku
│   └── nice2know_projektplan.md          # Dieser Plan
│
├── setup.sh                              # ✅ Environment-Setup
├── requirements.txt                      # ✅ Python-Dependencies
└── README.md                             # ✅ Projekt-Readme
```

---

## 8. Nächste Schritte (Phase 2 - MVP)

### 8.1 Sprint 1: PostgreSQL-Integration (Priorität 1)

**Ziel:** JSON-Daten aus File-Storage in PostgreSQL importieren

**Tasks:**
1. PostgreSQL-Setup
   - [ ] Datenbank erstellen (`createdb nice2know`)
   - [ ] Schema anlegen (siehe Kap. 8.2)
   - [ ] Indizes erstellen
   - [ ] Zugangsdaten in `secrets.json`

2. Import-Script entwickeln
   - [ ] `import_to_postgres.py` erstellen
   - [ ] JSON-Datei → JSONB-Mapping
   - [ ] Batch-Import für existing JSONs
   - [ ] Transaction-Handling

3. Run-Agent erweitern
   - [ ] Nach JSON-Generierung → DB-Import
   - [ ] Error-Handling bei DB-Fehlern
   - [ ] Rollback-Strategie

**Akzeptanzkriterien:**
- ✅ Alle 3 JSON-Typen lassen sich importieren
- ✅ JSONB-Queries funktionieren
- ✅ Indizes beschleunigen Suchen
- ✅ Existing JSONs im File-Storage migriert

**Zeitschätzung:** 1 Woche

### 8.2 PostgreSQL-Schema (Bereit)

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

### 8.3 Sprint 2: Attachment-Analyse (Priorität 2)

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

### 8.4 Sprint 3: Case-JSON-Generierung (Priorität 3)

**Ziel:** Verknüpfung von Problem-Solution-Asset

**Tasks:**
1. Case-JSON-Template erstellen
2. Linking-Logic implementieren
3. Resolution-Path dokumentieren
4. Metriken berechnen (time_to_resolution)

**Zeitschätzung:** 1 Woche

### 8.5 Sprint 4: REST-API (Priorität 4)

**Ziel:** CRUD-Operationen über HTTP-Endpunkte

**Framework:** FastAPI (Python)

**Endpunkte:**
```
GET    /api/v1/problems
GET    /api/v1/problems/{id}
GET    /api/v1/solutions
GET    /api/v1/assets
GET    /api/v1/search?q={query}
```

**Zeitschätzung:** 2 Wochen

---

## 9. Erfolgsmetriken (Tracking)

### 9.1 KPIs für Phase 1 (PoC) ✅

| Metrik | Ziel | Erreicht |
|--------|------|----------|
| E-Mails verarbeitbar | ✅ | ✅ 100% |
| JSON-Generierung | ✅ | ✅ 3/3 Typen |
| OLLAMA-Zuverlässigkeit | >90% | ✅ ~95% (manuell getestet) |
| Schema-Konformität | 100% | ✅ 100% (mit Validation) |
| Prompt-Engineering | Iterativ | ✅ 3 Iterationen |

### 9.2 KPIs für Phase 2 (MVP) 🚧

| Metrik | Ziel | Aktuell |
|--------|------|---------|
| PostgreSQL-Import | Funktionsfähig | 🚧 Offen |
| Attachment-OCR | Text aus Bildern | 📋 Geplant |
| Case-JSON-Linking | Vollständig | 📋 Geplant |
| API-Endpunkte | 5+ RESTful | 📋 Geplant |
| Response-Zeit | <2s pro Query | 📋 Zu messen |

### 9.3 KPIs für Produktivbetrieb (Phase 3) 📋

| Metrik | Ziel (nach 6 Monaten) | Status |
|--------|----------------------|--------|
| Knowledge Capture | >80% | 📋 Nicht gemessen |
| Zeitersparnis | 30% | 📋 Nicht gemessen |
| Lösungswiederverwendung | 40% | 📋 Nicht gemessen |
| Datenqualität | <5% Fehler | 📋 Nicht gemessen |
| User Adoption | 70% | 📋 Nicht gemessen |

---

## 10. Risiken & Mitigations (Aktualisiert)

| Risiko | Wahrscheinlichkeit | Impact | Status | Mitigation |
|--------|-------------------|--------|--------|------------|
| OLLAMA extrahiert falsche Daten | Medium | Hoch | ✅ Mitigiert | Human Review für Stichproben |
| Schema-Änderungen brechen Kompatibilität | Niedrig | Hoch | ✅ Mitigiert | Semantic Versioning |
| Anhänge zu groß | Mittel | Mittel | ✅ Mitigiert | 50MB-Limit implementiert |
| Datenschutz-Bedenken | Mittel | Hoch | ✅ Mitigiert | Lokales OLLAMA (kein Cloud) |
| PostgreSQL-Performance | Niedrig | Mittel | 🚧 Offen | Indizes geplant |
| OCR-Fehlerquote | Mittel | Mittel | 📋 Offen | Multi-Language-Support |

---

## 11. Technologie-Entscheidungen (Dokumentiert)

### 11.1 Warum OLLAMA statt Cloud-LLMs?

**Entscheidung:** Lokales OLLAMA statt OpenAI/Claude

**Gründe:**
1. **Datenschutz**: Keine Daten verlassen Server
2. **Kosten**: Keine API-Gebühren
3. **Latenz**: Keine Netzwerk-Roundtrips
4. **Kontrolle**: Eigenes Modell-Hosting
5. **Offline-Fähigkeit**: Kein Internet erforderlich

**Trade-off:**
- Hardware-Anforderungen (16GB RAM, GPU empfohlen)
- Modell-Qualität niedriger als GPT-4/Claude

### 11.2 Warum PostgreSQL statt MongoDB?

**Entscheidung:** PostgreSQL + JSONB statt MongoDB

**Gründe:**
1. **Relationale Integrität**: Foreign Keys zwischen Tables
2. **JSONB**: Flexibilität wie NoSQL + SQL-Queries
3. **Indexierung**: GIN-Indizes für JSONB-Performance
4. **ACID**: Transaktions-Garantien
5. **Reife**: Sehr stabile, etablierte Technologie

**Trade-off:**
- Komplexere Queries für tief verschachtelte JSONs
- Weniger "native" JSON-Unterstützung als MongoDB

### 11.3 Warum File-Storage-Staging?

**Entscheidung:** Zweistufiger Ansatz (File → DB)

**Gründe:**
1. **Debugging**: JSON-Dateien inspizierbar
2. **Flexibilität**: DB-Schema änderbar ohne Re-Extraktion
3. **Backup**: Dateien als Fallback
4. **Iterativ**: PoC ohne DB-Abhängigkeit

**Langfristig:** File-Storage bleibt für Audit-Trail

---

## 12. Lessons Learned (Phase 1)

### 12.1 Prompt-Engineering

**Gelernt:**
- LLMs neigen zu Markdown-Code-Blocks (`json\n...\n``)
- Post-Processing essentiell (Regex-Cleanup)
- Schema als Beispiel → bessere Struktur-Konformität
- Temperature=0.1 → deterministischer Output

**Anpassungen:**
- Prompt: "NO markdown, NO code blocks"
- Cleanup-Funktion in `llm_request.py`
- Schema-Einbettung in System-Prompt

### 12.2 OLLAMA-Performance

**Gelernt:**
- llama3.2:latest ist ausreichend für Extraktion
- Größere Modelle (13B+) nicht merklich besser
- GPU beschleunigt deutlich (CPU: ~30s, GPU: ~5s pro Mail)

**Empfehlung:**
- llama3.2:latest für Production
- GPU für >100 Mails/Tag

### 12.3 ID-Generierung

**Gelernt:**
- LLMs können keine echten UUIDs generieren
- Placeholder-IDs (`prob_[0-9a-f]{32}`) bleiben im Output
- Mail-ID als Basis → konsistente IDs

**Lösung:**
- Post-Processing extrahiert Mail-ID
- Generiert prob_/sol_-Präfix + Mail-ID-Hash
- Garantiert Eindeutigkeit + Rückverfolgbarkeit

---

## 13. Deployment-Plan (Phase 2)

### 13.1 Lokaler Server-Setup

**Hardware-Anforderungen:**
- CPU: 4+ Cores (8+ empfohlen)
- RAM: 16GB (für OLLAMA + PostgreSQL)
- Disk: 100GB+ (Modelle + Attachments + DB)
- GPU: Optional (NVIDIA, für Performance)

**Software-Stack:**
```
┌─────────────────────────────────┐
│  Ubuntu 22.04 LTS               │
├─────────────────────────────────┤
│  Docker Compose (optional)      │
│  ├─ PostgreSQL 14 Container     │
│  └─ nice2know App Container     │
│                                 │
│  ODER native Installation:      │
│  ├─ PostgreSQL 14               │
│  ├─ OLLAMA (systemd service)    │
│  └─ Python 3.10 venv            │
└─────────────────────────────────┘
```

### 13.2 Installation (Native)

```bash
# 1. System-Updates
sudo apt update && sudo apt upgrade -y

# 2. PostgreSQL
sudo apt install postgresql-14 postgresql-contrib -y
sudo systemctl enable postgresql
sudo systemctl start postgresql

# 3. OLLAMA
curl https://ollama.ai/install.sh | sh
ollama pull llama3.2:latest

# 4. nice2know
cd /opt
git clone https://github.com/yourusername/nice2know.git
cd nice2know
./setup.sh
source venv/bin/activate

# 5. PostgreSQL-Setup
sudo -u postgres psql
CREATE DATABASE nice2know;
CREATE USER n2k_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nice2know TO n2k_user;
\q

# 6. Schema erstellen
psql -h localhost -U n2k_user -d nice2know < schema.sql

# 7. Konfiguration
cd mail_agent
cp config/secrets.json.example config/secrets.json
nano config/secrets.json  # Credentials eintragen

# 8. Test
python test_mail.py
python agents/llm_request.py --test

# 9. Produktiv starten
python run_agent.py --loop --interval 300
```

### 13.3 Systemd-Service (Optional)

```ini
# /etc/systemd/system/nice2know.service
[Unit]
Description=nice2know Mail Agent
After=network.target postgresql.service ollama.service

[Service]
Type=simple
User=n2k_user
WorkingDirectory=/opt/nice2know/mail_agent
ExecStart=/opt/nice2know/venv/bin/python run_agent.py --loop --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nice2know
sudo systemctl start nice2know
sudo systemctl status nice2know
```

---

## 14. Zeitplan (Aktualisiert)

### ✅ Phase 1: Proof of Concept (Abgeschlossen)

**Dauer:** 4 Wochen (Okt - Nov 2025)

- **Woche 1-2**: Infrastruktur-Setup
  - ✅ Mail Fetcher implementiert
  - ✅ OLLAMA-Integration
  - ✅ Basic JSON-Generator
- **Woche 3**: Prompt-Engineering
  - ✅ Problem/Solution/Asset-Prompts
  - ✅ Schema-Templates
  - ✅ Iterative Optimierung
- **Woche 4**: Testing & Iteration
  - ✅ 10+ Test-E-Mails verarbeitet
  - ✅ JSON-Qualität evaluiert
  - ✅ Schema-Anpassungen

### 🚧 Phase 2: MVP (In Arbeit)

**Dauer:** 8 Wochen (Nov 2025 - Jan 2026)

- **Woche 5-6**: PostgreSQL-Integration
  - 🚧 DB-Setup
  - 🚧 Import-Script
  - 🚧 Migration existing JSONs
- **Woche 7-8**: Attachment-Processing
  - 📋 OCR-Integration (Tesseract)
  - 📋 PDF-Text-Extraktion
  - 📋 Storage-System
- **Woche 9**: Case-JSON-Linking
  - 📋 Case-Schema
  - 📋 Linking-Logic
  - 📋 Metriken-Berechnung
- **Woche 10-11**: REST-API
  - 📋 FastAPI-Setup
  - 📋 CRUD-Endpunkte
  - 📋 Authentication
  - 📋 OpenAPI-Dokumentation
- **Woche 12**: Testing & Optimierung
  - 📋 100+ E-Mails verarbeiten
  - 📋 Performance-Tuning
  - 📋 Bug-Fixes

### 📋 Phase 3: Production (Geplant)

**Dauer:** 4 Wochen (Jan - Feb 2026)

- **Woche 13**: Production-Deployment
- **Woche 14-15**: Monitoring & Fine-Tuning
- **Woche 16**: Dokumentation & Training

---

## 15. Anhang A: Verwendete Dateien

### A.1 Python-Scripts (Implementiert)

| Datei | Zweck | Status |
|-------|-------|--------|
| `run_agent.py` | Haupt-Orchestrierung | ✅ Fertig |
| `agents/imap_fetcher.py` | IMAP-Verbindung | ✅ Fertig |
| `agents/mail_parser.py` | E-Mail-Parsing | ✅ Fertig |
| `agents/attachment_handler.py` | Anhang-Verwaltung | ✅ Fertig |
| `agents/llm_request.py` | OLLAMA-Integration | ✅ Fertig |
| `utils/logger.py` | Logging | ✅ Fertig |
| `utils/file_handler.py` | Datei-Ops | ✅ Fertig |
| `utils/credentials.py` | Credentials-Manager | ✅ Fertig |
| `test_mail.py` | Connection-Test | ✅ Fertig |

### A.2 Konfigurationsdateien

| Datei | Zweck | Status |
|-------|-------|--------|
| `config/mail_config.json` | IMAP/SMTP-Einstellungen | ✅ Fertig |
| `config/secrets.json` | Credentials | ✅ Fertig |
| `requirements.txt` | Python-Dependencies | ✅ Fertig |
| `setup.sh` | Environment-Setup | ✅ Fertig |

### A.3 Prompt-Dateien

| Datei | Zweck | Status |
|-------|-------|--------|
| `catalog/prompts/extract_problem.txt` | Problem-Extraktion | ✅ Fertig |
| `catalog/prompts/extract_solution.txt` | Solution-Extraktion | ✅ Fertig |
| `catalog/prompts/extract_asset.txt` | Asset-Identifikation | ✅ Fertig |

### A.4 JSON-Schema-Templates

| Datei | Zweck | Status |
|-------|-------|--------|
| `catalog/json_store/problem_schema.json` | Problem-Struktur | ✅ Fertig |
| `catalog/json_store/solution_schema.json` | Solution-Struktur | ✅ Fertig |
| `catalog/json_store/asset_schema.json` | Asset-Struktur | ✅ Fertig |

---

## 16. Glossar

- **Asset**: IT-System, Anwendung oder Infrastruktur-Komponente
- **Case**: Vollständiger Support-Fall von Meldung bis Lösung (Phase 2)
- **JSONB**: PostgreSQL-binäres JSON-Datenformat
- **OLLAMA**: Lokales Large Language Model Framework
- **OCR**: Optical Character Recognition (Text aus Bildern)
- **PoC**: Proof of Concept (Machbarkeitsnachweis)
- **Reusability Score**: Bewertung der Wiederverwendbarkeit einer Lösung (0.0-1.0)
- **Schema Version**: Versionsnummer des JSON-Formats (Semantic Versioning)
- **UUID**: Universally Unique Identifier

---

**Dokument-Version**: 1.2  
**Letztes Update**: 15. November 2025  
**Nächstes Review**: 1. Dezember 2025 (nach Sprint 1)  
**Status**: Phase 1 ✅ | Phase 2 🚧 | Phase 3 📋