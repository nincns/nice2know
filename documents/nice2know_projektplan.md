# nice2know - Projektplan

**Version:** 1.0  
**Datum:** 15.11.2025  
**Status:** Konzeptphase  
**Verantwortlich:** Servicezentrum Informatik, EAH

---

## 1. Executive Summary

**nice2know** ist ein intelligentes Wissensmanagement-System, das E-Mail-basierte Support-Kommunikation automatisch in eine durchsuchbare, strukturierte Knowledge Base überführt. Durch KI-gestützte Analyse werden Probleme, Lösungen und betroffene IT-Assets extrahiert und in einer mehrdimensionalen JSON-Struktur persistiert.

### Kernziele
- Automatische Extraktion von Supportwissen aus E-Mail-Konversationen
- Strukturierte Ablage nach Problem-Lösung-Asset-Modell
- Wiederverwendbarkeit von Lösungen über Asset-Kategorien
- Reduzierung von Bearbeitungszeiten durch Wissenstransfer

---

## 2. Projektbeschreibung

### 2.1 Ausgangssituation
Das Servicezentrum Informatik erhält täglich Support-Anfragen per E-Mail. Diese enthalten wertvolles Wissen über:
- Wiederkehrende Probleme mit IT-Systemen
- Bewährte Lösungsansätze
- System-spezifische Konfigurationen
- Fehlerdiagnosen und Workarounds

Aktuell geht dieses Wissen nach Lösung des Tickets verloren oder ist nur über E-Mail-Suche auffindbar.

### 2.2 Projektvision
**nice2know** transformiert jeden Support-Case in strukturiertes Wissen:

```
E-Mail → KI-Analyse → Strukturierte Daten → Knowledge Base → Schnellere Lösungen
```

### 2.3 Mehrwert
1. **Für Supporter:** Schneller Zugriff auf bewährte Lösungen
2. **Für Assets:** Vollständige Problemhistorie pro System
3. **Für Organisation:** Identifikation systemischer Schwachstellen
4. **Für Onboarding:** Neue Mitarbeiter lernen aus realen Cases

### 2.4 Scope

#### In Scope
- E-Mail-Import mit Anhang-Verarbeitung
- KI-basierte Problem/Lösung-Extraktion
- Asset-Identifikation und -Katalogisierung
- JSON-Export für Datenbank-Integration
- Verlinkung verwandter Cases

#### Out of Scope (Phase 1)
- Automatische Ticket-Erstellung
- Echtzeit-Chat-Integration
- Predictive Maintenance
- Automatisierte Lösungsvorschläge während Ticket-Bearbeitung

---

## 3. Datenflussmodell

### 3.1 Überblick

```
┌─────────────────┐
│   E-Mail Box    │
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
│     LLM Processing Engine           │
│  ┌─────────────────────────────┐   │
│  │  1. Problem Extraction      │   │
│  │  2. Solution Identification │   │
│  │  3. Asset Recognition       │   │
│  │  4. Context Analysis        │   │
│  └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     JSON Generator                  │
│  ┌──────────┬──────────┬─────────┐ │
│  │ Problem  │ Solution │  Asset  │ │
│  │   JSON   │   JSON   │  JSON   │ │
│  └──────────┴──────────┴─────────┘ │
│           │                         │
│           ▼                         │
│     ┌──────────┐                   │
│     │   Case   │                   │
│     │   JSON   │                   │
│     └──────────┘                   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Knowledge Base Database          │
│  ┌─────────────────────────────┐   │
│  │  - Problems Collection      │   │
│  │  - Solutions Collection     │   │
│  │  - Assets Collection        │   │
│  │  - Cases Collection         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 3.2 Detaillierter Datenfluss

#### Phase 1: E-Mail Ingestion
```
Input: E-Mail (MIME Format)
├── Headers (From, To, Subject, Date, Message-ID)
├── Body (Plain Text / HTML)
└── Attachments []
    ├── Screenshots (PNG, JPG) → OCR
    ├── Logs (TXT, LOG) → Text Extraction
    ├── Dokumente (PDF, DOCX) → Text Extraction
    └── Sonstige → Referenz speichern
```

#### Phase 2: LLM Analysis
```
Input: Parsed Mail Content + Attachments
Process:
  1. Kontext-Analyse (Welches System? Welches Problem?)
  2. Problem-Extraktion (Symptome, Fehlermeldungen, Kontext)
  3. Lösungs-Identifikation (Schritte, Outcome, Validation)
  4. Asset-Mapping (Welches System ist betroffen?)
  5. Kategorisierung (Severity, Type, Reusability Score)
Output: Strukturierte Daten (Pre-JSON)
```

#### Phase 3: JSON Generation
```
Input: Strukturierte Daten
Process:
  1. Generiere Problem-JSON (leichtgewichtig)
  2. Generiere Solution-JSON(s) (detailliert, Steps)
  3. Identifiziere/Erstelle Asset-JSON (wenn neu)
  4. Erstelle Case-JSON (Linking)
  5. Validierung (Schema-Check, ID-Konsistenz)
