# Digital Forensics & Incident Response (DFIR) Toolkit

Practitioner reference for digital forensics procedures — evidence handling, memory and disk acquisition, and chain-of-custody documentation — built to complement [incident-response-playbooks](https://github.com/mrezwanulbari/incident-response-playbooks) (the response *process*) with the forensic *technique* layer underneath it.

## Why This Exists

Incident response playbooks tell you what decisions to make during an incident. This repository covers the forensic mechanics behind those decisions — how to actually acquire memory without contaminating evidence, how to maintain a defensible chain of custody, and what artifacts matter for common investigation types. Both matter; conflating them is why a lot of published IR material is either too process-heavy to be technically actionable or too technical to guide decision-making under pressure.

## What's Inside

| Area | Description |
|---|---|
| `procedures/evidence-chain-of-custody-template.md` | Documentation template and handling procedure for maintaining defensible chain of custody from acquisition through analysis |
| `procedures/memory-acquisition-checklist.md` | Step-by-step memory acquisition procedure, including order-of-volatility considerations and common acquisition pitfalls |
| `procedures/` *(expanding)* | Additional forensic procedures (disk imaging, network forensics, mobile forensics) added as they're developed |

## Core Principles

- **Order of volatility** — capture the most volatile evidence first (memory, network connections) before less volatile evidence (disk, logs), since volatile evidence is lost the moment power is removed or time passes
- **Write-blocking discipline** — never analyze original evidence directly; work from verified forensic copies
- **Documentation as you go** — chain of custody gaps discovered after the fact are far harder to defend than documentation maintained in real time
- **Hash verification at every handoff** — every transfer of evidence between people or systems should be verified against a cryptographic hash of the original acquisition

## Who This Is For

DFIR analysts and incident responders needing acquisition procedures they can follow under time pressure, SOC teams building internal forensic readiness, and compliance/legal teams needing to understand what defensible evidence handling actually requires.

## Status

Actively maintained — new procedures added as they're developed and field-tested.

## About the Author

Maintained by Shakil Md. Rezwanul Bari, Cyber Security Engineer with 17+ years of experience including DFIR work across enterprise and financial-sector environments. Connect on [LinkedIn](https://www.linkedin.com/in/rezwanulbari/).

## License

MIT — see [LICENSE](LICENSE).
