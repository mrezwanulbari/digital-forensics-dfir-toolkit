# Digital Forensics & Incident Response (DFIR) Toolkit

Practitioner reference and working tooling for digital forensics — evidence handling, live triage collection (Linux/Windows), network forensics, chain-of-custody documentation, case tracking, and timeline correlation. Built to complement [incident-response-playbooks](https://github.com/mrezwanulbari/incident-response-playbooks) (the response *process*) with the forensic *technique and tooling* layer underneath it.

## What's Inside

### Procedures
| File | Description |
|---|---|
| `procedures/evidence-chain-of-custody-template.md` | Documentation template and handling procedure for defensible chain of custody |
| `procedures/memory-acquisition-checklist.md` | Step-by-step memory acquisition procedure, order-of-volatility considerations |

### Live Triage Collection Scripts
| Script | Platform | Testing Status |
|---|---|---|
| `tooling/scripts/linux-triage-collector.sh` | Linux | **Tested end-to-end** — verified running against a live container, collects 20 categories of volatile/semi-volatile data, degrades gracefully when a tool (e.g. `systemctl`) isn't present rather than aborting |
| `tooling/scripts/windows-triage-collector.ps1` | Windows | Written and syntax-reviewed; **not execution-tested** (no Windows environment available in this repository's build process) — validate against a lab VM before relying on it operationally |

### Network Forensics
| Tool | Description |
|---|---|
| `tooling/network/pcap-quick-triage.py` | Fast pcap triage: top talkers, protocol breakdown, flagged notable-port activity (RDP, SMB, common C2 ports). **Tested** against a synthetic capture with planted suspicious traffic — correctly flagged it. Requires `scapy` (see `tooling/network/requirements.txt`) |

### Case Management & Timeline Tooling
| Tool | Description |
|---|---|
| `tooling/case-tracker/` | Stdlib-only Python CLI: case tracking, automatic SHA-256 evidence hashing, chain-of-custody event logging, IOC tracking (SQLite-backed). **Tested end-to-end.** |
| `tooling/timeline-correlation/` | Merges multi-source forensic CSV timelines into one chronologically sorted super timeline. **Tested** with multi-source sample data. |
| `tooling/docker/` | Dockerfile + docker-compose for running the case tracker containerized, no local Python setup needed. Written following standard practice; **not build-tested** (no Docker available in this repository's build process) — validate the build yourself before relying on it. |

### Schema & Templates
| File | Description |
|---|---|
| `schema/case-export-schema.json` | Formal JSON Schema for the case tracker's export format. **Validated** against a real export produced by `case_tracker.py`. |
| `templates/dfir-report-template.md` | Final investigation report structure — executive summary separated from technical findings, timeline, evidence summary, IOCs, root cause, and prioritized recommendations |

## Relationship to Full-Scale Platforms

For multi-analyst teams needing a web UI, role-based access, and collaborative case workflows, a purpose-built case-management platform — [IRIS](https://github.com/dfir-iris/iris-web) is a strong open-source example — is the right tool, and this repository doesn't attempt to replace that. The tooling here is scoped for solo/field use and for understanding the underlying data model (case → evidence → custody events → IOCs) at a level that's easy to read, audit, and extend.

## Core Principles

- **Order of volatility** — network/process state before disk, disk before archival media
- **Write-blocking discipline** — analyze copies, never originals
- **Documentation as you go** — a custody gap found later is far harder to defend than one avoided in real time
- **Hash verification at every handoff**
- **Honest testing status** — every tool above states whether it's been executed and verified, or written but not yet run in its target environment. Treat the latter as a strong draft, not a trusted production tool, until you've validated it yourself.

## Who This Is For

DFIR analysts and incident responders needing acquisition procedures and lightweight tooling they can actually run, SOC teams building internal forensic readiness, and compliance/legal teams needing to understand what defensible evidence handling requires.

## Status

Actively maintained — new procedures and tooling added as they're developed and field-tested.

## About the Author

Maintained by Shakil Md. Rezwanul Bari, Cyber Security Engineer with 17+ years of experience including DFIR work across enterprise and financial-sector environments. Connect on [LinkedIn](https://www.linkedin.com/in/rezwanulbari/).

## License

MIT — see [LICENSE](LICENSE).