Output: 3-4 JSON-Dateien pro Case
```

#### Phase 4: Persistence
```
Input: Validierte JSONs
Process:
  1. Upsert Asset (wenn bereits vorhanden: Update)
  2. Insert Problem
  3. Insert Solution(s)
  4. Insert Case (mit Referenzen)
  5. Update Cross-References
Output: Database Records + IDs
```

### 3.3 Anhang-Verarbeitungsstrategie

| Dateityp | Verarbeitung | Speicherort | Integration |
|----------|--------------|-------------|-------------|
| PNG/JPG | OCR (Tesseract) | Object Storage | Text → Problem Context |
| PDF | Text-Extraktion | Object Storage | Separate KB-Article oder Problem-Annex |
| TXT/LOG | Direktes Parsing | Inline in JSON | Array in `error_messages` |
| DOCX | Text-Extraktion | Object Storage | Separate KB-Article |
| Sonstige | Nur Metadaten | Object Storage | Manuelles Review Flag |

---

## 4. Systemarchitektur

### 4.1 Komponenten

```
┌──────────────────────────────────────────────────────────┐
│                     nice2know System                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┐        ┌──────────────────┐         │
│  │  Mail Fetcher  │───────▶│  Queue Manager   │         │
│  │  (IMAP/API)    │        │  (RabbitMQ/SQS)  │         │
│  └────────────────┘        └─────────┬────────┘         │
│                                       │                   │
│                                       ▼                   │
│                            ┌──────────────────┐          │
│                            │  Worker Pool     │          │
│                            │  - Mail Parser   │          │
│                            │  - LLM Processor │          │
│                            │  - JSON Gen      │          │
│                            └─────────┬────────┘          │
│                                      │                    │
│                                      ▼                    │
│  ┌────────────────────────────────────────────┐         │
│  │         Storage Layer                       │         │
│  ├──────────────────┬──────────────────────────┤        │
│  │  JSON Files      │   Knowledge Base DB      │        │
│  │  (Staging)       │   (MongoDB/PostgreSQL)   │        │
│  └──────────────────┴──────────────────────────┘        │
│                                                           │
│  ┌────────────────────────────────────────────┐         │
│  │         API Layer                           │         │
│  │  - REST API (CRUD Operations)               │         │
│  │  - Search API (Full-Text, Faceted)          │         │
│  │  - Analytics API (Metrics, Trends)          │         │
│  └────────────────────────────────────────────┘         │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Technologie-Stack (Empfehlung)

| Layer | Technologie | Begründung |
|-------|-------------|------------|
| Mail Fetcher | Python + IMAPlib | Standard, robust |
| Queue | RabbitMQ | Zuverlässig, Open Source |
| LLM Processing | Claude API (Anthropic) | Exzellente Extraction-Fähigkeiten |
| Worker Pool | Python + Celery | Skalierbar, etabliert |
| Database | MongoDB | Schema-flexibel für JSON |
| Object Storage | MinIO / S3 | Attachments |
| API | FastAPI (Python) | Schnell, moderne Async-Support |
| Frontend | React + TypeScript | (Optional, Phase 2) |

---

## 5. JSON-Datenstruktur

### 5.1 Übersicht der JSON-Typen

nice2know verwendet **4 separate JSON-Strukturen** pro Support-Case:

1. **Problem JSON** - Leichtgewichtig, schnelle Suche
2. **Solution JSON** - Detailliert, wiederverwendbar
3. **Asset JSON** - Katalog der IT-Systeme
4. **Case JSON** - Orchestrierung und Linking

### 5.2 Versionierung

Alle JSONs verwenden semantische Versionierung:
```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem"
}
```

---

## 6. Problem JSON

### 6.1 Zweck
Erfasst die **Problemstellung** aus der E-Mail in kompakter Form. Optimiert für schnelle Volltextsuche und Kategorisierung.

