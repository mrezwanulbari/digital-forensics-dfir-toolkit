# Memory Acquisition Checklist

Step-by-step procedure for forensically sound memory acquisition, prioritized by order of volatility.

## Order of Volatility (Most to Least — Acquire in This Order If Multiple Types Needed)

1. CPU registers, cache — effectively impossible to capture forensically, generally out of scope
2. **Routing table, ARP cache, process table, kernel statistics, RAM** — capture immediately, lost on reboot/shutdown
3. Temporary file systems and swap space
4. Data on disk
5. Remote logging and monitoring data relevant to the system
6. Physical configuration and network topology
7. Archival media / backups

Memory acquisition sits at the most time-sensitive tier — every minute of delay risks losing forensically relevant data as the system continues normal operation and memory pages get overwritten.

## Pre-Acquisition Checklist

- [ ] Confirm the acquisition is authorized and scoped (which system, what evidence is being sought) before touching anything
- [ ] Identify the acquisition tool appropriate to the OS and confirm it's on trusted, write-protected external media — never install/run untrusted binaries from the target system's own storage
- [ ] Document system state before acquisition: date/time (compare against a trusted time source — note any clock drift), logged-in users, visible running processes, network connections
- [ ] **Do not shut down or restart the system before acquisition** — this is the single most common evidence-destroying mistake. Memory acquisition must happen on a running, live system.

## Acquisition Steps

1. Connect trusted external media containing the acquisition tool
2. Run the memory acquisition tool, directing output to the external media (never write acquisition output back to the target system's own disk)
3. Record start time, end time, and any errors/warnings the tool reports during acquisition
4. Immediately compute a cryptographic hash (SHA-256) of the acquired memory image
5. Record the hash in the chain-of-custody log (see [evidence-chain-of-custody-template.md](evidence-chain-of-custody-template.md)) before the media leaves your physical control

## Post-Acquisition

- [ ] Verify the acquired image is readable/parseable by your analysis tooling before considering the on-site acquisition complete — a corrupted acquisition discovered later, after the system has been rebooted or evidence otherwise degraded, cannot be redone
- [ ] Create a working copy for analysis; the original acquired image goes into controlled storage untouched
- [ ] Only proceed to less-volatile evidence collection (disk imaging, log collection) once memory acquisition is confirmed complete and verified

## Common Pitfalls

- **Acquiring memory after other responders have already interacted with the system** — every process launched, file opened, or network connection made after compromise (including by well-meaning IT staff investigating "what's wrong") overwrites memory pages and can destroy the evidence you're trying to capture. Memory acquisition should happen as early as possible in the response, ideally before extensive live triage.
- **Insufficient external storage capacity** — verify available capacity on acquisition media exceeds system RAM size before starting; a failed acquisition partway through due to storage exhaustion may still have altered system state without producing usable evidence.
- **Running acquisition tools with elevated privileges the investigator doesn't have documented authorization for** — confirm authorization scope explicitly before privilege escalation, not after.

---
*Part of the [digital-forensics-dfir-toolkit](../README.md) repository.*
