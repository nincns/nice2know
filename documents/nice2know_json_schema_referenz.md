# nice2know - JSON Schema Referenz

**Version:** 1.0.0  
**Datum:** 15.11.2025  
**Zweck:** Vollständige Referenz aller JSON-Schlüssel für das nice2know Knowledge Base System

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Problem JSON](#problem-json)
3. [Solution JSON](#solution-json)
4. [Asset JSON](#asset-json)
5. [Case JSON](#case-json)
6. [Gemeinsame Datentypen](#gemeinsame-datentypen)
7. [Enumerationen](#enumerationen)
8. [Validierungsregeln](#validierungsregeln)

---

## Übersicht

### JSON-Typen in nice2know

nice2know verwendet vier separate JSON-Strukturen zur Abbildung von Support-Wissen:

| JSON-Typ | Präfix | Zweck | Größe |
|----------|--------|-------|-------|
| Problem | `n2k_problem` | Problembeschreibung | Klein (~2-5 KB) |
| Solution | `n2k_solution` | Lösungsdokumentation | Mittel (~5-15 KB) |
| Asset | `n2k_asset` | IT-Asset-Katalog | Mittel (~3-10 KB) |
| Case | `n2k_case` | Case-Orchestrierung | Klein (~3-7 KB) |

### Schema-Versionierung

Alle JSON-Dokumente enthalten:
```json
{
  "schema_version": "1.0.0",
  "type": "n2k_[problem|solution|asset|case]"
}
```

**Versionierung**: Semantisches Versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking Changes im Schema
- **MINOR**: Neue optionale Felder
- **PATCH**: Bugfixes, Dokumentation

---

## Problem JSON

### Metadaten-Schlüssel

#### `schema_version`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: Semantic Versioning (z.B. "1.0.0")
- **Beschreibung**: Version des JSON-Schemas
- **Beispiel**: `"1.0.0"`
- **Verwendung**: Für Schema-Migration und Kompatibilitätsprüfung

#### `type`
- **Typ**: String
- **Pflicht**: Ja
- **Wert**: `"n2k_problem"` (konstant)
- **Beschreibung**: Identifiziert den JSON-Typ
- **Beispiel**: `"n2k_problem"`
- **Verwendung**: Routing, Validierung

#### `id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `prob_{uuid}` oder `prob_{mail_id_sanitized}`
- **Länge**: 37-64 Zeichen
- **Beschreibung**: Eindeutige Problem-ID
- **Beispiel**: `"prob_0cb386ae2c684a53a69e8a4a786a298e"`
- **Verwendung**: Primary Key, Referenzierung in Solution/Case
- **Index**: Unique, Primary

#### `mail_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: UUID oder E-Mail Message-ID (sanitized)
- **Beschreibung**: Referenz zur Original-E-Mail
- **Beispiel**: `"0cb386ae-2c68-4a53-a69e-8a4a786a298e"`
- **Verwendung**: Rückverfolgung zur Quell-E-Mail
- **Index**: Non-Unique

#### `asset_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `asset_{identifier}`
- **Beschreibung**: Referenz zum betroffenen Asset
- **Beispiel**: `"asset_mailsystem_eah_01"`
- **Verwendung**: Foreign Key zu Asset JSON, Asset-basierte Queries
- **Index**: Non-Unique, für Aggregationen

#### `timestamp`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ`
- **Beschreibung**: Zeitpunkt der Problemmeldung
- **Beispiel**: `"2025-11-15T10:35:57.424Z"`
- **Verwendung**: Zeitreihenanalyse, Sortierung
- **Index**: Range-Index für Queries

### Reporter-Objekt

#### `reporter.name`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 1-200 Zeichen
- **Beschreibung**: Name der meldenden Person
- **Beispiel**: `"Hentschke"`
- **Verwendung**: Kontaktinformation, Statistiken
- **Datenschutz**: Ggf. pseudonymisieren bei Export

#### `reporter.email`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: RFC 5322 E-Mail
- **Beschreibung**: E-Mail-Adresse des Meldenden
- **Beispiel**: `"hentschke@eah-jena.de"`
- **Verwendung**: Kontaktaufnahme, Statistiken
- **Datenschutz**: Ggf. pseudonymisieren bei Export

#### `reporter.department`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 1-200 Zeichen
- **Beschreibung**: Abteilung/Organisationseinheit
- **Beispiel**: `"Servicezentrum Informatik"`
- **Verwendung**: Organisationsstatistiken, Eskalation

### Problem-Objekt

#### `problem.title`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 10-200 Zeichen
- **Beschreibung**: Kurze, prägnante Problembeschreibung
- **Beispiel**: `"Mail-System nimmt keine eingehenden Mails entgegen"`
- **Verwendung**: Listen-Ansicht, Volltextsuche, Dashboard
- **Index**: Full-Text-Index
- **Best Practice**: Aktive Formulierung, spezifisch

#### `problem.description`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 50-5000 Zeichen
- **Beschreibung**: Ausführliche Problembeschreibung
- **Beispiel**: `"Das System verweigert die Annahme von E-Mails. Absender erhalten Bounce-Messages."`
- **Verwendung**: Detail-Ansicht, Kontext für LLM
- **Index**: Full-Text-Index
- **Best Practice**: Wer, Was, Wann, Wo, Wie

#### `problem.symptoms`
- **Typ**: Array[String]
- **Pflicht**: Ja (min. 1 Element)
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Liste beobachtbarer Symptome
- **Beispiel**: `["Eingehende Mails werden abgelehnt", "Mailhistorie fehlt"]`
- **Verwendung**: Problem-Matching, Diagnostik
- **Index**: Array-Index für Multi-Value-Search
- **Best Practice**: Beobachtbar, messbar, spezifisch

#### `problem.error_messages`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 5-2000 Zeichen
- **Beschreibung**: Fehlermeldungen aus Logs, Screenshots (OCR)
- **Beispiel**: `["SMTP 550 - Mailbox unavailable", "Connection timeout"]`
- **Verwendung**: Exakte Error-Suche, Debugging
- **Index**: Full-Text-Index
- **Best Practice**: Originalfehlermeldungen, Stack Traces

#### `problem.affected_functionality`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 5-200 Zeichen
- **Beschreibung**: Welche Funktionen/Features sind betroffen?
- **Beispiel**: `["E-Mail Empfang", "Mail-to-Know-System Integration"]`
- **Verwendung**: Impact-Analyse, Priorisierung

### Classification-Objekt

#### `classification.category`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: Siehe [Enumerationen](#category-enum)
- **Beschreibung**: Hauptkategorie des Problems
- **Beispiel**: `"email"`
- **Verwendung**: Faceted Search, Routing zu Experten
- **Index**: Category-Index

#### `classification.subcategory`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 3-100 Zeichen
- **Beschreibung**: Feingranulare Kategorisierung
- **Beispiel**: `"incoming_mail"`
- **Verwendung**: Detaillierte Filterung
- **Best Practice**: Hierarchisch zu category

#### `classification.severity`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `low`, `medium`, `high`, `critical`
- **Beschreibung**: Schweregrad des Problems
- **Beispiel**: `"high"`
- **Verwendung**: Priorisierung, SLA-Steuerung, Eskalation
- **Mapping**:
  - `low`: Kosmetisch, Workaround vorhanden
  - `medium`: Funktionalität eingeschränkt
  - `high`: Wichtige Funktion ausgefallen
  - `critical`: Systemausfall, viele Nutzer betroffen

#### `classification.priority`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 3-50 Zeichen
- **Beschreibung**: Business-Priorität (ergänzend zu severity)
- **Beispiel**: `"quick_win"`
- **Verwendung**: Roadmap-Planung, Sprint-Planung
- **Mögliche Werte**: `"quick_win"`, `"strategic"`, `"must_have"`, `"nice_to_have"`

#### `classification.affected_users`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 1-100 Zeichen
- **Beschreibung**: Anzahl/Gruppe betroffener Nutzer
- **Beispiel**: `"alle"`, `"~50 Studierende"`, `"Abteilung IT"`
- **Verwendung**: Impact-Berechnung

#### `classification.business_impact`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `low`, `medium`, `high`, `critical`
- **Beschreibung**: Auswirkung auf Geschäftsprozesse
- **Beispiel**: `"critical"`
- **Verwendung**: Management-Reporting, Priorisierung

### Context-Objekt

#### `context.time_of_occurrence`
- **Typ**: String (ISO8601)
- **Pflicht**: Nein
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Wann trat das Problem erstmals auf?
- **Beispiel**: `"2025-11-15T11:35:00Z"`
- **Verwendung**: Zeitkorrelation mit Changes/Deployments
- **Hinweis**: Kann von `timestamp` abweichen (Meldung vs. Auftreten)

#### `context.frequency`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `once`, `intermittent`, `continuous`
- **Beschreibung**: Wie häufig tritt das Problem auf?
- **Beispiel**: `"continuous"`
- **Verwendung**: Root-Cause-Analyse, Priorisierung
- **Mapping**:
  - `once`: Einmaliges Ereignis
  - `intermittent`: Sporadisch, schwer reproduzierbar
  - `continuous`: Dauerhaft, jederzeit reproduzierbar

#### `context.environment`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `production`, `staging`, `development`, `test`
- **Beschreibung**: In welcher Umgebung trat das Problem auf?
- **Beispiel**: `"production"`
- **Verwendung**: Filterung, Severity-Bewertung

#### `context.related_changes`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Kürzliche Änderungen, die relevant sein könnten
- **Beispiel**: `["Update auf Version 3.7.2", "Firewall-Regel geändert"]`
- **Verwendung**: Change-Korrelation, Root-Cause-Analyse

### Status-Schlüssel

#### `status`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `open`, `in_progress`, `resolved`, `closed`, `reopened`
- **Beschreibung**: Aktueller Status des Problems
- **Beispiel**: `"resolved"`
- **Verwendung**: Workflow-Steuerung, Dashboards, Metriken
- **Lifecycle**:
  1. `open` → Problem gemeldet
  2. `in_progress` → Bearbeitung läuft
  3. `resolved` → Lösung implementiert
  4. `closed` → Bestätigt gelöst, archiviert
  5. `reopened` → Problem trat erneut auf

#### `resolution_date`
- **Typ**: String (ISO8601)
- **Pflicht**: Nein (Pflicht wenn status=resolved/closed)
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Zeitpunkt der Problemlösung
- **Beispiel**: `"2025-11-15T14:20:00Z"`
- **Verwendung**: MTTR-Berechnung, SLA-Tracking
- **Validierung**: Muss >= timestamp sein

---

## Solution JSON

### Metadaten-Schlüssel

#### `schema_version`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: Semantic Versioning
- **Beschreibung**: Version des Solution-Schemas
- **Beispiel**: `"1.0.0"`

#### `type`
- **Typ**: String
- **Pflicht**: Ja
- **Wert**: `"n2k_solution"` (konstant)
- **Beschreibung**: Identifiziert den JSON-Typ
- **Beispiel**: `"n2k_solution"`

#### `id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `sol_{uuid}`
- **Länge**: 36-64 Zeichen
- **Beschreibung**: Eindeutige Solution-ID
- **Beispiel**: `"sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0"`
- **Generierung**: UUID v4
- **Index**: Unique, Primary

#### `problem_ids`
- **Typ**: Array[String]
- **Pflicht**: Ja (min. 1 Element)
- **Element-Format**: `prob_{uuid}`
- **Beschreibung**: Liste aller Probleme, die diese Lösung adressiert
- **Beispiel**: `["prob_0cb386ae...", "prob_xyz123..."]`
- **Verwendung**: Many-to-Many Relationship, Lösungs-Wiederverwendung
- **Index**: Array-Index für Reverse-Lookup
- **Best Practice**: Eine Lösung kann mehrere ähnliche Probleme lösen

#### `asset_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `asset_{identifier}`
- **Beschreibung**: Asset, für das diese Lösung gilt
- **Beispiel**: `"asset_mailsystem_eah_01"`
- **Verwendung**: Foreign Key, Asset-spezifische Lösungen finden
- **Index**: Non-Unique

#### `timestamp`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ`
- **Beschreibung**: Zeitpunkt der Lösungsdokumentation
- **Beispiel**: `"2025-11-15T14:20:00Z"`
- **Verwendung**: Versionierung, Aktualität

### Solution-Objekt

#### `solution.title`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 10-200 Zeichen
- **Beschreibung**: Prägnanter Lösungstitel
- **Beispiel**: `"E-Mail Import in Knowledge Base aktivieren"`
- **Verwendung**: Listen-Ansicht, Suche
- **Best Practice**: Aktionsverb + Ziel, verständlich

#### `solution.type`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `configuration`, `bugfix`, `workaround`, `update`, `other`
- **Beschreibung**: Art der Lösung
- **Beispiel**: `"configuration"`
- **Verwendung**: Filterung, Analyse von Lösungstypen
- **Mapping**:
  - `configuration`: Config-Änderung
  - `bugfix`: Code-Fix, Patch
  - `workaround`: Temporäre Umgehung
  - `update`: Software/Hardware-Update
  - `other`: Sonstige Maßnahmen

#### `solution.approach`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `permanent_fix`, `workaround`, `temporary`
- **Beschreibung**: Wie nachhaltig ist die Lösung?
- **Beispiel**: `"workaround"`
- **Verwendung**: Technische Schuld tracken, Roadmap
- **Mapping**:
  - `permanent_fix`: Dauerhafte Lösung, Root Cause behoben
  - `workaround`: Umgehung, Problem besteht weiter
  - `temporary`: Zeitlich begrenzt (bis Update etc.)

#### `solution.description`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 50-5000 Zeichen
- **Beschreibung**: Ausführliche Beschreibung der Lösung
- **Beispiel**: `"Integration des Mail-Systems mit der Knowledge Base..."`
- **Verwendung**: Kontext, Begründung
- **Best Practice**: Was, Warum, Wie, Auswirkungen

#### `solution.prerequisites`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 5-500 Zeichen
- **Beschreibung**: Was muss vorhanden/erfüllt sein?
- **Beispiel**: `["Zugriff auf Mail-System", "API-Token für KB"]`
- **Verwendung**: Vorbedingungen prüfen, Planung
- **Best Practice**: Konkret, prüfbar

#### `solution.steps`
- **Typ**: Array[Object]
- **Pflicht**: Ja (min. 1 Element)
- **Beschreibung**: Schrittweise Anleitung
- **Verwendung**: Runbook, Automatisierung
- **Struktur**: Siehe [Step-Objekt](#step-objekt)

### Step-Objekt

#### `steps[].step_number`
- **Typ**: Integer
- **Pflicht**: Ja
- **Range**: 1-999
- **Beschreibung**: Schrittnummer (sequenziell)
- **Beispiel**: `1`
- **Verwendung**: Sortierung, Fortschritt
- **Validierung**: Muss lückenlos aufsteigend sein

#### `steps[].action`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 10-200 Zeichen
- **Beschreibung**: Kurze Beschreibung der Aktion
- **Beispiel**: `"Knowledge Base Import-API konfigurieren"`
- **Verwendung**: Überschrift, Checkliste
- **Best Practice**: Aktionsverb, präzise

#### `steps[].details`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 20-2000 Zeichen
- **Beschreibung**: Ausführliche Erklärung
- **Beispiel**: `"API-Endpoint /api/import/mail in der Config eintragen"`
- **Verwendung**: Durchführung, Kontext
- **Best Practice**: Wo, Was genau, Warum

#### `steps[].command`
- **Typ**: String oder null
- **Pflicht**: Nein
- **Länge**: 5-5000 Zeichen
- **Beschreibung**: Auszuführender Befehl (Shell, SQL, etc.)
- **Beispiel**: `"echo 'KB_IMPORT_URL=https://...' >> /etc/mail/config.env"`
- **Verwendung**: Copy-Paste, Automatisierung
- **Best Practice**: Escape Quotes, Pfade absolut
- **Format**: Plain text, language-agnostic

#### `steps[].expected_result`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 10-1000 Zeichen
- **Beschreibung**: Was sollte nach diesem Schritt passieren?
- **Beispiel**: `"Config-Datei enthält neue Variable"`
- **Verwendung**: Validierung, Testing
- **Best Practice**: Messbar, prüfbar

#### `steps[].estimated_duration`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "2 min", "30 sec")
- **Beschreibung**: Geschätzte Dauer des Schritts
- **Beispiel**: `"2 min"`
- **Verwendung**: Zeitplanung, Priorisierung

#### `steps[].warnings`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Warnungen, Vorsichtsmaßnahmen
- **Beispiel**: `["Backup erstellen vor Änderung", "Produktivbetrieb betroffen"]`
- **Verwendung**: Risikominimierung

### Validation-Objekt

#### `solution.validation.success_criteria`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Woran erkennt man Erfolg?
- **Beispiel**: `["Mails werden zugestellt", "Keine Fehler in Logs"]`
- **Verwendung**: Acceptance Testing, Verifikation
- **Best Practice**: Messbar, binär (ja/nein)

#### `solution.validation.test_procedure`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 20-2000 Zeichen
- **Beschreibung**: Wie testet man die Lösung?
- **Beispiel**: `"Test-Mail senden und nach 5 Min in KB suchen"`
- **Verwendung**: Qualitätssicherung
- **Best Practice**: Schritt-für-Schritt, reproduzierbar

#### `solution.validation.rollback_plan`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 20-2000 Zeichen
- **Beschreibung**: Was tun, wenn es schiefgeht?
- **Beispiel**: `"Import-URL entfernen, Mail-Service neu starten"`
- **Verwendung**: Disaster Recovery, Risikominimierung
- **Best Practice**: Konkret, getestet

### Outcome-Objekt

#### `solution.outcome.tested`
- **Typ**: Boolean
- **Pflicht**: Ja
- **Beschreibung**: Wurde die Lösung tatsächlich getestet?
- **Beispiel**: `true`
- **Verwendung**: Qualitätskennzeichen, Vertrauen

#### `solution.outcome.successful`
- **Typ**: Boolean
- **Pflicht**: Nein (Pflicht wenn tested=true)
- **Beschreibung**: War der Test erfolgreich?
- **Beispiel**: `true`
- **Verwendung**: Erfolgsrate, Filtering
- **Validierung**: Nur wenn tested=true

#### `solution.outcome.side_effects`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Bekannte Nebenwirkungen
- **Beispiel**: `["Zusätzlicher Storage-Verbrauch"]`
- **Verwendung**: Risikobewertung, Kapazitätsplanung

#### `solution.outcome.performance_impact`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `none`, `minimal`, `moderate`, `significant`
- **Beschreibung**: Auswirkung auf Performance
- **Beispiel**: `"minimal"`
- **Verwendung**: Capacity Planning, Priorisierung

### Metadata-Objekt

#### `metadata.author`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 1-200 Zeichen
- **Beschreibung**: Wer hat die Lösung dokumentiert?
- **Beispiel**: `"Hentschke"`
- **Verwendung**: Attribution, Kontakt

#### `metadata.source`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 5-500 Zeichen
- **Beschreibung**: Woher stammt die Lösung?
- **Beispiel**: `"Support-Case 0cb386ae"`, `"Vendor Documentation"`
- **Verwendung**: Vertrauensbewertung, Referenz

#### `metadata.reusability_score`
- **Typ**: Float
- **Pflicht**: Nein
- **Range**: 0.0-1.0
- **Beschreibung**: Wie wiederverwendbar ist die Lösung?
- **Beispiel**: `0.85`
- **Verwendung**: Priorisierung, Dokumentationsaufwand
- **Berechnung**: 
  - 1.0 = Universell anwendbar
  - 0.5 = Spezifisch für Konfiguration
  - 0.0 = Einmalig, nicht wiederverwendbar

#### `metadata.complexity`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `low`, `medium`, `high`
- **Beschreibung**: Komplexität der Lösung
- **Beispiel**: `"low"`
- **Verwendung**: Skill-Matching, Eskalation
- **Mapping**:
  - `low`: 1-3 einfache Schritte
  - `medium`: 4-10 Schritte, etwas technisch
  - `high`: >10 Schritte, Expertenwissen nötig

#### `metadata.estimated_time`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "10 min", "2 hours")
- **Beschreibung**: Geschätzte Gesamtumsetzungsdauer
- **Beispiel**: `"10 min"`
- **Verwendung**: Zeitplanung, Priorisierung
- **Best Practice**: Summe aus steps[].estimated_duration

#### `metadata.required_skills`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 3-100 Zeichen
- **Beschreibung**: Benötigte Fähigkeiten
- **Beispiel**: `["Mail-Server Administration", "API-Integration"]`
- **Verwendung**: Skill-Matching, Training-Bedarfe

### Verknüpfungen

#### `related_solutions`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: `sol_{uuid}`
- **Beschreibung**: IDs verwandter/alternativer Lösungen
- **Beispiel**: `["sol_xyz123...", "sol_abc456..."]`
- **Verwendung**: Cross-Referencing, "Siehe auch"

#### `tags`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 2-50 Zeichen
- **Beschreibung**: Freie Tags für Suche
- **Beispiel**: `["mail", "knowledge-base", "integration", "quick-win"]`
- **Verwendung**: Tagging, Folksonomy, Discovery
- **Best Practice**: Lowercase, Bindestriche statt Leerzeichen

---

## Asset JSON

### Metadaten-Schlüssel

#### `schema_version`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: Semantic Versioning
- **Beschreibung**: Version des Asset-Schemas
- **Beispiel**: `"1.0.0"`

#### `type`
- **Typ**: String
- **Pflicht**: Ja
- **Wert**: `"n2k_asset"` (konstant)
- **Beschreibung**: Identifiziert den JSON-Typ
- **Beispiel**: `"n2k_asset"`

#### `id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `asset_{identifier}` (sprechend) oder `asset_{uuid}`
- **Länge**: 10-100 Zeichen
- **Beschreibung**: Eindeutige Asset-ID
- **Beispiel**: `"asset_mailsystem_eah_01"`
- **Generierung**: Manuell (sprechend) bevorzugt, sonst UUID
- **Index**: Unique, Primary
- **Best Practice**: Sprechende IDs für Hauptsysteme

#### `created_at`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Zeitpunkt der Asset-Erstellung in KB
- **Beispiel**: `"2025-11-15T10:00:00Z"`
- **Verwendung**: Audit Trail

#### `updated_at`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Letzte Aktualisierung des Asset-Eintrags
- **Beispiel**: `"2025-11-15T14:20:00Z"`
- **Verwendung**: Cache Invalidation, Change Tracking
- **Validierung**: Muss >= created_at sein

### Asset-Objekt

#### `asset.name`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 3-200 Zeichen
- **Beschreibung**: Technischer, eindeutiger Name
- **Beispiel**: `"EAH Mail-System"`
- **Verwendung**: Primary Identifier
- **Index**: Unique
- **Best Practice**: Konsistente Naming Convention

#### `asset.display_name`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 3-200 Zeichen
- **Beschreibung**: Benutzerfreundlicher Anzeigename
- **Beispiel**: `"Zentrales E-Mail-System"`
- **Verwendung**: UI, Reports

#### `asset.description`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 20-2000 Zeichen
- **Beschreibung**: Was macht dieses Asset? Zweck, Funktion
- **Beispiel**: `"Hochschulweites E-Mail-System für Mitarbeitende und Studierende"`
- **Verwendung**: Dokumentation, Onboarding

#### `asset.type`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: Siehe [Asset Types](#asset-types-enum)
- **Beschreibung**: Detaillierter Asset-Typ
- **Beispiel**: `"mail_infrastructure"`
- **Verwendung**: Kategorisierung, Filtering
- **Index**: Category Index

#### `asset.category`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: Siehe [Asset Categories](#asset-categories-enum)
- **Beschreibung**: Übergeordnete Kategorie
- **Beispiel**: `"communication"`
- **Verwendung**: High-Level Grouping

#### `asset.status`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `active`, `inactive`, `decommissioned`, `planned`
- **Beschreibung**: Aktueller Lifecycle-Status
- **Beispiel**: `"active"`
- **Verwendung**: Filtering, Asset Management
- **Mapping**:
  - `active`: Im Produktivbetrieb
  - `inactive`: Temporär außer Betrieb
  - `decommissioned`: Abgeschaltet, Daten archiviert
  - `planned`: Noch nicht produktiv

#### `asset.criticality`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `low`, `medium`, `high`, `critical`
- **Beschreibung**: Geschäftskritikalität
- **Beispiel**: `"high"`
- **Verwendung**: SLA-Steuerung, Incident Priorisierung
- **Mapping**:
  - `low`: Nice-to-have
  - `medium`: Wichtig für Teilprozesse
  - `high`: Wichtig für Kernprozesse
  - `critical`: Systemkritisch, hohe Ausfallkosten

### Technical-Objekt

#### `technical.software`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 1-200 Zeichen
- **Beschreibung**: Software-/Produktname
- **Beispiel**: `"Postfix"`
- **Verwendung**: Vendor-Recherche, Update-Management

#### `technical.version`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 1-50 Zeichen
- **Beschreibung**: Versionsnummer
- **Beispiel**: `"3.7.2"`
- **Verwendung**: Vulnerability Management, Kompatibilität

#### `technical.platform`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 3-200 Zeichen
- **Beschreibung**: Betriebssystem/Runtime-Plattform
- **Beispiel**: `"Linux (Ubuntu 22.04 LTS)"`
- **Verwendung**: Deployment, Troubleshooting

#### `technical.architecture`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 3-50 Zeichen
- **Beschreibung**: CPU-Architektur
- **Beispiel**: `"x86_64"`, `"ARM64"`
- **Verwendung**: Binary Compatibility

#### `technical.deployment`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `on-premise`, `cloud`, `hybrid`
- **Beschreibung**: Deployment-Modell
- **Beispiel**: `"on-premise"`
- **Verwendung**: Capacity Planning, Compliance

#### `technical.vendor`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 2-200 Zeichen
- **Beschreibung**: Hersteller/Anbieter
- **Beispiel**: `"Open Source"`, `"Microsoft"`
- **Verwendung**: Support-Kontakte, Lizenzmanagement

#### `technical.license`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 3-200 Zeichen
- **Beschreibung**: Lizenzmodell
- **Beispiel**: `"IBM Public License"`, `"Subscription"` 
- **Verwendung**: Compliance, Kosten

### Integrations Array

#### `integrations[].name`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 2-200 Zeichen
- **Beschreibung**: Name des integrierten Systems
- **Beispiel**: `"LDAP"`

#### `integrations[].purpose`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 5-500 Zeichen
- **Beschreibung**: Zweck der Integration
- **Beispiel**: `"User Authentication"`

#### `integrations[].asset_id`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: `asset_{identifier}`
- **Beschreibung**: Referenz zum integrierten Asset
- **Beispiel**: `"asset_ldap_eah_01"`
- **Verwendung**: Dependency Mapping

#### `integrations[].interface`
- **Typ**: String
- **Pflicht**: Nein
- **Werte**: `API`, `LDAP`, `Database`, `File`, `Message Queue`
- **Beschreibung**: Art der Schnittstelle
- **Beispiel**: `"LDAP"`

#### `integrations[].status`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `active`, `inactive`
- **Beschreibung**: Status der Integration
- **Beispiel**: `"active"`

### Ownership-Objekt

#### `ownership.department`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 3-200 Zeichen
- **Beschreibung**: Verantwortliche Abteilung
- **Beispiel**: `"Servicezentrum Informatik"`
- **Verwendung**: Routing, Eskalation

#### `ownership.primary_contact`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 2-200 Zeichen
- **Beschreibung**: Hauptansprechpartner
- **Beispiel**: `"Hentschke"`
- **Verwendung**: Kontaktaufnahme

#### `ownership.email`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: RFC 5322 E-Mail
- **Beschreibung**: Kontakt-E-Mail
- **Beispiel**: `"it-support@eah-jena.de"`
- **Verwendung**: Support-Routing

#### `ownership.escalation_contact`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 2-200 Zeichen
- **Beschreibung**: Eskalationskontakt
- **Beispiel**: `"IT-Leitung"`
- **Verwendung**: Kritische Incidents

### Documentation-Objekt

#### `documentation.wiki_url`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: Link zur Wiki-Dokumentation
- **Beispiel**: `"https://wiki.eah-jena.de/mailsystem"`

#### `documentation.api_docs`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: Link zur API-Dokumentation
- **Beispiel**: `"https://api-docs.eah-jena.de/mail"`

#### `documentation.runbook`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: Link zum Betriebshandbuch
- **Beispiel**: `"https://docs.eah-jena.de/runbooks/mail"`

#### `documentation.architecture_diagram`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: Link zum Architekturdiagramm
- **Beispiel**: `"https://docs.eah-jena.de/arch/mail.png"`

### Maintenance-Objekt

#### `maintenance.last_update`
- **Typ**: String (Date)
- **Pflicht**: Nein
- **Format**: `YYYY-MM-DD`
- **Beschreibung**: Letztes Software-/Hardware-Update
- **Beispiel**: `"2025-10-01"`

#### `maintenance.update_frequency`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext
- **Beschreibung**: Geplanter Update-Rhythmus
- **Beispiel**: `"quarterly"`, `"monthly"`, `"annually"`

#### `maintenance.backup_schedule`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext
- **Beschreibung**: Backup-Frequenz
- **Beispiel**: `"daily"`, `"hourly"`

#### `maintenance.monitoring`
- **Typ**: Boolean
- **Pflicht**: Nein
- **Beschreibung**: Wird das Asset überwacht?
- **Beispiel**: `true`

#### `maintenance.sla`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "99.9%", "24/7")
- **Beschreibung**: Service Level Agreement
- **Beispiel**: `"99.5%"`

### Knowledge-Objekt

#### `knowledge.known_problems`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: `prob_{uuid}`
- **Beschreibung**: IDs bekannter Probleme
- **Beispiel**: `["prob_0cb386ae...", "prob_xyz..."]`
- **Verwendung**: Reverse Lookup, Problem-Historie
- **Aktualisierung**: Automatisch bei Problem-Insert

#### `knowledge.available_solutions`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: `sol_{uuid}`
- **Beschreibung**: IDs verfügbarer Lösungen
- **Beispiel**: `["sol_a7b9c3d...", "sol_xyz..."]`
- **Verwendung**: Quick Access zu Solutions
- **Aktualisierung**: Automatisch bei Solution-Insert

#### `knowledge.total_incidents`
- **Typ**: Integer
- **Pflicht**: Nein
- **Range**: 0-999999
- **Beschreibung**: Gesamtzahl der Incidents
- **Beispiel**: `12`
- **Verwendung**: Metriken, Zuverlässigkeitsanalyse
- **Aktualisierung**: Counter, automatisch

#### `knowledge.mean_time_to_resolve`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "45 min", "2 hours")
- **Beschreibung**: Durchschnittliche Lösungszeit
- **Beispiel**: `"45 min"`
- **Verwendung**: SLA-Monitoring, Kapazitätsplanung
- **Berechnung**: Durchschnitt aus resolution_date - timestamp

#### `knowledge.common_issues`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 10-500 Zeichen
- **Beschreibung**: Häufige Probleme (Freitext-Zusammenfassung)
- **Beispiel**: `["Spam-Filter Fehlalarme", "LDAP Sync-Probleme"]`
- **Verwendung**: Quick Reference, Training
- **Aktualisierung**: Manuell oder durch Aggregation

### Verknüpfungen

#### `related_assets`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: `asset_{identifier}`
- **Beschreibung**: IDs verwandter/abhängiger Assets
- **Beispiel**: `["asset_ldap_eah_01", "asset_storage_mail_01"]`
- **Verwendung**: Dependency Mapping, Impact Analysis

#### `tags`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 2-50 Zeichen
- **Beschreibung**: Freie Tags
- **Beispiel**: `["email", "communication", "critical-infrastructure"]`

---

## Case JSON

### Metadaten-Schlüssel

#### `schema_version`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: Semantic Versioning
- **Beschreibung**: Version des Case-Schemas
- **Beispiel**: `"1.0.0"`

#### `type`
- **Typ**: String
- **Pflicht**: Ja
- **Wert**: `"n2k_case"` (konstant)
- **Beschreibung**: Identifiziert den JSON-Typ
- **Beispiel**: `"n2k_case"`

#### `id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `case_{uuid}` oder `case_{mail_id_sanitized}`
- **Länge**: 37-64 Zeichen
- **Beschreibung**: Eindeutige Case-ID
- **Beispiel**: `"case_0cb386ae2c684a53a69e8a4a786a298e"`
- **Generierung**: Aus mail_id abgeleitet
- **Index**: Unique, Primary

#### `mail_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: UUID oder E-Mail Message-ID
- **Beschreibung**: Original E-Mail Message-ID
- **Beispiel**: `"0cb386ae-2c68-4a53-a69e-8a4a786a298e"`
- **Verwendung**: Rückverfolgung zur E-Mail
- **Index**: Non-Unique (Thread-Support)

#### `created_at`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ`
- **Beschreibung**: Case-Erstellung (= E-Mail-Eingang)
- **Beispiel**: `"2025-11-15T10:35:57.424Z"`
- **Index**: Range-Index für Zeitreihen

#### `resolved_at`
- **Typ**: String (ISO8601)
- **Pflicht**: Nein
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Zeitpunkt der Case-Lösung
- **Beispiel**: `"2025-11-15T14:20:00Z"`
- **Verwendung**: MTTR-Berechnung

### Case-Objekt

#### `case.title`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 10-200 Zeichen
- **Beschreibung**: Case-Titel (typischerweise aus E-Mail-Subject)
- **Beispiel**: `"Mail-System Import-Fehler"`
- **Verwendung**: Listen-Ansicht, Dashboard

#### `case.status`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `open`, `in_progress`, `resolved`, `closed`, `reopened`
- **Beschreibung**: Aktueller Case-Status
- **Beispiel**: `"resolved"`
- **Verwendung**: Workflow, Filtering

#### `case.priority`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `low`, `medium`, `high`, `critical`
- **Beschreibung**: Case-Priorität
- **Beispiel**: `"high"`
- **Verwendung**: Queue-Sortierung

#### `case.reporter`
- **Typ**: Object
- **Pflicht**: Ja
- **Struktur**: `{ "name": "...", "email": "..." }`
- **Beschreibung**: Meldende Person
- **Beispiel**: `{ "name": "Hentschke", "email": "hentschke@eah-jena.de" }`

### Mail_Metadata-Objekt

#### `mail_metadata.subject`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 1-500 Zeichen
- **Beschreibung**: E-Mail Betreff
- **Beispiel**: `"Re: Mail-System Probleme"`

#### `mail_metadata.from`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: RFC 5322 E-Mail
- **Beschreibung**: Absender
- **Beispiel**: `"hentschke@eah-jena.de"`

#### `mail_metadata.to`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: RFC 5322 E-Mail
- **Beschreibung**: Empfänger
- **Beispiel**: `"it-support@eah-jena.de"`

#### `mail_metadata.date`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: E-Mail Sendedatum
- **Beispiel**: `"2025-11-15T11:35:00Z"`

#### `mail_metadata.thread_id`
- **Typ**: String
- **Pflicht**: Nein
- **Beschreibung**: Thread-ID (bei Konversationen)
- **Beispiel**: `"thread_abc123"`
- **Verwendung**: Konversations-Verkettung

#### `mail_metadata.has_attachments`
- **Typ**: Boolean
- **Pflicht**: Ja
- **Beschreibung**: Hat die E-Mail Anhänge?
- **Beispiel**: `false`

#### `mail_metadata.attachments`
- **Typ**: Array[Object]
- **Pflicht**: Nein (leer wenn has_attachments=false)
- **Beschreibung**: Liste der Anhänge
- **Struktur**: Siehe [Attachment-Objekt](#attachment-objekt)

### Attachment-Objekt

#### `attachments[].filename`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 1-255 Zeichen
- **Beschreibung**: Dateiname
- **Beispiel**: `"error_screenshot.png"`

#### `attachments[].type`
- **Typ**: String (MIME Type)
- **Pflicht**: Ja
- **Format**: MIME Type
- **Beschreibung**: Dateityp
- **Beispiel**: `"image/png"`

#### `attachments[].size_bytes`
- **Typ**: Integer
- **Pflicht**: Ja
- **Range**: 0-999999999
- **Beschreibung**: Dateigröße in Bytes
- **Beispiel**: `2458624`

#### `attachments[].storage_path`
- **Typ**: String
- **Pflicht**: Ja
- **Beschreibung**: Pfad im Object Storage
- **Beispiel**: `"/attachments/2025/11/error_screenshot_abc123.png"`

#### `attachments[].storage_url`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: Öffentliche URL zum Download
- **Beispiel**: `"https://storage.eah-jena.de/n2k/attachments/..."`

#### `attachments[].extracted_text`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 0-50000 Zeichen
- **Beschreibung**: Via OCR/Parser extrahierter Text
- **Beispiel**: `"SMTP Error 550: Mailbox unavailable"`

#### `attachments[].ocr_applied`
- **Typ**: Boolean
- **Pflicht**: Nein
- **Beschreibung**: Wurde OCR angewendet?
- **Beispiel**: `true`

#### `attachments[].processing_status`
- **Typ**: String (Enum)
- **Pflicht**: Ja
- **Werte**: `pending`, `indexed`, `failed`, `skipped`
- **Beschreibung**: Verarbeitungsstatus
- **Beispiel**: `"indexed"`

### Entities-Objekt

#### `entities.problem_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `prob_{uuid}`
- **Beschreibung**: Referenz zum Problem
- **Beispiel**: `"prob_0cb386ae2c684a53a69e8a4a786a298e"`
- **Index**: Foreign Key

#### `entities.asset_id`
- **Typ**: String
- **Pflicht**: Ja
- **Format**: `asset_{identifier}`
- **Beschreibung**: Referenz zum betroffenen Asset
- **Beispiel**: `"asset_mailsystem_eah_01"`
- **Index**: Foreign Key

#### `entities.applied_solution_id`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: `sol_{uuid}`
- **Beschreibung**: Welche Lösung wurde letztendlich verwendet?
- **Beispiel**: `"sol_a7b9c3d4e5f6a1b2c3d4e5f6a7b8c9d0"`
- **Verwendung**: Success-Tracking, Reusability

#### `entities.alternative_solutions`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: `sol_{uuid}`
- **Beschreibung**: Andere mögliche/getestete Lösungen
- **Beispiel**: `["sol_xyz...", "sol_abc..."]`
- **Verwendung**: "Siehe auch", Learning

### Resolution_Path Array

#### `resolution_path[].step`
- **Typ**: Integer
- **Pflicht**: Ja
- **Range**: 1-999
- **Beschreibung**: Schrittnummer im Lösungsweg
- **Beispiel**: `1`

#### `resolution_path[].timestamp`
- **Typ**: String (ISO8601)
- **Pflicht**: Ja
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Zeitpunkt des Schritts
- **Beispiel**: `"2025-11-15T11:40:00Z"`

#### `resolution_path[].action`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 5-200 Zeichen
- **Beschreibung**: Was wurde getan?
- **Beispiel**: `"Problem analysiert"`, `"Lösung getestet"`

#### `resolution_path[].actor`
- **Typ**: String
- **Pflicht**: Ja
- **Länge**: 2-200 Zeichen
- **Beschreibung**: Wer hat gehandelt?
- **Beispiel**: `"Hentschke"`

#### `resolution_path[].solution_id`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: `sol_{uuid}`
- **Beschreibung**: Falls Lösung getestet: Welche?
- **Beispiel**: `"sol_a7b9c3d..."`

#### `resolution_path[].outcome`
- **Typ**: String (Enum)
- **Pflicht**: Nein
- **Werte**: `success`, `failed`, `partial`
- **Beschreibung**: Ergebnis des Schritts
- **Beispiel**: `"success"`

#### `resolution_path[].notes`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 0-2000 Zeichen
- **Beschreibung**: Freitext-Notizen
- **Beispiel**: `"SMTP-Logs zeigen Rejection wegen fehlendem KB-Import"`

### Conversation_Context-Objekt

#### `conversation_context.thread_messages`
- **Typ**: Integer
- **Pflicht**: Nein
- **Range**: 1-999
- **Beschreibung**: Anzahl Nachrichten im Thread
- **Beispiel**: `3`

#### `conversation_context.participants`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Format**: E-Mail-Adresse
- **Beschreibung**: Alle Teilnehmer der Konversation
- **Beispiel**: `["hentschke@eah-jena.de", "it-support@eah-jena.de"]`

#### `conversation_context.conversation_summary`
- **Typ**: String
- **Pflicht**: Nein
- **Länge**: 50-2000 Zeichen
- **Beschreibung**: KI-generierte Zusammenfassung
- **Beispiel**: `"Mail-System lehnte Mails ab. Ursache: Fehlendes KB-Import Feature..."`

### Knowledge_Base_Integration-Objekt

#### `knowledge_base_integration.kb_article_generated`
- **Typ**: Boolean
- **Pflicht**: Nein
- **Beschreibung**: Wurde ein KB-Artikel generiert?
- **Beispiel**: `true`

#### `knowledge_base_integration.kb_article_id`
- **Typ**: String
- **Pflicht**: Nein (Pflicht wenn kb_article_generated=true)
- **Format**: `kb_art_{id}`
- **Beschreibung**: ID des generierten KB-Artikels
- **Beispiel**: `"kb_art_001"`

#### `knowledge_base_integration.kb_article_url`
- **Typ**: String (URL)
- **Pflicht**: Nein
- **Format**: Valid HTTP(S) URL
- **Beschreibung**: URL zum KB-Artikel
- **Beispiel**: `"https://kb.eah-jena.de/articles/001"`

#### `knowledge_base_integration.indexed_at`
- **Typ**: String (ISO8601)
- **Pflicht**: Nein
- **Format**: `YYYY-MM-DDTHH:MM:SSZ`
- **Beschreibung**: Zeitpunkt der KB-Indizierung
- **Beispiel**: `"2025-11-15T14:30:00Z"`

### Metrics-Objekt

#### `metrics.time_to_first_response`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "5 min")
- **Beschreibung**: Zeit bis zur ersten Reaktion
- **Beispiel**: `"5 min"`
- **Berechnung**: erste resolution_path[].timestamp - created_at

#### `metrics.time_to_resolution`
- **Typ**: String
- **Pflicht**: Nein
- **Format**: Freitext (z.B. "3h 45min")
- **Beschreibung**: Gesamtlösungszeit
- **Beispiel**: `"3h 45min"`
- **Berechnung**: resolved_at - created_at

#### `metrics.reopened`
- **Typ**: Boolean
- **Pflicht**: Nein
- **Beschreibung**: Wurde der Case wiedereröffnet?
- **Beispiel**: `false`

#### `metrics.satisfaction_score`
- **Typ**: Float
- **Pflicht**: Nein
- **Range**: 1.0-5.0
- **Beschreibung**: Nutzerzufriedenheit (falls erfasst)
- **Beispiel**: `4.5`

### Tags

#### `tags`
- **Typ**: Array[String]
- **Pflicht**: Nein
- **Element-Länge**: 2-50 Zeichen
- **Beschreibung**: Freie Tags
- **Beispiel**: `["mail", "quick-win", "configuration"]`

---

## Gemeinsame Datentypen

### ISO8601 Timestamp
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ` (UTC)
- **Beispiel**: `"2025-11-15T10:35:57.424Z"`
- **Timezone**: Immer UTC (Z)
- **Präzision**: Millisekunden

### UUID
- **Version**: UUID v4 (random)
- **Format**: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- **Beispiel**: `"0cb386ae-2c68-4a53-a69e-8a4a786a298e"`
- **Verwendung**: Eindeutige IDs

### E-Mail Adresse
- **Standard**: RFC 5322
- **Format**: `local-part@domain`
- **Beispiel**: `"hentschke@eah-jena.de"`
- **Validierung**: Regex oder Library

### URL
- **Schema**: `http://` oder `https://`
- **Validierung**: Valid URL nach RFC 3986
- **Beispiel**: `"https://wiki.eah-jena.de/mailsystem"`

---

## Enumerationen

### category (Enum)
**Verwendung**: Problem.classification.category, Asset.asset.category

```
- email          E-Mail-Systeme
- identity       LDAP, Active Directory, SSO
- network        Switches, Firewalls, VPN
- application    Business-Apps, ERP, LMS
- infrastructure Server, Storage, Backup
- client         Workstations, Mobile Devices
- security       Malware, Zugriffsprobleme
- other          Sonstige
```

### severity (Enum)
**Verwendung**: Problem.classification.severity

```
- low       Kosmetisch, geringer Impact
- medium    Eingeschränkte Funktionalität
- high      Wichtige Funktion ausgefallen
- critical  System ausgefallen, hoher Business Impact
```

### status (Enum)
**Verwendung**: Problem.status, Case.case.status

```
- open         Neu gemeldet, noch nicht bearbeitet
- in_progress  Bearbeitung läuft
- resolved     Lösung implementiert
- closed       Bestätigt gelöst, archiviert
- reopened     Problem trat erneut auf
```

### frequency (Enum)
**Verwendung**: Problem.context.frequency

```
- once         Einmaliges Ereignis
- intermittent Sporadisch, schwer reproduzierbar
- continuous   Dauerhaft, jederzeit reproduzierbar
```

### environment (Enum)
**Verwendung**: Problem.context.environment

```
- production   Produktivumgebung
- staging      Staging/Pre-Prod
- development  Entwicklungsumgebung
- test         Testumgebung
```

### solution_type (Enum)
**Verwendung**: Solution.solution.type

```
- configuration  Konfigurationsänderung
- bugfix         Code-Fix, Patch
- workaround     Temporäre Umgehung
- update         Software/Hardware-Update
- other          Sonstige Maßnahmen
```

### solution_approach (Enum)
**Verwendung**: Solution.solution.approach

```
- permanent_fix  Dauerhafte Lösung, Root Cause behoben
- workaround     Umgehung, Problem besteht weiter
- temporary      Zeitlich begrenzt
```

### performance_impact (Enum)
**Verwendung**: Solution.outcome.performance_impact

```
- none         Keine Performance-Auswirkung
- minimal      <5% Performance-Verlust
- moderate     5-20% Performance-Verlust
- significant  >20% Performance-Verlust
```

### complexity (Enum)
**Verwendung**: Solution.metadata.complexity

```
- low     1-3 einfache Schritte
- medium  4-10 Schritte, etwas technisch
- high    >10 Schritte, Expertenwissen nötig
```

### asset_status (Enum)
**Verwendung**: Asset.asset.status

```
- active          Im Produktivbetrieb
- inactive        Temporär außer Betrieb
- decommissioned  Abgeschaltet, archiviert
- planned         Noch nicht produktiv
```

### criticality (Enum)
**Verwendung**: Asset.asset.criticality, Problem.classification.business_impact

```
- low      Nice-to-have
- medium   Wichtig für Teilprozesse
- high     Wichtig für Kernprozesse
- critical Systemkritisch, hohe Ausfallkosten
```

### deployment (Enum)
**Verwendung**: Asset.technical.deployment

```
- on-premise  Lokale Infrastruktur
- cloud       Cloud-gehostet
- hybrid      Mix aus on-premise und cloud
```

### asset_categories (Enum)
**Verwendung**: Asset.asset.category

```
- communication   E-Mail, Chat, Telefonie
- identity        LDAP, AD, SSO, IAM
- infrastructure  Server, Storage, Netzwerk
- application     Business-Apps
- network         Switches, Router, Firewalls
- security        Firewalls, AV, IDS/IPS
- storage         SAN, NAS, Backup
- client          Workstations, Laptops, Mobile
```

### asset_types (Enum)
**Verwendung**: Asset.asset.type

**Communication:**
```
- mail_infrastructure
- chat_system
- voip_system
```

**Identity:**
```
- ldap_service
- active_directory
- sso_provider
- identity_management
```

**Infrastructure:**
```
- web_server
- database_server
- application_server
- file_server
- backup_system
```

**Network:**
```
- switch
- router
- firewall
- vpn_gateway
- load_balancer
```

**Application:**
```
- erp_system
- crm_system
- lms_system (Learning Management)
- cms_system
- ticketing_system
```

**Client:**
```
- workstation
- laptop
- mobile_device
- thin_client
```

### priority (Enum)
**Verwendung**: Case.case.priority

```
- low      Niedrige Priorität
- medium   Mittlere Priorität
- high     Hohe Priorität
- critical Kritisch, sofortige Bearbeitung
```

### attachment_processing_status (Enum)
**Verwendung**: Case.mail_metadata.attachments[].processing_status

```
- pending  Noch nicht verarbeitet
- indexed  Erfolgreich verarbeitet und indiziert
- failed   Verarbeitung fehlgeschlagen
- skipped  Absichtlich übersprungen
```

### resolution_outcome (Enum)
**Verwendung**: Case.resolution_path[].outcome

```
- success  Schritt erfolgreich
- failed   Schritt fehlgeschlagen
- partial  Teilweise erfolgreich
```

---

## Validierungsregeln

### Zeitstempel-Konsistenz

1. **Problem JSON:**
   - `resolution_date` >= `timestamp`

2. **Asset JSON:**
   - `updated_at` >= `created_at`

3. **Case JSON:**
   - `resolved_at` >= `created_at`
   - `resolution_path[i].timestamp` >= `created_at`
   - `resolution_path[i].timestamp` <= `resolved_at` (falls resolved)

### ID-Referenzen

1. **Foreign Keys müssen existieren:**
   - Problem.asset_id → Asset.id
   - Solution.asset_id → Asset.id
   - Solution.problem_ids[] → Problem.id
   - Case.entities.problem_id → Problem.id
   - Case.entities.asset_id → Asset.id
   - Case.entities.applied_solution_id → Solution.id

2. **ID-Format-Validierung:**
   - Problem: `^prob_[a-f0-9]{32,}$`
   - Solution: `^sol_[a-f0-9]{32,}$`
   - Asset: `^asset_[a-zA-Z0-9_-]{3,}$`
   - Case: `^case_[a-f0-9]{32,}$`

### Pflichtfeld-Logik

1. **Bedingte Pflichtfelder:**
   - `Problem.resolution_date`: Pflicht wenn `status` = "resolved" oder "closed"
   - `Solution.outcome.successful`: Pflicht wenn `outcome.tested` = true
   - `Case.resolved_at`: Pflicht wenn `case.status` = "resolved" oder "closed"

2. **Array-Mindestgröße:**
   - `Problem.symptoms`: min. 1 Element
   - `Solution.problem_ids`: min. 1 Element
   - `Solution.steps`: min. 1 Element

### Wertebereichs-Validierung

1. **String-Längen:**
   - Titel-Felder: 10-200 Zeichen
   - Beschreibungs-Felder: 20-5000 Zeichen
   - Namen: 1-200 Zeichen

2. **Numerische Werte:**
   - `metadata.reusability_score`: 0.0-1.0
   - `metrics.satisfaction_score`: 1.0-5.0
   - `attachments[].size_bytes`: 0-999999999

3. **URL-Validierung:**
   - Muss mit `http://` oder `https://` beginnen
   - Gültige Domain/IP

4. **E-Mail-Validierung:**
   - RFC 5322 konform
   - Format: `local@domain.tld`

### Cross-Field Validation

1. **Attachment-Logik:**
   - Wenn `has_attachments` = true → `attachments` Array nicht leer
   - Wenn `has_attachments` = false → `attachments` Array leer

2. **Status-Konsistenz:**
   - Wenn `status` = "resolved" → `resolution_date` gesetzt
   - Wenn `kb_article_generated` = true → `kb_article_id` gesetzt

3. **Step-Sequenz:**
   - `steps[].step_number` muss lückenlos aufsteigend sein

---

## JSON Schema Files

Für jede JSON-Struktur existiert ein JSON-Schema-File zur automatischen Validierung:

- `schemas/n2k_problem_v1.0.0.json`
- `schemas/n2k_solution_v1.0.0.json`
- `schemas/n2k_asset_v1.0.0.json`
- `schemas/n2k_case_v1.0.0.json`

**Verwendung:**
```bash
# Validierung mit jsonschema CLI
jsonschema -i data/problem.json schemas/n2k_problem_v1.0.0.json
```

**Python-Validierung:**
```python
import jsonschema
import json

with open('schemas/n2k_problem_v1.0.0.json') as f:
    schema = json.load(f)

with open('data/problem.json') as f:
    data = json.load(f)

jsonschema.validate(instance=data, schema=schema)
```

---

## Best Practices

### 1. ID-Generierung
- **Problem/Case**: Aus E-Mail Message-ID ableiten für Traceability
- **Solution**: UUID v4 für Eindeutigkeit
- **Asset**: Sprechende IDs für Hauptsysteme (z.B. `asset_mailsystem_eah_01`)

### 2. Zeitstempel
- **Immer UTC verwenden** (`Z` Suffix)
- **Millisekunden-Präzision** für granulare Zeitreihen
- **ISO8601** für Austauschbarkeit

### 3. Arrays
- **Niemals null**, sondern leere Arrays `[]`
- **Sortierung**: Wo sinnvoll (z.B. steps), sonst chronologisch
- **Deduplizierung**: Keine Duplikate in Tags/IDs

### 4. Beschreibungen
- **Aktive Sprache** ("System nimmt keine Mails an" statt "Mails werden nicht angenommen")
- **Spezifisch** statt generisch
- **Messbare Symptome** ("500ms Timeout" statt "langsam")

### 5. Versionierung
- **Schema Version** in jedem JSON
- **Breaking Changes** = MAJOR Bump
- **Migration Scripts** für Schema-Updates

### 6. Performance
- **Indizes** auf häufig gesuchte Felder
- **Denormalisierung** wo sinnvoll (z.B. asset_id in Problem)
- **Projection** in Queries (nur benötigte Felder laden)

---

**Dokumentversion**: 1.0.0  
**Letzte Aktualisierung**: 15.11.2025  
**Maintainer**: Servicezentrum Informatik, EAH Jena
