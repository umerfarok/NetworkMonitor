# ⚡ Quick Start Guide

**Get NetworkMonitor running in 2 minutes!**

---

## 🪟 Windows (One-Line Install)

### Step 1: Install Npcap (one-time)
1. Download from [npcap.com](https://npcap.com)
2. Run as Administrator
3. ☑️ Check "WinPcap API-compatible Mode"

### Step 2: Install NetworkMonitor

**Option A - One-Line PowerShell:**
```powershell
irm https://raw.githubusercontent.com/umerfarok/networkmonitor/main/scripts/install.ps1 | iex
```

**Option B - Manual Download:**
1. [**Download Latest Release**](https://github.com/umerfarok/networkmonitor/releases/latest)
2. Get `NetworkMonitor-Windows-Setup-*.zip`
3. Extract and run `NetworkMonitor_Setup.exe` as Administrator

### Step 3: Run
Right-click **NetworkMonitor** → **Run as administrator**

Dashboard opens at: `http://localhost:5000`

---

## 🐧 Linux (One-Line Install)

```bash
curl -sSL https://raw.githubusercontent.com/umerfarok/networkmonitor/main/scripts/install.sh | sudo bash
```

Or manually:
```bash
# Install dependencies
sudo apt install -y libpcap-dev

# Download and run
wget https://github.com/umerfarok/networkmonitor/releases/latest/download/NetworkMonitor-Linux-*.tar.gz
tar -xzf NetworkMonitor-Linux-*.tar.gz
sudo ./NetworkMonitor
```

Dashboard: `http://localhost:5000`

---

## 🍎 macOS (One-Line Install)

```bash
curl -sSL https://raw.githubusercontent.com/umerfarok/networkmonitor/main/scripts/install.sh | bash
```

Or manually:
```bash
curl -LO https://github.com/umerfarok/networkmonitor/releases/latest/download/NetworkMonitor-macOS-*.zip
unzip NetworkMonitor-macOS-*.zip
sudo ./NetworkMonitor
```

Dashboard: `http://localhost:5000`

---

## ☁️ Using with Vercel (Cloud Dashboard)

1. **Start NetworkMonitor locally** (see above)
2. **Visit** your Vercel deployment URL
3. Dashboard connects to `localhost:5000` automatically

---

## 🖥️ What You Can Do

| Feature | Description |
|---------|-------------|
| 📊 **View Devices** | See all devices on your network |
| ✂️ **Cut Connection** | Disconnect any device instantly |
| 🔄 **Restore** | Bring device back online |
| 🔒 **Protect** | Shield device from attacks |
| ⚡ **Limit Speed** | Set bandwidth limits |
| 📈 **Monitor** | Real-time traffic stats |

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Npcap not found" | [Download & install Npcap](https://npcap.com) |
| "Permission denied" | Run as Admin / with sudo |
| "Cannot connect" | Check if port 5000 is open |
| "No devices found" | Connect to WiFi/Ethernet first |

---

**Need more help?** See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.