### 6.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_problem",
  "id": "prob_0cb386ae2c684a53a69e8a4a786a298e",
  "mail_id": "0cb386ae-2c68-4a53-a69e-8a4a786a298e",
  "asset_id": "asset_mailsystem_eah_01",
  "timestamp": "2025-11-15T10:35:57.424Z",
  "reporter": {
    "name": "Hentschke",
    "email": "hentschke@eah-jena.de",
    "department": "Servicezentrum Informatik"
  },
  "problem": {
    "title": "Mail-System nimmt keine eingehenden Mails entgegen",
    "description": "Das System verweigert die Annahme von E-Mails. Absender erhalten Bounce-Messages.",
    "symptoms": [
      "Eingehende Mails werden abgelehnt",
      "Mailhistorie fehlt idealerweise"
    ],
    "error_messages": [
      "SMTP 550 - Mailbox unavailable",
      "Lokales Spammodell blockiert Zustellung"
    ],
    "affected_functionality": [
      "E-Mail Empfang",
      "Mail-to-Know-System Integration"
    ]
  },
  "classification": {
    "category": "email",
    "subcategory": "incoming_mail",
    "severity": "high",
    "priority": "quick_win",
    "affected_users": "alle",
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

### 6.3 Schlüsselbeschreibung

| Schlüssel | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `schema_version` | String | Ja | Versionsnummer des JSON-Schemas |
| `type` | String | Ja | Immer "n2k_problem" |
| `id` | String | Ja | Eindeutige Problem-ID (prob_...) |
| `mail_id` | String | Ja | Referenz zur Original-Mail (aus E-Mail Message-ID) |
| `asset_id` | String | Ja | Referenz zum betroffenen Asset |
| `timestamp` | ISO8601 | Ja | Zeitpunkt der Problemmeldung |
| `reporter.name` | String | Ja | Name des Meldenden |
| `reporter.email` | String | Ja | E-Mail des Meldenden |
| `reporter.department` | String | Nein | Abteilung (für Statistiken) |
| `problem.title` | String | Ja | Kurze, prägnante Problembeschreibung (max 200 Zeichen) |
| `problem.description` | String | Ja | Ausführliche Beschreibung |
| `problem.symptoms` | Array[String] | Ja | Liste beobachtbarer Symptome |
| `problem.error_messages` | Array[String] | Nein | Fehlermeldungen (Logs, Screenshots via OCR) |
| `problem.affected_functionality` | Array[String] | Nein | Welche Funktionen sind betroffen? |
| `classification.category` | Enum | Ja | Hauptkategorie (siehe 6.4) |
| `classification.subcategory` | String | Nein | Feingranulare Kategorie |
| `classification.severity` | Enum | Ja | low, medium, high, critical |
| `classification.priority` | String | Nein | Z.B. "quick_win" aus Original-Mail |
| `classification.affected_users` | String | Nein | Anzahl/Gruppe betroffener Nutzer |
| `classification.business_impact` | Enum | Nein | low, medium, high, critical |
| `context.time_of_occurrence` | ISO8601 | Nein | Wann trat das Problem auf? |
| `context.frequency` | Enum | Nein | once, intermittent, continuous |
| `context.environment` | Enum | Nein | production, staging, development |
| `context.related_changes` | Array[String] | Nein | Kürzliche Änderungen am System |
| `status` | Enum | Ja | open, in_progress, resolved, closed |
| `resolution_date` | ISO8601 | Nein | Wann wurde das Problem gelöst? |

### 6.4 Kategorien (Enumerations)

#### category
```
- email (E-Mail-Systeme)
- identity (LDAP, Active Directory, SSO)
- network (Switches, Firewalls, VPN)
- application (Business-Apps, ERP, LMS)
- infrastructure (Server, Storage, Backup)
- client (Workstations, Mobile Devices)
- security (Malware, Zugriffsprobleme)
- other
```

---

## 7. Solution JSON

### 7.1 Zweck
Dokumentiert **Lösungswege** in wiederverwendbarer Form. Kann auf mehrere Probleme anwendbar sein. Enthält detaillierte Schritt-für-Schritt-Anleitungen.

### 7.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_solution",
  "id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
  "problem_ids": [
    "prob_0cb386ae2c684a53a69e8a4a786a298e"
  ],
  "asset_id": "asset_mailsystem_eah_01",
  "timestamp": "2025-11-15T14:20:00Z",
  "solution": {
    "title": "E-Mail Import in Knowledge Base aktivieren",
    "type": "configuration",
    "approach": "workaround",
    "description": "Integration des Mail-Systems mit der Knowledge Base durch Import-Funktion. Normaler Mailfluss bleibt erhalten, zusätzlich werden Konversationen automatisch in die Wissensdatenbank übernommen.",
    "prerequisites": [
      "Zugriff auf Mail-System Konfiguration",
      "Knowledge Base muss erreichbar sein",
      "API-Token für Knowledge Base"
    ],
    "steps": [
      {
        "step_number": 1,
        "action": "Knowledge Base Import-API konfigurieren",
        "details": "API-Endpoint /api/import/mail in der Mail-System Config eintragen",
        "command": "echo 'KB_IMPORT_URL=https://kb.eah-jena.de/api/import/mail' >> /etc/mail/config.env",
        "expected_result": "Config-Datei enthält neue Variable",
        "estimated_duration": "2 min"
      },
      {
        "step_number": 2,
        "action": "Mail-Routing anpassen",
        "details": "Eingehende Mails zusätzlich an KB-Import weiterleiten",
        "command": null,
        "expected_result": "Mails werden dupliziert (Normal-Delivery + KB-Import)",
        "estimated_duration": "5 min"
      },
      {
        "step_number": 3,
        "action": "Test-Mail senden",
        "details": "Testmail an System senden und KB-Import verifizieren",
        "command": null,
        "expected_result": "Mail erscheint sowohl in Mailbox als auch in Knowledge Base",
        "estimated_duration": "3 min"
      }
    ],
    "validation": {
      "success_criteria": [
        "Mails werden regulär zugestellt",
        "KB-Import läuft automatisch",
        "Keine Fehler in Mail-Logs"
      ],
      "test_procedure": "Test-Mail senden und nach 5 Minuten in KB suchen",
      "rollback_plan": "Import-URL aus Config entfernen, Mail-Service neu starten"
    },
    "outcome": {
      "tested": true,
      "successful": true,
      "side_effects": [
        "Zusätzlicher Storage-Verbrauch für KB-Daten"
      ],
      "performance_impact": "minimal"
    }
  },
  "metadata": {
    "author": "Hentschke",
    "source": "Support-Case 0cb386ae",
    "reusability_score": 0.85,
    "complexity": "low",
    "estimated_time": "10 min",
    "required_skills": [
      "Mail-Server Administration",
      "Basiskenntnisse API-Integration"
    ]
  },
  "related_solutions": [
    "sol_xyz123..." 
  ],
  "tags": [
    "mail",
    "knowledge-base",
    "integration",
    "quick-win"
  ]
}
```

### 7.3 Schlüsselbeschreibung

| Schlüssel | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `schema_version` | String | Ja | Versionsnummer des JSON-Schemas |
| `type` | String | Ja | Immer "n2k_solution" |
| `id` | String | Ja | Eindeutige Solution-ID (sol_...) |
| `problem_ids` | Array[String] | Ja | Liste aller Probleme, die diese Lösung adressiert |
| `asset_id` | String | Ja | Asset, für das diese Lösung gilt |
| `timestamp` | ISO8601 | Ja | Zeitpunkt der Lösungsdokumentation |
| `solution.title` | String | Ja | Prägnanter Lösungstitel |
| `solution.type` | Enum | Ja | configuration, bugfix, workaround, update, other |
| `solution.approach` | Enum | Ja | permanent_fix, workaround, temporary |
| `solution.description` | String | Ja | Ausführliche Beschreibung der Lösung |
| `solution.prerequisites` | Array[String] | Nein | Was muss vorhanden/erfüllt sein? |
| `solution.steps` | Array[Object] | Ja | Schrittweise Anleitung (siehe 7.4) |
| `solution.validation.success_criteria` | Array[String] | Nein | Woran erkennt man Erfolg? |
| `solution.validation.test_procedure` | String | Nein | Wie testet man die Lösung? |
| `solution.validation.rollback_plan` | String | Nein | Was tun, wenn es schiefgeht? |
| `solution.outcome.tested` | Boolean | Ja | Wurde die Lösung tatsächlich getestet? |
| `solution.outcome.successful` | Boolean | Nein | War der Test erfolgreich? |
| `solution.outcome.side_effects` | Array[String] | Nein | Bekannte Nebenwirkungen |
| `solution.outcome.performance_impact` | Enum | Nein | none, minimal, moderate, significant |
| `metadata.author` | String | Nein | Wer hat die Lösung dokumentiert? |
| `metadata.source` | String | Nein | Woher stammt die Lösung? |
| `metadata.reusability_score` | Float | Nein | 0.0-1.0, wie wiederverwendbar ist die Lösung? |
| `metadata.complexity` | Enum | Nein | low, medium, high |
| `metadata.estimated_time` | String | Nein | Geschätzte Umsetzungsdauer |
| `metadata.required_skills` | Array[String] | Nein | Benötigte Fähigkeiten |
| `related_solutions` | Array[String] | Nein | IDs verwandter Lösungen |
| `tags` | Array[String] | Nein | Freie Tags für Suche |

### 7.4 Step-Objekt Struktur

```json
{
  "step_number": 1,
  "action": "Kurze Beschreibung der Aktion",
  "details": "Ausführliche Erklärung",
  "command": "Optional: Auszuführender Befehl",
  "expected_result": "Was sollte passieren?",
  "estimated_duration": "Zeitangabe",
  "warnings": ["Optionale Warnungen"]
}
```

---

## 8. Asset JSON

### 8.1 Zweck
Katalogisiert **IT-Assets** (Systeme, Anwendungen, Infrastruktur). Fungiert als Bindeglied zwischen Problemen und Lösungen. Ermöglicht Asset-basierte Analysen.

### 8.2 Schema

```json
{
  "schema_version": "1.0.0",
  "type": "n2k_asset",
  "id": "asset_mailsystem_eah_01",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-15T14:20:00Z",
  "asset": {
    "name": "EAH Mail-System",
    "display_name": "Zentrales E-Mail-System",
    "description": "Hochschulweites E-Mail-System für Mitarbeitende und Studierende",
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
      "asset_id": "asset_ldap_eah_01"
    },
    {
      "name": "Spam-Filter",
      "purpose": "Mail Security",
      "asset_id": "asset_spamfilter_01"
    },
    {
      "name": "Knowledge Base",
      "purpose": "Mail Import",
      "asset_id": "asset_n2k_kb_01"
    }
  ],
  "ownership": {
    "department": "Servicezentrum Informatik",
    "primary_contact": "Hentschke",
    "email": "it-support@eah-jena.de",
    "escalation_contact": null
  },
  "documentation": {
    "wiki_url": "https://wiki.eah-jena.de/mailsystem",
    "api_docs": null,
    "runbook": "https://docs.eah-jena.de/runbooks/mail",
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
      "Spam-Filter Fehlalarme",
      "LDAP Sync-Probleme"
    ]
  },
  "related_assets": [
    "asset_ldap_eah_01",
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

### 8.3 Schlüsselbeschreibung

| Schlüssel | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `schema_version` | String | Ja | Versionsnummer des JSON-Schemas |
| `type` | String | Ja | Immer "n2k_asset" |
| `id` | String | Ja | Eindeutige Asset-ID (asset_...) |
| `created_at` | ISO8601 | Ja | Wann wurde der Asset-Eintrag erstellt? |
| `updated_at` | ISO8601 | Ja | Letzte Aktualisierung |
| `asset.name` | String | Ja | Technischer Name (eindeutig) |
| `asset.display_name` | String | Ja | Benutzerfreundlicher Name |
| `asset.description` | String | Ja | Was macht dieses Asset? |
| `asset.type` | Enum | Ja | Asset-Typ (siehe 8.4) |
| `asset.category` | Enum | Ja | Übergeordnete Kategorie |
| `asset.status` | Enum | Ja | active, inactive, decommissioned, planned |
| `asset.criticality` | Enum | Ja | low, medium, high, critical |
| `technical.software` | String | Nein | Softwarename |
| `technical.version` | String | Nein | Versionsnummer |
| `technical.platform` | String | Nein | Betriebssystem/Plattform |
| `technical.architecture` | String | Nein | CPU-Architektur |
| `technical.deployment` | Enum | Nein | on-premise, cloud, hybrid |
| `technical.vendor` | String | Nein | Hersteller/Anbieter |
| `technical.license` | String | Nein | Lizenzmodell |
| `integrations` | Array[Object] | Nein | Verbundene Systeme (siehe 8.5) |
| `ownership.department` | String | Ja | Verantwortliche Abteilung |
| `ownership.primary_contact` | String | Ja | Hauptansprechpartner |
| `ownership.email` | String | Ja | Kontakt-E-Mail |
| `ownership.escalation_contact` | String | Nein | Eskalationskontakt |
| `documentation.wiki_url` | String | Nein | Link zur Dokumentation |
| `documentation.api_docs` | String | Nein | API-Dokumentation |
| `documentation.runbook` | String | Nein | Betriebshandbuch |
| `documentation.architecture_diagram` | String | Nein | Architekturdiagramm |
| `maintenance.last_update` | Date | Nein | Letztes Update |
| `maintenance.update_frequency` | String | Nein | Update-Rhythmus |
| `maintenance.backup_schedule` | String | Nein | Backup-Frequenz |
| `maintenance.monitoring` | Boolean | Nein | Wird überwacht? |
| `maintenance.sla` | String | Nein | Service Level Agreement |
| `knowledge.known_problems` | Array[String] | Nein | IDs bekannter Probleme |
| `knowledge.available_solutions` | Array[String] | Nein | IDs verfügbarer Lösungen |
| `knowledge.total_incidents` | Integer | Nein | Gesamtzahl Incidents |
| `knowledge.mean_time_to_resolve` | String | Nein | Durchschnittliche Lösungszeit |
| `knowledge.common_issues` | Array[String] | Nein | Häufige Probleme (Freitext) |
| `related_assets` | Array[String] | Nein | IDs verwandter Assets |
| `tags` | Array[String] | Nein | Freie Tags |

### 8.4 Asset-Typen

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

Types (Auswahl):
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

### 8.5 Integration-Objekt

```json
{
  "name": "System-Name",
  "purpose": "Zweck der Integration",
  "asset_id": "asset_...",
  "interface": "API|LDAP|Database|File",
  "status": "active|inactive"
}
```

---

## 9. Case JSON

### 9.1 Zweck
Orchestriert den **vollständigen Support-Case**. Verlinkt Problem, Lösung(en) und Asset. Dokumentiert den Lösungsweg inklusive Alternativen.

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
    "title": "Mail-System Import-Fehler",
    "status": "resolved",
    "priority": "high",
    "reporter": {
      "name": "Hentschke",
      "email": "hentschke@eah-jena.de"
    }
  },
  "mail_metadata": {
    "subject": "Re: Mail-System Probleme",
    "from": "hentschke@eah-jena.de",
    "to": "it-support@eah-jena.de",
    "date": "2025-11-15T11:35:00Z",
    "thread_id": "thread_abc123",
    "has_attachments": false,
    "attachments": []
  },
  "entities": {
    "problem_id": "prob_0cb386ae2c684a53a69e8a4a786a298e",
    "asset_id": "asset_mailsystem_eah_01",
    "applied_solution_id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
    "alternative_solutions": []
  },
  "resolution_path": [
    {
      "step": 1,
      "timestamp": "2025-11-15T11:40:00Z",
      "action": "Problem analysiert",
      "actor": "Hentschke",
      "notes": "SMTP-Logs zeigen Rejection wegen fehlendem KB-Import"
    },
    {
      "step": 2,
      "timestamp": "2025-11-15T13:00:00Z",
      "action": "Lösung identifiziert",
      "actor": "Hentschke",
      "solution_id": "sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0",
      "notes": "KB-Import aktivieren als Lösung gewählt"
    },
    {
      "step": 3,
      "timestamp": "2025-11-15T14:10:00Z",
      "action": "Lösung implementiert",
      "actor": "Hentschke",
      "outcome": "success"
    },
    {
      "step": 4,
      "timestamp": "2025-11-15T14:20:00Z",
      "action": "Lösung validiert",
      "actor": "Hentschke",
      "outcome": "success",
      "notes": "Test-Mail erfolgreich in KB importiert"
    }
  ],
  "conversation_context": {
    "thread_messages": 3,
    "participants": [
      "hentschke@eah-jena.de",
      "it-support@eah-jena.de"
    ],
    "conversation_summary": "Mail-System lehnte Mails ab. Ursache: Fehlendes KB-Import Feature. Lösung: KB-Import aktiviert."
  },
  "knowledge_base_integration": {
    "kb_article_generated": true,
    "kb_article_id": "kb_art_001",
    "kb_article_url": "https://kb.eah-jena.de/articles/001",
    "indexed_at": "2025-11-15T14:30:00Z"
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

### 9.3 Schlüsselbeschreibung

| Schlüssel | Typ | Pflicht | Beschreibung |
|-----------|-----|---------|--------------|
| `schema_version` | String | Ja | Versionsnummer des JSON-Schemas |
| `type` | String | Ja | Immer "n2k_case" |
| `id` | String | Ja | Eindeutige Case-ID (case_...) |
| `mail_id` | String | Ja | Original E-Mail Message-ID |
| `created_at` | ISO8601 | Ja | Zeitpunkt der Case-Erstellung |
| `resolved_at` | ISO8601 | Nein | Zeitpunkt der Lösung |
| `case.title` | String | Ja | Case-Titel (aus Mail-Subject) |
| `case.status` | Enum | Ja | open, in_progress, resolved, closed, reopened |
| `case.priority` | Enum | Ja | low, medium, high, critical |
| `case.reporter` | Object | Ja | Name und E-Mail des Meldenden |
| `mail_metadata.subject` | String | Ja | E-Mail Betreff |
| `mail_metadata.from` | String | Ja | Absender |
| `mail_metadata.to` | String | Ja | Empfänger |
| `mail_metadata.date` | ISO8601 | Ja | E-Mail Datum |
| `mail_metadata.thread_id` | String | Nein | Thread-ID (bei Konversationen) |
| `mail_metadata.has_attachments` | Boolean | Ja | Anhänge vorhanden? |
| `mail_metadata.attachments` | Array[Object] | Nein | Liste der Anhänge (siehe 9.4) |
| `entities.problem_id` | String | Ja | Referenz zum Problem |
| `entities.asset_id` | String | Ja | Referenz zum Asset |
| `entities.applied_solution_id` | String | Nein | Welche Lösung wurde verwendet? |
| `entities.alternative_solutions` | Array[String] | Nein | Andere mögliche Lösungen |
| `resolution_path` | Array[Object] | Nein | Chronologischer Lösungsweg (siehe 9.5) |
| `conversation_context.thread_messages` | Integer | Nein | Anzahl Nachrichten im Thread |
| `conversation_context.participants` | Array[String] | Nein | Beteiligte E-Mail-Adressen |
| `conversation_context.conversation_summary` | String | Nein | KI-generierte Zusammenfassung |
| `knowledge_base_integration.kb_article_generated` | Boolean | Nein | KB-Artikel erstellt? |
| `knowledge_base_integration.kb_article_id` | String | Nein | ID des KB-Artikels |
| `knowledge_base_integration.kb_article_url` | String | Nein | URL zum KB-Artikel |
| `knowledge_base_integration.indexed_at` | ISO8601 | Nein | Zeitpunkt der Indizierung |
| `metrics.time_to_first_response` | String | Nein | Reaktionszeit |
| `metrics.time_to_resolution` | String | Nein | Gesamtlösungszeit |
| `metrics.reopened` | Boolean | Nein | Wurde Case wiedereröffnet? |
| `metrics.satisfaction_score` | Float | Nein | 1.0-5.0, falls erfasst |
| `tags` | Array[String] | Nein | Freie Tags |

### 9.4 Attachment-Objekt

```json
{
  "filename": "error_screenshot.png",
  "type": "image/png",
  "size_bytes": 2458624,
  "storage_path": "/attachments/2025/11/error_screenshot_abc123.png",
  "storage_url": "https://storage.eah-jena.de/n2k/attachments/...",
  "extracted_text": "SMTP Error 550: Mailbox unavailable",
  "ocr_applied": true,
  "processing_status": "indexed"
}
```

### 9.5 Resolution Path Step-Objekt

```json
{
  "step": 1,
  "timestamp": "2025-11-15T11:40:00Z",
  "action": "Problem analysiert|Lösung getestet|...",
  "actor": "Name der Person",
  "solution_id": "sol_...",
  "outcome": "success|failed|partial",
  "notes": "Freitext-Notizen"
}
```

---

## 10. ID-Konventionen

### 10.1 ID-Format

Alle IDs folgen dem Schema: `{type}_{uuid}`

| Typ | Präfix | Beispiel |
|-----|--------|----------|
| Problem | `prob_` | `prob_0cb386ae2c684a53a69e8a4a786a298e` |
| Solution | `sol_` | `sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0` |
| Asset | `asset_` | `asset_mailsystem_eah_01` |
| Case | `case_` | `case_0cb386ae2c684a53a69e8a4a786a298e` |
| KB Article | `kb_art_` | `kb_art_001` |

### 10.2 ID-Generierung

- **Problem/Case**: Verwenden die E-Mail Message-ID (ohne Sonderzeichen)
- **Solution**: UUID v4
- **Asset**: Manuell vergeben (sprechend) oder UUID bei automatischer Erstellung

---

## 11. Datenbank-Schema (Empfehlung)

### 11.1 MongoDB Collections

```javascript
// Collection: problems
{
  _id: ObjectId,
  problem_id: "prob_...",  // Indexed, Unique
  mail_id: "...",  // Indexed
  asset_id: "...",  // Indexed
  // ... rest of Problem JSON
  _metadata: {
    created_at: ISODate,
    updated_at: ISODate,
    version: 1
  }
}

// Collection: solutions
{
  _id: ObjectId,
  solution_id: "sol_...",  // Indexed, Unique
  problem_ids: ["prob_..."],  // Indexed (Array)
  asset_id: "...",  // Indexed
  // ... rest of Solution JSON
  _metadata: { ... }
}

// Collection: assets
{
  _id: ObjectId,
  asset_id: "asset_...",  // Indexed, Unique
  asset_name: "...",  // Indexed, Unique
  asset_type: "...",  // Indexed
  // ... rest of Asset JSON
  _metadata: { ... }
}

// Collection: cases
{
  _id: ObjectId,
  case_id: "case_...",  // Indexed, Unique
  mail_id: "...",  // Indexed
  problem_id: "...",  // Indexed
  asset_id: "...",  // Indexed
  applied_solution_id: "...",  // Indexed
  // ... rest of Case JSON
  _metadata: { ... }
}
```

### 11.2 Wichtige Indizes

```javascript
// Full-Text Search
db.problems.createIndex({
  "problem.title": "text",
  "problem.description": "text",
  "problem.symptoms": "text"
});

db.solutions.createIndex({
  "solution.title": "text",
  "solution.description": "text",
  "tags": "text"
});

// Performance Indizes
db.problems.createIndex({ "asset_id": 1, "status": 1 });
db.solutions.createIndex({ "asset_id": 1, "metadata.reusability_score": -1 });
db.cases.createIndex({ "created_at": -1 });
db.assets.createIndex({ "asset.type": 1, "asset.status": 1 });
```

---

## 12. Workflow & Prozesse

### 12.1 Standard-Workflow

```
1. E-Mail trifft ein
   ↓
2. Mail-Parser extrahiert Daten
   ↓
3. Queue: Neuer Job für LLM-Worker
   ↓
4. LLM-Worker analysiert E-Mail
   ├── Identifiziert Problem
   ├── Identifiziert Lösung (falls vorhanden)
   └── Identifiziert/Erstellt Asset
   ↓
5. JSON-Generator erstellt 3-4 JSONs
   ↓
6. Validierung (Schema-Check)
   ↓
7. Speicherung in Datenbank
   ├── Problem → problems collection
   ├── Solution → solutions collection
   ├── Asset → assets collection (upsert)
   └── Case → cases collection
   ↓
8. Update Cross-References
   ├── Asset.known_problems += problem_id
   └── Asset.available_solutions += solution_id
   ↓
9. Optional: KB-Artikel generieren
   ↓
10. Fertig ✓
```

### 12.2 Sonderfälle

#### Fall 1: E-Mail ohne Lösung
```
Problem wird erfasst, aber:
- entities.applied_solution_id = null
- case.status = "open"
- Kein Solution-JSON erstellt
```

#### Fall 2: Mehrere Lösungsversuche
```
- Mehrere Solution-JSONs (sol_1, sol_2, sol_3)
- resolution_path dokumentiert alle Versuche
- entities.applied_solution_id = erfolgreichste Lösung
- entities.alternative_solutions = [andere]
```

#### Fall 3: Neues Asset
```
- Asset wird automatisch erstellt
- Minimale Daten (Name, Type aus LLM-Analyse)
- ownership.department = "Unknown" → Manuelles Review
- asset.status = "pending_verification"
```

#### Fall 4: E-Mail mit Anhängen
```
- Anhänge werden in Object Storage gespeichert
- OCR/Text-Extraktion läuft asynchron
- mail_metadata.attachments wird befüllt
- Extracted Text → problem.error_messages (falls relevant)
```

---

## 13. API-Endpunkte (Vorschlag)

### 13.1 REST API

```
# Problems
GET    /api/v1/problems              # Liste aller Probleme
GET    /api/v1/problems/{id}         # Spezifisches Problem
POST   /api/v1/problems              # Neues Problem anlegen
PUT    /api/v1/problems/{id}         # Problem aktualisieren
DELETE /api/v1/problems/{id}         # Problem löschen

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
GET    /api/v1/search/advanced       # Faceted Search

# Analytics
GET    /api/v1/analytics/assets/{id}/problems     # Alle Probleme eines Assets
GET    /api/v1/analytics/assets/{id}/solutions    # Alle Lösungen eines Assets
GET    /api/v1/analytics/trends                   # Trend-Analysen
```

### 13.2 Query-Parameter

```
# Pagination
?page=1&limit=20

# Filtering
?asset_id=asset_mailsystem_eah_01
?status=open
?severity=high
?category=email

# Sorting
?sort_by=created_at&order=desc

# Full-Text Search
?q=mail+nicht+zugestellt
```

---

## 14. Meilensteine & Zeitplan

### Phase 1: Proof of Concept (4 Wochen)
- **Woche 1-2**: Setup Infrastruktur
  - Mail-Fetcher implementieren
  - LLM-Integration (Claude API)
  - Basis-JSON-Generator
- **Woche 3**: Datenbank-Schema
  - MongoDB Setup
  - Collection-Design
  - Indizes erstellen
- **Woche 4**: Testing & Iteration
  - 10 Test-E-Mails verarbeiten
  - JSON-Qualität evaluieren
  - Schema-Anpassungen

### Phase 2: MVP (8 Wochen)
- **Woche 5-6**: Vollständiger Workflow
  - Queue-System
  - Worker-Pool
  - Error-Handling
- **Woche 7-8**: Anhang-Verarbeitung
  - OCR-Integration
  - Storage-System
  - PDF-Extraktion
- **Woche 9-10**: API-Entwicklung
  - REST Endpoints
  - Authentifizierung
  - Dokumentation (OpenAPI)
- **Woche 11-12**: Testing & Optimierung
  - 100+ E-Mails verarbeiten
  - Performance-Tuning
  - Bug-Fixes

### Phase 3: Production (4 Wochen)
- **Woche 13**: Produktiv-Deployment
- **Woche 14-15**: Monitoring & Finetuning
- **Woche 16**: Dokumentation & Training

---

## 15. Risiken & Mitigationen

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| LLM extrahiert falsche Daten | Mittel | Hoch | Human-Review-Flag bei niedriger Confidence |
| Schema-Änderungen brechen Kompatibilität | Niedrig | Hoch | Versionierung, Migration-Scripts |
| E-Mail-Attachments zu groß | Mittel | Mittel | Size-Limit, Compression |
| Datenschutz-Bedenken | Mittel | Hoch | Anonymisierung personenbezogener Daten |
| LLM-API-Kosten zu hoch | Niedrig | Mittel | Batching, Caching, Rate-Limiting |

---

## 16. Erfolgsmetriken

### KPIs (nach 6 Monaten)
- **Wissenserfassung**: >80% aller Support-E-Mails automatisch verarbeitet
- **Zeitersparnis**: 30% Reduktion in Time-to-Resolution für wiederkehrende Probleme
- **Wissenswiederverwendung**: 40% der Cases nutzen existierende Solutions
- **Datenqualität**: <5% fehlerhafte Extractions (gemessen an Human-Review)
- **User Adoption**: 70% der Support-Mitarbeitenden nutzen KB aktiv

---

## 17. Nächste Schritte

1. **Review & Approval**: Projektplan mit Stakeholdern besprechen
2. **Technologie-Evaluation**: Claude API vs. alternative LLMs
3. **Ressourcen-Planung**: Entwickler, Server, Budget
4. **Proof of Concept**: Erste 10 E-Mails manuell verarbeiten
5. **Iteratives Refinement**: JSON-Schema basierend auf Realität anpassen

---

## Anhang A: Beispiel-Datenfluss

### Input: Support-E-Mail
```
From: hentschke@eah-jena.de
To: it-support@eah-jena.de
Subject: Mail-System nimmt keine Mails an
Date: 15.11.2025, 11:35

Hallo Team,

unser Mail-System lehnt eingehende E-Mails ab. 
Absender erhalten Bounce-Messages mit "SMTP 550".
Das lokale Spammodell scheint involviert zu sein.

Vorschlag: Knowledge-Base-Import aktivieren, damit 
solche Cases automatisch erfasst werden.

Gruß,
Hentschke
```

### Output: 4 JSON-Dateien

1. **prob_0cb386ae...json** (Problem)
2. **sol_a7b9c3d4...json** (Solution)
3. **asset_mailsystem_eah_01.json** (Asset, ggf. Update)
4. **case_0cb386ae...json** (Case)

*(Detaillierte JSONs siehe Kapitel 6-9)*

---

## Anhang B: Glossar

- **Asset**: IT-System, Anwendung oder Infrastruktur-Komponente
- **Case**: Ein vollständiger Support-Fall von Meldung bis Lösung
- **LLM**: Large Language Model (KI für Text-Analyse)
- **OCR**: Optical Character Recognition (Text aus Bildern)
- **Reusability Score**: Bewertung, wie oft eine Lösung wiederverwendbar ist
- **Resolution Path**: Chronologischer Ablauf der Lösungsfindung
- **Schema Version**: Versionsnummer des JSON-Formats
- **UUID**: Universally Unique Identifier

---

## Anhang C: Kontakt & Verantwortlichkeiten

**Projektleitung**: [Name]  
**Technische Leitung**: [Name]  
**Product Owner**: Servicezentrum Informatik  
**Stakeholder**: IT-Leitung, Support-Team, Datenschutzbeauftragter

---

**Dokumentversion**: 1.0  
**Letztes Update**: 15.11.2025  
**Nächstes Review**: 01.12.2025
