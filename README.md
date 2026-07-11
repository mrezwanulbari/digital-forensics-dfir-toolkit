# Digital Forensics & Incident Response (DFIR) Toolkit

Practitioner reference and working tooling for digital forensics — evidence handling, memory and disk acquisition, chain-of-custody documentation, case tracking, and timeline correlation — built to complement [incident-response-playbooks](https://github.com/mrezwanulbari/incident-response-playbooks) (the response *process*) with the forensic *technique and tooling* layer underneath it.

## Why This Exists

Incident response playbooks tell you what decisions to make during an incident. This repository covers the forensic mechanics behind those decisions: how to actually acquire memory without contaminating evidence, how to maintain a defensible chain of custody, and functional tooling for case tracking and timeline correlation when a full case-management platform isn't the right fit for the job.

## What's Inside

### Procedures
| File | Description |
|---|---|
| `procedures/evidence-chain-of-custody-template.md` | Documentation template and handling procedure for defensible chain of custody from acquisition through analysis |
| `procedures/memory-acquisition-checklist.md` | Step-by-step memory acquisition procedure, including order-of-volatility considerations and common pitfalls |

### Tooling (working code, not just documentation)
| Tool | Description |
|---|---|
| [`tooling/case-tracker/`](tooling/case-tracker/) | Stdlib-only Python CLI for case tracking, automatic SHA-256 evidence hashing, chain-of-custody event logging, and IOC tracking — backed by local SQLite |
| [`tooling/timeline-correlation/`](tooling/timeline-correlation/) | Merges multiple forensic artifact CSVs (filesystem, browser history, event logs) into one chronologically sorted super timeline with source attribution |

Both tools are dependency-free (Python standard library only) and tested end-to-end — see each tool's own README for usage.

## Relationship to Full-Scale Platforms

For multi-analyst teams needing a web UI, role-based access, and collaborative case workflows, a purpose-built case-management platform — [IRIS](https://github.com/dfir-iris/iris-web) is a strong open-source example — is the right tool, and this repository doesn't attempt to replace that. The tooling here is scoped for solo/field use and for understanding the underlying data model (case → evidence → custody events → IOCs) at a level that's easy to read, audit, and extend, rather than standing up full infrastructure.

## Core Principles

- **Order of volatility** — capture the most volatile evidence first (memory, network connections) before less volatile evidence (disk, logs)
- **Write-blocking discipline** — never analyze original evidence directly; work from verified forensic copies
- **Documentation as you go** — chain of custody gaps discovered after the fact are far harder to defend than documentation maintained in real time
- **Hash verification at every handoff** — every transfer of evidence should be verified against a cryptographic hash of the original acquisition

## Who This Is For

DFIR analysts and incident responders needing acquisition procedures and lightweight tooling they can actually run, SOC teams building internal forensic readiness, and compliance/legal teams needing to understand what defensible evidence handling requires.

## Status

Actively maintained — new procedures and tooling added as they're developed and field-tested.

## About the Author

Maintained by Shakil Md. Rezwanul Bari, Cyber Security Engineer with 17+ years of experience including DFIR work across enterprise and financial-sector environments. Connect on [LinkedIn](https://www.linkedin.com/in/rezwanulbari/).

## License

MIT — see [LICENSE](LICENSE).
