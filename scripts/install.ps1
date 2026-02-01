# NetworkMonitor Windows Installation Script
# Usage: irm https://raw.githubusercontent.com/umerfarok/networkmonitor/main/scripts/install.ps1 | iex
# Or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "    NetworkMonitor Installation" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator." -ForegroundColor Yellow
    Write-Host "Some features may require admin rights." -ForegroundColor Yellow
    Write-Host ""
}

# Check for Npcap
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$npcapInstalled = Test-Path "C:\Windows\System32\Npcap\wpcap.dll"
$winpcapInstalled = Test-Path "C:\Windows\System32\wpcap.dll"

if (-not $npcapInstalled -and -not $winpcapInstalled) {
    Write-Host ""
    Write-Host "WARNING: Npcap is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "NetworkMonitor requires Npcap for network scanning." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please:" -ForegroundColor White
    Write-Host "  1. Download Npcap from: https://npcap.com" -ForegroundColor Gray
    Write-Host "  2. Run the installer as Administrator" -ForegroundColor Gray
    Write-Host "  3. Check 'Install Npcap in WinPcap API-compatible Mode'" -ForegroundColor Gray
    Write-Host ""
    
    $response = Read-Host "Open Npcap download page? (y/n)"
    if ($response -eq 'y') {
        Start-Process "https://npcap.com"
    }
    
    Write-Host ""
    Write-Host "After installing Npcap, run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Npcap: OK" -ForegroundColor Green

# Get latest release
Write-Host ""
Write-Host "Finding latest release..." -ForegroundColor Yellow

try {
    $releases = Invoke-RestMethod -Uri "https://api.github.com/repos/umerfarok/networkmonitor/releases/latest"
    $version = $releases.tag_name
    
    Write-Host "Latest version: $version" -ForegroundColor Green
} catch {
    Write-Host "Error: Could not fetch release information." -ForegroundColor Red
    Write-Host "Please download manually from:" -ForegroundColor Yellow
    Write-Host "https://github.com/umerfarok/networkmonitor/releases" -ForegroundColor Cyan
    exit 1
}

# Find Windows installer
$asset = $releases.assets | Where-Object { $_.name -like "*Windows-Setup*" } | Select-Object -First 1

if (-not $asset) {
    $asset = $releases.assets | Where-Object { $_.name -like "*Windows*" } | Select-Object -First 1
}

if (-not $asset) {
    Write-Host "Error: No Windows release found." -ForegroundColor Red
    exit 1
}

$downloadUrl = $asset.browser_download_url
$fileName = $asset.name
$downloadPath = Join-Path $env:TEMP $fileName

Write-Host ""
Write-Host "Downloading $fileName..." -ForegroundColor Yellow

try {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "Error downloading: $_" -ForegroundColor Red
    exit 1
}

# Extract if zip
$extractPath = Join-Path $env:TEMP "NetworkMonitor_Install"
if (Test-Path $extractPath) {
    Remove-Item $extractPath -Recurse -Force
}

Write-Host "Extracting..." -ForegroundColor Yellow

if ($fileName -like "*.zip") {
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
} else {
    # If it's already an exe, just copy it
    New-Item -ItemType Directory -Path $extractPath -Force | Out-Null
    Copy-Item $downloadPath $extractPath
}

# Find installer or executable
$installer = Get-ChildItem -Path $extractPath -Recurse -Filter "*Setup*.exe" | Select-Object -First 1
$executable = Get-ChildItem -Path $extractPath -Recurse -Filter "NetworkMonitor.exe" | Select-Object -First 1

if ($installer) {
    Write-Host ""
    Write-Host "Found installer: $($installer.Name)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Launching installer..." -ForegroundColor Yellow
    Write-Host "(Follow the installation wizard)" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process -FilePath $installer.FullName -Wait
    
} elseif ($executable) {
    # Portable mode - install to Program Files
    $installDir = "C:\Program Files\NetworkMonitor"
    
    Write-Host ""
    Write-Host "Installing to: $installDir" -ForegroundColor Yellow
    
    if (-not $isAdmin) {
        Write-Host "Error: Installing to Program Files requires Administrator rights." -ForegroundColor Red
        Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
        exit 1
    }
    
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Copy-Item -Path (Join-Path $extractPath "*") -Destination $installDir -Recurse -Force
    
    # Create desktop shortcut
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\NetworkMonitor.lnk")
    $Shortcut.TargetPath = Join-Path $installDir "NetworkMonitor.exe"
    $Shortcut.WorkingDirectory = $installDir
    $Shortcut.Description = "NetworkMonitor - Network Monitoring Tool"
    $Shortcut.Save()
    
    Write-Host "Created desktop shortcut" -ForegroundColor Green
} else {
    Write-Host "Error: Could not find installer or executable." -ForegroundColor Red
    Write-Host "Please install manually from: $extractPath" -ForegroundColor Yellow
    exit 1
}

# Cleanup
Remove-Item $downloadPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "    Installation Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start NetworkMonitor:" -ForegroundColor White
Write-Host "  1. Right-click 'NetworkMonitor' shortcut" -ForegroundColor Gray
Write-Host "  2. Select 'Run as administrator'" -ForegroundColor Gray
Write-Host ""
Write-Host "Dashboard will open at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Run as Administrator for network scanning!" -ForegroundColor Yellow
Write-Host ""

$response = Read-Host "Launch NetworkMonitor now? (y/n)"
if ($response -eq 'y') {
    $exePath = "C:\Program Files\NetworkMonitor\NetworkMonitor.exe"
    if (Test-Path $exePath) {
        if ($isAdmin) {
            Start-Process $exePath
        } else {
            Start-Process $exePath -Verb RunAs
        }
    } else {
        Write-Host "Please launch from the Start Menu or Desktop shortcut." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Thank you for installing NetworkMonitor!" -ForegroundColor Green
Write-Host ""
