# Case Tracker CLI

A minimal, stdlib-only Python CLI for tracking DFIR cases, evidence (with automatic SHA-256 hashing and chain-of-custody logging), and IOCs — backed by a local SQLite database.

## Why This Exists

Full case-management platforms like [IRIS](https://github.com/dfir-iris/iris-web) are the right tool for multi-analyst teams needing a web UI, role-based access, and collaborative case workflows. This tool fills a different gap: solo or field DFIR work where standing up a full platform isn't practical, but you still need defensible evidence hashing and structured case notes — not a spreadsheet, not memory.

## Requirements

Python 3.8+. No external dependencies — uses only the standard library (`sqlite3`, `hashlib`, `argparse`, `json`).

## Usage

```bash
# Initialize the local database (first run only)
python3 case_tracker.py init

# Create a case
python3 case_tracker.py create-case --name "INC-2026-014" --description "Suspected ransomware, finance dept workstation"

# Log evidence — computes SHA-256 automatically and starts the custody log
python3 case_tracker.py add-evidence --case-id 1 --file /path/to/evidence.img --description "Forensic disk image" --actor "Your Name"

# Log a custody transfer or other event for existing evidence
python3 case_tracker.py log-custody --evidence-id 1 --action "transferred" --actor "Your Name" --note "Moved to analysis workstation"

# Track an IOC against the case
python3 case_tracker.py add-ioc --case-id 1 --type ip --value 203.0.113.42 --context "C2 beacon observed in firewall logs"

# List and inspect
python3 case_tracker.py list-cases
python3 case_tracker.py show-case --case-id 1

# Export a full case (evidence, custody log, IOCs) to JSON for reporting or handoff
python3 case_tracker.py export-case --case-id 1 --output case_1_export.json
```

## Data Model

- **cases** — id, name, description, status, created_at
- **evidence** — id, case_id, file_path, description, sha256, acquired_at
- **custody_log** — id, evidence_id, action, actor, note, timestamp (append-only)
- **iocs** — id, case_id, ioc_type, value, context, added_at

The database lives at `~/.dfir_case_tracker/cases.db` by default.

## Design Notes

- **Hashing is chunked** (64KB reads) so hashing a multi-gigabyte forensic image doesn't load the whole file into memory.
- **Custody log is append-only** — there's no `update-custody` or `delete-custody` command by design; corrections should be logged as new entries referencing the correction, not edits to history, to preserve an honest audit trail.
- **This tool logs custody events; it does not replace the formal chain-of-custody document** your organization/legal process requires — treat the SHA-256 output and exported JSON as source data to populate that document, not a replacement for it.

---
*Part of the [digital-forensics-dfir-toolkit](../../README.md) repository.*
