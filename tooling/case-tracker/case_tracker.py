#!/usr/bin/env python3
"""
case_tracker.py — Lightweight DFIR case tracking CLI.

A minimal, dependency-free (stdlib only) tool for tracking investigation
cases, evidence items with chain-of-custody logging, and indicators of
compromise (IOCs), backed by a local SQLite database.

This is intentionally scoped as a single-investigator / small-team CLI tool,
not a case-management platform — for full multi-analyst case management with
a web UI, role-based access, and collaborative workflows, a purpose-built
platform (e.g. IRIS: https://github.com/dfir-iris/iris-web) is the right
tool. This script fills the gap for solo/field use where standing up a full
platform isn't practical: quick case notes, defensible evidence hashing, and
IOC tracking from the command line.

Usage:
    python3 case_tracker.py init
    python3 case_tracker.py create-case --name "INC-2026-014" --description "Suspected ransomware, finance dept workstation"
    python3 case_tracker.py add-evidence --case-id 1 --file /path/to/evidence.img --description "Forensic disk image"
    python3 case_tracker.py add-ioc --case-id 1 --type ip --value 203.0.113.42 --context "C2 beacon"
    python3 case_tracker.py list-cases
    python3 case_tracker.py show-case --case-id 1
    python3 case_tracker.py export-case --case-id 1 --output case_1_export.json
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / ".dfir_case_tracker" / "cases.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            description TEXT,
            sha256 TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        );

        CREATE TABLE IF NOT EXISTS custody_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            actor TEXT,
            note TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (evidence_id) REFERENCES evidence(id)
        );

        CREATE TABLE IF NOT EXISTS iocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            ioc_type TEXT NOT NULL,
            value TEXT NOT NULL,
            context TEXT,
            added_at TEXT NOT NULL,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        );
        """
    )
    conn.commit()
    conn.close()
    print(f"Initialized case database at {DB_PATH}")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256_of_file(path, chunk_size=65536):
    """Hash a file in chunks so large forensic images don't get loaded into memory."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def create_case(args):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO cases (name, description, status, created_at) VALUES (?, ?, 'open', ?)",
            (args.name, args.description, now()),
        )
        conn.commit()
        case_id = conn.execute("SELECT id FROM cases WHERE name = ?", (args.name,)).fetchone()[0]
        print(f"Created case '{args.name}' with ID {case_id}")
    except sqlite3.IntegrityError:
        print(f"Error: a case named '{args.name}' already exists", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def add_evidence(args):
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Hashing {file_path} (this may take a while for large images)...")
    digest = sha256_of_file(file_path)

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO evidence (case_id, file_path, description, sha256, acquired_at) VALUES (?, ?, ?, ?, ?)",
        (args.case_id, str(file_path), args.description, digest, now()),
    )
    evidence_id = cur.lastrowid
    conn.execute(
        "INSERT INTO custody_log (evidence_id, action, actor, note, timestamp) VALUES (?, 'acquired', ?, ?, ?)",
        (evidence_id, args.actor or "unspecified", "Initial acquisition and hashing", now()),
    )
    conn.commit()
    conn.close()
    print(f"Evidence logged with ID {evidence_id}")
    print(f"SHA-256: {digest}")
    print("Record this hash in your external chain-of-custody documentation as the baseline value.")


def log_custody_event(args):
    conn = get_connection()
    conn.execute(
        "INSERT INTO custody_log (evidence_id, action, actor, note, timestamp) VALUES (?, ?, ?, ?, ?)",
        (args.evidence_id, args.action, args.actor, args.note, now()),
    )
    conn.commit()
    conn.close()
    print(f"Custody event logged for evidence ID {args.evidence_id}")


def add_ioc(args):
    conn = get_connection()
    conn.execute(
        "INSERT INTO iocs (case_id, ioc_type, value, context, added_at) VALUES (?, ?, ?, ?, ?)",
        (args.case_id, args.type, args.value, args.context, now()),
    )
    conn.commit()
    conn.close()
    print(f"IOC logged: {args.type}={args.value}")


def list_cases(args):
    conn = get_connection()
    rows = conn.execute("SELECT id, name, status, created_at FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    if not rows:
        print("No cases found. Use 'create-case' to add one.")
        return
    for r in rows:
        print(f"[{r[0]}] {r[1]}  status={r[2]}  created={r[3]}")


def show_case(args):
    conn = get_connection()
    case = conn.execute("SELECT id, name, description, status, created_at FROM cases WHERE id = ?", (args.case_id,)).fetchone()
    if not case:
        print(f"No case found with ID {args.case_id}", file=sys.stderr)
        sys.exit(1)

    print(f"Case [{case[0]}] {case[1]}  ({case[3]})")
    print(f"  Created: {case[4]}")
    print(f"  Description: {case[2] or '(none)'}")

    evidence = conn.execute(
        "SELECT id, file_path, description, sha256, acquired_at FROM evidence WHERE case_id = ?", (args.case_id,)
    ).fetchall()
    print(f"\n  Evidence ({len(evidence)}):")
    for e in evidence:
        print(f"    [{e[0]}] {e[1]}")
        print(f"        sha256={e[3]}  acquired={e[4]}")

    iocs = conn.execute(
        "SELECT ioc_type, value, context, added_at FROM iocs WHERE case_id = ?", (args.case_id,)
    ).fetchall()
    print(f"\n  IOCs ({len(iocs)}):")
    for i in iocs:
        print(f"    {i[0]}: {i[1]}  ({i[2] or 'no context'})")

    conn.close()


def export_case(args):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    case = conn.execute("SELECT * FROM cases WHERE id = ?", (args.case_id,)).fetchone()
    if not case:
        print(f"No case found with ID {args.case_id}", file=sys.stderr)
        sys.exit(1)

    evidence = conn.execute("SELECT * FROM evidence WHERE case_id = ?", (args.case_id,)).fetchall()
    evidence_out = []
    for e in evidence:
        custody = conn.execute(
            "SELECT action, actor, note, timestamp FROM custody_log WHERE evidence_id = ? ORDER BY timestamp",
            (e["id"],),
        ).fetchall()
        evidence_out.append(dict(e) | {"custody_log": [dict(c) for c in custody]})

    iocs = conn.execute("SELECT * FROM iocs WHERE case_id = ?", (args.case_id,)).fetchall()

    export = {
        "case": dict(case),
        "evidence": evidence_out,
        "iocs": [dict(i) for i in iocs],
        "exported_at": now(),
    }

    with open(args.output, "w") as f:
        json.dump(export, f, indent=2)

    conn.close()
    print(f"Exported case {args.case_id} to {args.output}")


def build_parser():
    parser = argparse.ArgumentParser(description="Lightweight DFIR case tracking CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize the local case database").set_defaults(func=lambda a: init_db())

    p = sub.add_parser("create-case", help="Create a new case")
    p.add_argument("--name", required=True)
    p.add_argument("--description", default="")
    p.set_defaults(func=create_case)

    p = sub.add_parser("add-evidence", help="Log a piece of evidence with SHA-256 hashing")
    p.add_argument("--case-id", type=int, required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--actor", default=None, help="Name of the person acquiring evidence")
    p.set_defaults(func=add_evidence)

    p = sub.add_parser("log-custody", help="Log a chain-of-custody event for existing evidence")
    p.add_argument("--evidence-id", type=int, required=True)
    p.add_argument("--action", required=True, help="e.g. transferred, analyzed, returned")
    p.add_argument("--actor", required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=log_custody_event)

    p = sub.add_parser("add-ioc", help="Add an indicator of compromise to a case")
    p.add_argument("--case-id", type=int, required=True)
    p.add_argument("--type", required=True, help="e.g. ip, domain, hash, email")
    p.add_argument("--value", required=True)
    p.add_argument("--context", default="")
    p.set_defaults(func=add_ioc)

    sub.add_parser("list-cases", help="List all cases").set_defaults(func=list_cases)

    p = sub.add_parser("show-case", help="Show full detail for a case")
    p.add_argument("--case-id", type=int, required=True)
    p.set_defaults(func=show_case)

    p = sub.add_parser("export-case", help="Export a case to JSON")
    p.add_argument("--case-id", type=int, required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=export_case)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
