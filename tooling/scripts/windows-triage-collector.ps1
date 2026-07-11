<#
.SYNOPSIS
    windows-triage-collector.ps1 — Live triage artifact collection for Windows hosts.

.DESCRIPTION
    Collects volatile and semi-volatile data in order of volatility, writes
    everything to a timestamped output directory, and hashes the resulting
    bundle for chain-of-custody purposes.

    NOTE ON TESTING: This script is written and syntax-reviewed but has not
    been executed against a live Windows host as part of building this
    repository (no Windows environment available in the build sandbox).
    Validate against a lab VM before relying on it in a live response —
    treat it as a strong starting point, not a blindly-trusted production
    tool. The Linux equivalent (linux-triage-collector.sh) has been executed
    and verified end-to-end.

.NOTES
    Run from an elevated (Administrator) PowerShell session for complete
    process/handle/network visibility.

.EXAMPLE
    .\windows-triage-collector.ps1 -OutputDir C:\Triage
#>

param(
    [string]$OutputDir = ".\triage_$($env:COMPUTERNAME)_$(Get-Date -Format 'yyyyMMddTHHmmssZ')"
)

$ErrorActionPreference = "Continue"  # one failed collection step should not abort the whole run

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message"
}

function Invoke-Collect {
    param(
        [string]$Name,
        [scriptblock]$Script
    )
    Write-Log "Collecting: $Name"
    try {
        & $Script | Out-File -FilePath (Join-Path $OutputDir "$Name.txt") -Encoding utf8
    } catch {
        Write-Log "  warning: $Name collection failed: $($_.Exception.Message)"
        $_.Exception.Message | Out-File -FilePath (Join-Path $OutputDir "$Name.err") -Encoding utf8
    }
}

Write-Log "Starting triage collection on $env:COMPUTERNAME -> $OutputDir"
Write-Log "Collection order follows volatility: network/process state first, filesystem artifacts last"

# --- Highest volatility: live system state ---
Invoke-Collect "01_datetime_and_uptime" { Get-Date; Write-Output "---"; (Get-CimInstance Win32_OperatingSystem).LastBootUpTime }
Invoke-Collect "02_logged_on_users" { quser 2>$null; Write-Output "---"; Get-CimInstance Win32_LoggedOnUser | Select-Object Antecedent, Dependent }
Invoke-Collect "03_network_connections" { Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess }
Invoke-Collect "04_arp_cache" { Get-NetNeighbor }
Invoke-Collect "05_routing_table" { Get-NetRoute }
Invoke-Collect "06_running_processes" { Get-Process | Select-Object Id, ProcessName, Path, StartTime, Company }
Invoke-Collect "07_process_command_lines" { Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name, CommandLine }
Invoke-Collect "08_dns_cache" { Get-DnsClientCache }
Invoke-Collect "09_loaded_drivers" { Get-CimInstance Win32_SystemDriver | Where-Object { $_.State -eq "Running" } | Select-Object Name, PathName, State }

# --- Semi-volatile: configuration and persistence mechanisms ---
Invoke-Collect "10_scheduled_tasks" { Get-ScheduledTask | Where-Object { $_.State -ne "Disabled" } | Select-Object TaskName, TaskPath, State }
Invoke-Collect "11_services" { Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartMode, PathName }
Invoke-Collect "12_autorun_registry_keys" {
    $keys = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    )
    foreach ($k in $keys) {
        Write-Output "--- $k ---"
        Get-ItemProperty -Path $k -ErrorAction SilentlyContinue
    }
}
Invoke-Collect "13_local_admin_group_members" { Get-LocalGroupMember -Group "Administrators" }
Invoke-Collect "14_recently_modified_files" {
    Get-ChildItem -Path C:\Users -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) } |
        Select-Object FullName, LastWriteTime, Length |
        Select-Object -First 2000
}
Invoke-Collect "15_prefetch_listing" { Get-ChildItem -Path C:\Windows\Prefetch -ErrorAction SilentlyContinue | Select-Object Name, LastWriteTime }
Invoke-Collect "16_installed_software" { Get-CimInstance Win32_Product | Select-Object Name, Version, InstallDate }
Invoke-Collect "17_environment_variables" { Get-ChildItem Env: }
Invoke-Collect "18_powershell_history" {
    $histPath = (Get-PSReadlineOption).HistorySavePath
    if (Test-Path $histPath) { Get-Content $histPath }
}

# --- Bundle hash for chain of custody ---
Write-Log "Hashing collected bundle for chain-of-custody baseline"
$manifestPath = "$OutputDir`_MANIFEST.sha256"
Get-ChildItem -Path $OutputDir -File | ForEach-Object {
    $hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
    "$($hash.Hash)  $($_.Name)" | Out-File -FilePath $manifestPath -Append -Encoding utf8
}

Write-Log "Triage collection complete: $OutputDir"
Write-Log "Bundle manifest hash file: $manifestPath"
Write-Log "Record this manifest hash in your chain-of-custody log (see procedures/evidence-chain-of-custody-template.md)"
