# Timeline Correlation Tool

Merges multiple forensic artifact timelines (CSV exports from filesystem MACB analysis, browser history, event logs, etc.) into a single chronologically sorted "super timeline" with source attribution — the manual correlation step that larger tools like [Plaso](https://github.com/log2timeline/plaso) automate at much greater scale, scoped here for the common case of merging a handful of CSVs without needing a full Plaso deployment.

## Requirements

Python 3.8+. Standard library only (`csv`, `datetime`, `argparse`).

## Usage

```bash
python3 merge_timelines.py \
    --input filesystem_timeline.csv:filesystem \
    --input browser_history.csv:browser \
    --input event_logs.csv:eventlog \
    --output super_timeline.csv \
    --time-col timestamp --desc-col description
```

Each `--input` is `path:source_label` — the label is preserved in the output so you can trace every event back to its origin artifact source.

## Input Format

Each input CSV needs at minimum a timestamp column and a description column (names configurable via `--time-col`/`--desc-col`, default `timestamp`/`description`):

```csv
timestamp,description
2026-07-09T14:22:01Z,"File created: C:\Users\jdoe\Downloads\payload.exe"
```

Supports several common timestamp formats out of the box (ISO 8601 with/without milliseconds, space-separated datetime, US-style with AM/PM). Rows with unparseable timestamps are kept (not dropped) and sorted to the end with a warning, rather than crashing the whole merge over one malformed row — a single bad row in a 50,000-row export shouldn't block the timeline build.

## Output

A single CSV: `timestamp, source, description`, sorted chronologically across all input sources — the format an analyst actually needs for building an incident narrative, where "what happened, in what order, across every artifact source" is the question, not "what happened in the filesystem" and "what happened in the event log" as separate disconnected views.

## Example

Given a filesystem timeline showing a file creation and an event log showing the resulting process launch, the merged output correctly interleaves them:

```csv
timestamp,source,description
2026-07-09T14:22:01,filesystem,"File created: payload.exe"
2026-07-09T14:23:45,eventlog,"Process creation: payload.exe (PID 4521) by jdoe"
```

This ordering — file dropped, then executed 104 seconds later — is exactly the kind of cross-source correlation that's easy to miss when reviewing each artifact source in isolation.

---
*Part of the [digital-forensics-dfir-toolkit](../../README.md) repository.*
