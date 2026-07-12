#!/usr/bin/env bash
#
# macos-triage-collector.sh — Live triage artifact collection for macOS hosts.
#
# Companion to linux-triage-collector.sh, adapted for macOS-specific tools
# and artifact locations (launchd instead of systemd/cron, plist-based
# persistence instead of registry keys, etc.). Collects in order of
# volatility and hashes the resulting bundle for chain-of-custody purposes.
#
# NOTE ON TESTING: Written and syntax-reviewed against documented macOS
# command behavior, but not execution-tested against a live macOS host (no
# macOS environment available in this repository's build process). Validate
# against a lab Mac before relying on it operationally — same caveat as
# windows-triage-collector.ps1. linux-triage-collector.sh is the one script
# in this set that has been executed and verified end-to-end.
#
# Usage:
#   sudo ./macos-triage-collector.sh [output_dir]
#
# Run with sudo for complete process/network visibility.

set -uo pipefail

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
run_collect "01_datetime_and_uptime" bash -c 'date -u; echo "---"; uptime; echo "---"; sw_vers'
run_collect "02_logged_in_users" bash -c 'who; echo "---last---"; last -20'
run_collect "03_network_connections" bash -c 'lsof -i -n -P 2>/dev/null; echo "---netstat---"; netstat -anp tcp; netstat -anp udp'
run_collect "04_arp_cache" bash -c 'arp -a'
run_collect "05_routing_table" bash -c 'netstat -rn'
run_collect "06_running_processes" bash -c 'ps -axo pid,ppid,user,%cpu,%mem,lstart,command'
run_collect "07_open_files" bash -c 'lsof -n 2>/dev/null | head -5000'
run_collect "08_loaded_kernel_extensions" bash -c 'kextstat 2>/dev/null || echo "kextstat unavailable (deprecated on newer macOS — check System Extensions instead via: systemextensionsctl list")'
run_collect "09_mounted_volumes" bash -c 'mount; echo "---"; diskutil list'

# --- Semi-volatile: persistence mechanisms (macOS-specific) ---
run_collect "10_launch_agents_daemons" bash -c '
    echo "=== System LaunchDaemons ==="; ls -la /System/Library/LaunchDaemons/ 2>/dev/null
    echo "=== Library LaunchDaemons ==="; ls -la /Library/LaunchDaemons/ 2>/dev/null
    echo "=== Library LaunchAgents ==="; ls -la /Library/LaunchAgents/ 2>/dev/null
    echo "=== User LaunchAgents ==="; for home in /Users/*; do
        [ -d "$home/Library/LaunchAgents" ] && { echo "--- $home ---"; ls -la "$home/Library/LaunchAgents/" 2>/dev/null; }
    done
'
run_collect "11_launchd_loaded_jobs" bash -c 'launchctl list'
run_collect "12_login_items" bash -c '
    for home in /Users/*; do
        f="$home/Library/Application Support/com.apple.backgroundtaskmanagementagent"
        echo "--- checking $home ---"
        osascript -e "tell application \"System Events\" to get the name of every login item" 2>/dev/null
    done
'
run_collect "13_cron_jobs" bash -c '
    echo "=== root crontab ==="; crontab -l 2>/dev/null
    for u in $(dscl . -list /Users 2>/dev/null); do
        echo "--- $u ---"; crontab -l -u "$u" 2>/dev/null
    done
'
run_collect "14_profiles_mdm" bash -c 'profiles list 2>/dev/null'
run_collect "15_recently_modified_files" bash -c 'find / -type f -mtime -1 -not -path "/proc/*" -not -path "/dev/*" 2>/dev/null | head -2000'
run_collect "16_quarantine_downloads" bash -c '
    for home in /Users/*; do
        [ -d "$home/Downloads" ] && { echo "--- $home/Downloads ---"; ls -la "$home/Downloads/" 2>/dev/null; }
    done
'
run_collect "17_shell_histories" bash -c '
    for home in /Users/* /var/root; do
        for hf in "$home/.bash_history" "$home/.zsh_history"; do
            [ -f "$hf" ] && { echo "--- $hf ---"; cat "$hf"; }
        done
    done
'
run_collect "18_installed_applications" bash -c 'ls -la /Applications/'
run_collect "19_gatekeeper_status" bash -c 'spctl --status; echo "---"; csrutil status 2>/dev/null'
run_collect "20_environment_variables" bash -c 'env'

# --- Bundle hash for chain of custody ---
log "Hashing collected bundle for chain-of-custody baseline"
find "$OUTDIR" -type f -exec shasum -a 256 {} \; > "$OUTDIR/../$(basename "$OUTDIR")_MANIFEST.sha256" 2>/dev/null

log "Triage collection complete: $OUTDIR"
log "Bundle manifest: $(dirname "$OUTDIR")/$(basename "$OUTDIR")_MANIFEST.sha256"
log "Record this manifest hash in your chain-of-custody log (see procedures/evidence-chain-of-custody-template.md)"
