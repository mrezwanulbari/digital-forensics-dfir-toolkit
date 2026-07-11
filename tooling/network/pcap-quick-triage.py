#!/usr/bin/env python3
"""
pcap_quick_triage.py — Fast first-pass triage of a packet capture file.

Produces the summary an analyst actually wants in the first five minutes
with a new pcap: top talkers by volume, protocol breakdown, and a flagged
list of connections to non-standard/high-risk ports — before diving into
full packet-level analysis in Wireshark or a deeper tool.

Requires: scapy (pip install scapy)

Usage:
    python3 pcap_quick_triage.py capture.pcap
    python3 pcap_quick_triage.py capture.pcap --top 20 --output triage_report.json
"""

import argparse
import json
import sys
from collections import Counter, defaultdict

try:
    from scapy.all import rdpcap, IP, TCP, UDP
except ImportError:
    print("Error: scapy is required. Install with: pip install scapy --break-system-packages", file=sys.stderr)
    sys.exit(1)

# Ports commonly worth flagging in a quick triage pass — not exhaustive,
# just the set that's saved real time by surfacing immediately rather than
# waiting for the analyst to notice them buried in a full connection list.
NOTABLE_PORTS = {
    23: "Telnet (unencrypted remote access)",
    445: "SMB (lateral movement / worm propagation vector)",
    3389: "RDP (remote access — verify against expected admin sources)",
    4444: "Common Metasploit default handler port",
    4899: "Radmin (common RAT/remote access tool port)",
    6667: "IRC (legacy C2 channel)",
    1337: "Commonly used by malware/tooling as a 'notable' port",
    8080: "Alt-HTTP (common proxy/C2 port, verify context)",
    8443: "Alt-HTTPS (common proxy/C2 port, verify context)",
}


def analyze(pcap_path, top_n):
    print(f"Loading {pcap_path}...")
    packets = rdpcap(pcap_path)
    print(f"Loaded {len(packets)} packets")

    talkers = Counter()
    protocol_counts = Counter()
    port_activity = Counter()
    flagged_connections = []
    conversations = defaultdict(int)

    for pkt in packets:
        if IP not in pkt:
            continue
        src, dst = pkt[IP].src, pkt[IP].dst
        talkers[src] += len(pkt)
        talkers[dst] += len(pkt)
        conversations[(src, dst)] += 1

        if TCP in pkt:
            protocol_counts["TCP"] += 1
            for port in (pkt[TCP].sport, pkt[TCP].dport):
                port_activity[port] += 1
                if port in NOTABLE_PORTS:
                    flagged_connections.append(
                        {"src": src, "dst": dst, "port": port, "reason": NOTABLE_PORTS[port]}
                    )
        elif UDP in pkt:
            protocol_counts["UDP"] += 1
            for port in (pkt[UDP].sport, pkt[UDP].dport):
                port_activity[port] += 1
                if port in NOTABLE_PORTS:
                    flagged_connections.append(
                        {"src": src, "dst": dst, "port": port, "reason": NOTABLE_PORTS[port]}
                    )
        else:
            protocol_counts["other"] += 1

    # Dedup flagged connections (same src/dst/port seen many times = one finding, not N)
    seen = set()
    deduped_flags = []
    for f in flagged_connections:
        key = (f["src"], f["dst"], f["port"])
        if key not in seen:
            seen.add(key)
            deduped_flags.append(f)

    top_talkers = talkers.most_common(top_n)
    top_conversations = sorted(conversations.items(), key=lambda x: x[1], reverse=True)[:top_n]

    report = {
        "pcap_file": pcap_path,
        "total_packets": len(packets),
        "protocol_breakdown": dict(protocol_counts),
        "top_talkers_by_packet_count": [{"ip": ip, "packets": count} for ip, count in top_talkers],
        "top_conversations": [
            {"src": src, "dst": dst, "packet_count": count} for (src, dst), count in top_conversations
        ],
        "flagged_notable_port_activity": deduped_flags,
    }
    return report


def print_summary(report):
    print("\n=== Quick Triage Summary ===")
    print(f"Total packets: {report['total_packets']}")
    print(f"Protocol breakdown: {report['protocol_breakdown']}")

    print(f"\nTop talkers (by packet volume):")
    for t in report["top_talkers_by_packet_count"][:10]:
        print(f"  {t['ip']:20s} {t['packets']} packets")

    print(f"\nTop conversations:")
    for c in report["top_conversations"][:10]:
        print(f"  {c['src']:16s} -> {c['dst']:16s}  ({c['packet_count']} packets)")

    if report["flagged_notable_port_activity"]:
        print(f"\n⚠ Flagged notable port activity ({len(report['flagged_notable_port_activity'])} unique):")
        for f in report["flagged_notable_port_activity"]:
            print(f"  {f['src']} -> {f['dst']}:{f['port']}  — {f['reason']}")
    else:
        print("\nNo notable-port activity flagged in this capture.")


def main():
    parser = argparse.ArgumentParser(description="Fast first-pass triage of a pcap file")
    parser.add_argument("pcap_file")
    parser.add_argument("--top", type=int, default=10, help="Number of top talkers/conversations to include")
    parser.add_argument("--output", help="Optional path to write full JSON report")
    args = parser.parse_args()

    report = analyze(args.pcap_file, args.top)
    print_summary(report)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nFull report written to {args.output}")


if __name__ == "__main__":
    main()
