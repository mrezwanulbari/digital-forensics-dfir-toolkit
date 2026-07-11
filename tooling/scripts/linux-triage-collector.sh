#!/usr/bin/env bash
#
# linux-triage-collector.sh — Live triage artifact collection for Linux hosts.
#
# Collects volatile and semi-volatile data in order of volatility, writes
# everything to a timestamped output directory, and hashes the resulting
# bundle for chain-of-custody purposes. Designed to run with minimal
# dependencies (standard coreutils + procps) so it works on a stripped-down
# production host, not just a full analyst workstation.
#
# Usage:
#   sudo ./linux-triage-collector.sh [output_dir]
#
# Run as root (or with sudo) for complete process/network visibility —
# running unprivileged will silently omit other users' processes and some
# network detail, which is worse than an explicit permission error.

set -uo pipefail  # deliberately not -e: one failed collection step should not abort the whole run

OUTDIR="${1:-./triage_$(hostname)_$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUTDIR"

log() { echo "[$(date -u +%H:%M:%S)] $*"; }

run_collect() {
    local name="$1"; shift
    log "Collecting: $name"
    { "$@" ; } > "$OUTDIR/$name.txt" 2>"$OUTDIR/$name.err" || log "  warning: $name collection reported errors (see $name.err)"
}

log "Starting triage collection on $(hostname) -> $OUTDIR"
log "Collection order follows volatility: network/process state first, filesystem artifacts last"

# --- Highest volatility: live system state ---
run_collect "01_datetime_and_uptime" bash -c 'date -u; echo "---"; uptime; echo "---"; timedatectl 2>/dev/null || true'
run_collect "02_logged_in_users" bash -c 'who -a; echo "---last---"; last -n 50'
run_collect "03_network_connections" bash -c 'ss -tulanp 2>/dev/null || netstat -tulanp 2>/dev/null'
run_collect "04_arp_cache" bash -c 'ip neigh show 2>/dev/null || arp -a'
run_collect "05_routing_table" bash -c 'ip route show 2>/dev/null || route -n'
run_collect "06_running_processes" bash -c 'ps -auxww'
run_collect "07_process_tree" bash -c 'ps -ef --forest 2>/dev/null || ps -ejH'
run_collect "08_open_files" bash -c 'lsof -n 2>/dev/null | head -5000'
run_collect "09_loaded_kernel_modules" bash -c 'lsmod'
run_collect "10_mounted_filesystems" bash -c 'mount; echo "---"; df -h'

# --- Semi-volatile: configuration and persistence mechanisms ---
run_collect "11_scheduled_tasks_cron" bash -c '
    echo "=== system crontab ==="; cat /etc/crontab 2>/dev/null
    echo "=== cron.d ==="; for f in /etc/cron.d/*; do echo "--- $f ---"; cat "$f" 2>/dev/null; done
    echo "=== user crontabs ==="; for u in $(cut -f1 -d: /etc/passwd); do echo "--- $u ---"; crontab -l -u "$u" 2>/dev/null; done
'
run_collect "12_systemd_services" bash -c 'systemctl list-units --type=service --all 2>/dev/null'
run_collect "13_systemd_timers" bash -c 'systemctl list-timers --all 2>/dev/null'
run_collect "14_startup_files" bash -c '
    for f in /etc/rc.local /etc/profile /etc/bash.bashrc; do
        echo "--- $f ---"; cat "$f" 2>/dev/null
    done
'
run_collect "15_ssh_authorized_keys" bash -c '
    for home in /root /home/*; do
        f="$home/.ssh/authorized_keys"
        [ -f "$f" ] && { echo "--- $f ---"; cat "$f"; }
    done
'
run_collect "16_recently_modified_files" bash -c 'find / -xdev -type f -mmin -1440 -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null | head -2000'
run_collect "17_suid_sgid_binaries" bash -c 'find / -xdev \( -perm -4000 -o -perm -2000 \) -type f 2>/dev/null'
run_collect "18_shell_histories" bash -c '
    for home in /root /home/*; do
        for hf in "$home/.bash_history" "$home/.zsh_history"; do
            [ -f "$hf" ] && { echo "--- $hf ---"; cat "$hf"; }
        done
    done
'
run_collect "19_installed_packages" bash -c 'dpkg -l 2>/dev/null || rpm -qa 2>/dev/null'
run_collect "20_environment_variables" bash -c 'env'

# --- Bundle hash for chain of custody ---
log "Hashing collected bundle for chain-of-custody baseline"
find "$OUTDIR" -type f -exec sha256sum {} \; > "$OUTDIR/../$(basename "$OUTDIR")_MANIFEST.sha256" 2>/dev/null
sha256sum "$OUTDIR/../$(basename "$OUTDIR")_MANIFEST.sha256" 2>/dev/null

log "Triage collection complete: $OUTDIR"
log "Bundle manifest hash: $(dirname "$OUTDIR")/$(basename "$OUTDIR")_MANIFEST.sha256"
log "Record this manifest hash in your chain-of-custody log (see procedures/evidence-chain-of-custody-template.md)"
