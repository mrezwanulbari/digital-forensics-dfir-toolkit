# Related Open-Source DFIR Tools

This repository focuses on procedures, working CLI tooling, and templates built from direct practitioner experience — it intentionally does not try to be a comprehensive tool index. For that, the community-maintained [awesome-incident-response](https://github.com/meirwah/awesome-incident-response) list is the canonical, far more comprehensive resource and is the right place to go exploring the full ecosystem.

What follows here is a short, opinionated pointer list — the tools that show up repeatedly in real investigations — organized by the same category boundaries this repository uses, so it's easy to see where each fits alongside what's already here.

## Memory Analysis
- **[Volatility 3](https://github.com/volatilityfoundation/volatility3)** — the standard for memory image analysis; pairs directly with the [memory acquisition checklist](procedures/memory-acquisition-checklist.md) in this repo (acquire here, analyze there)

## Evidence Collection at Scale
- **[Velociraptor](https://github.com/Velocidex/velociraptor)** — fleet-wide endpoint visibility and evidence collection; the natural next step up from this repo's [Linux](tooling/scripts/linux-triage-collector.sh)/[Windows](tooling/scripts/windows-triage-collector.ps1)/[macOS](tooling/scripts/macos-triage-collector.sh) triage scripts when you need to collect from many hosts rather than one
- **[KAPE](https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape)** — targeted Windows artifact collection, a common companion to `windows-triage-collector.ps1` for deeper follow-up collection

## Disk Forensics
- **[Autopsy](https://www.autopsy.com/) / [The Sleuth Kit](https://github.com/sleuthkit/sleuthkit)** — the standard open-source disk image analysis platform, for the deep-dive work after live triage narrows down which systems need full imaging

## Timeline Analysis
- **[Plaso](https://github.com/log2timeline/plaso)** — automated super-timeline generation at scale; this repo's [`merge_timelines.py`](tooling/timeline-correlation/merge_timelines.py) covers the common case of merging a handful of already-extracted CSVs, Plaso is the right tool once you need to extract and correlate timeline data from raw disk/log sources directly

## Network Forensics
- **[Wireshark](https://www.wireshark.org/)** — full packet-level analysis once [`pcap-quick-triage.py`](tooling/network/pcap-quick-triage.py) has flagged what's worth a closer look
- **[Zeek](https://zeek.org/)** — network traffic analysis at scale, generates structured logs well-suited to SIEM ingestion (see [siem-soar-detection-engineering](https://github.com/mrezwanulbari/siem-soar-detection-engineering))

## Sandboxing / Malware Analysis
- **[CAPE Sandbox](https://github.com/kevoreilly/CAPEv2)** — automated malware behavioral analysis, useful when a triage collection turns up a suspicious binary worth detonating in isolation

## Adversary Emulation
- **[Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)** — small, testable adversary emulation actions mapped to MITRE ATT&CK, the natural validation step for the technique coverage tracked in [MITRE-ATT-CK-Threat-Defense-Framework](https://github.com/mrezwanulbari/MITRE-ATT-CK-Threat-Defense-Framework)

## Full Case Management Platforms
- **[IRIS](https://github.com/dfir-iris/iris-web)** — see the note in the main [README](README.md) on how this repository's lightweight `case-tracker` CLI relates to full platforms like this

---

For deeper category coverage (Linux distributions, communities, books, videos, and dozens more tools per category), see [awesome-incident-response](https://github.com/meirwah/awesome-incident-response).

*Part of the [digital-forensics-dfir-toolkit](README.md) repository.*
