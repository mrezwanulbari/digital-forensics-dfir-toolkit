# Network Forensics Tooling

## pcap-quick-triage.py

Fast first-pass triage of a packet capture: top talkers by volume, protocol breakdown, top conversations, and a flagged list of connections on notable/high-risk ports (RDP, SMB, common C2/RAT default ports) — the summary an analyst wants in the first five minutes with a new pcap, before diving into full packet analysis in Wireshark.

### Install

```bash
pip install -r requirements.txt
```

### Usage

```bash
python3 pcap_quick_triage.py capture.pcap
python3 pcap_quick_triage.py capture.pcap --top 20 --output triage_report.json
```

### What It Flags

A curated (not exhaustive) set of ports worth immediate attention: Telnet, SMB, RDP, common Metasploit/RAT default ports, and common alt-HTTP(S) proxy/C2 ports. This is a triage aid, not a detection engine — a flagged port is a prompt to look closer, not a confirmed finding. Expect and expand the `NOTABLE_PORTS` dictionary in the script for your specific environment's known-risky ports.

### Tested

Verified against a synthetic pcap with planted RDP and Metasploit-handler-port traffic — the tool correctly identified and flagged both while leaving normal HTTPS/DNS traffic unflagged.

---
*Part of the [digital-forensics-dfir-toolkit](../README.md) repository.*
