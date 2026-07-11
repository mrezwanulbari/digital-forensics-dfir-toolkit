#!/usr/bin/env python3
"""
merge_timelines.py — Merge multiple forensic artifact timelines (CSV) into a
single sorted "super timeline" with source attribution.

Common real-world use: you've pulled a filesystem MACB timeline, a browser
history export, and Windows Event Log timestamps into separate CSVs (from
whatever extraction tool produced them), and need one chronologically sorted
view to build an incident narrative — this is the manual step that tools
like Plaso automate at a much larger scale; this script covers the common
case of merging a handful of CSVs without needing a full Plaso deployment.

Expected input CSV format (flexible column names, mapped via --time-col /
--desc-col, but each file must have at minimum a timestamp column and a
description/event column):

    timestamp,description,...
    2026-07-09T14:22:01Z,"File created: C:\\Users\\...\\payload.exe",...

Usage:
    python3 merge_timelines.py \\
        --input filesystem_timeline.csv:filesystem \\
        --input browser_history.csv:browser \\
        --input event_logs.csv:eventlog \\
        --output super_timeline.csv \\
        --time-col timestamp --desc-col description
"""

import argparse
import csv
import sys
from datetime import datetime


def parse_timestamp(value):
    """
    Attempt to parse a range of common timestamp formats found across
    forensic extraction tools. Returns None if unparseable (row is kept
    but sorted last, with a warning) rather than crashing the whole merge
    over one malformed row — a single bad timestamp in a 50,000-row export
    shouldn't block the entire timeline build.
    """
    value = value.strip()
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_timeline(path, source_label, time_col, desc_col):
    rows = []
    skipped = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if time_col not in reader.fieldnames:
            print(f"Error: column '{time_col}' not found in {path}. Available columns: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)
        for row in reader:
            ts_raw = row.get(time_col, "")
            ts = parse_timestamp(ts_raw)
            if ts is None:
                skipped += 1
            rows.append(
                {
                    "timestamp_parsed": ts,
                    "timestamp_raw": ts_raw,
                    "source": source_label,
                    "description": row.get(desc_col, ""),
                    "raw_row": row,
                }
            )
    if skipped:
        print(f"Warning: {skipped} row(s) in {path} had unparseable timestamps and will sort last", file=sys.stderr)
    return rows


def merge(inputs, output_path, time_col, desc_col):
    all_rows = []
    for path, source_label in inputs:
        rows = load_timeline(path, source_label, time_col, desc_col)
        all_rows.extend(rows)
        print(f"Loaded {len(rows)} events from {path} (source: {source_label})")

    # Sort: parsed timestamps first in chronological order, unparseable ones last
    all_rows.sort(key=lambda r: (r["timestamp_parsed"] is None, r["timestamp_parsed"] or datetime.max))

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "source", "description"])
        for r in all_rows:
            ts_out = r["timestamp_parsed"].isoformat() if r["timestamp_parsed"] else f"UNPARSED:{r['timestamp_raw']}"
            writer.writerow([ts_out, r["source"], r["description"]])

    print(f"\nMerged {len(all_rows)} total events into {output_path}")


def parse_input_arg(value):
    if ":" not in value:
        print(f"Error: --input must be in format path:source_label, got '{value}'", file=sys.stderr)
        sys.exit(1)
    path, label = value.rsplit(":", 1)
    return path, label


def main():
    parser = argparse.ArgumentParser(description="Merge multiple forensic CSV timelines into one sorted super timeline")
    parser.add_argument("--input", action="append", required=True, help="path:source_label — repeat for each input file")
    parser.add_argument("--output", required=True)
    parser.add_argument("--time-col", default="timestamp")
    parser.add_argument("--desc-col", default="description")
    args = parser.parse_args()

    inputs = [parse_input_arg(v) for v in args.input]
    merge(inputs, args.output, args.time_col, args.desc_col)


if __name__ == "__main__":
    main()
