# 🚀 NetworkMonitor Installation Guide

This guide will help you install and run NetworkMonitor on your computer in just a few minutes!

---

## 📥 Download Options

### Option 1: Download from GitHub Releases (Recommended)

1. Go to [**Releases Page**](https://github.com/umerfarok/networkmonitor/releases)
2. Download the latest version for your operating system:

| Platform | Download | Type |
|----------|----------|------|
| **Windows** | `NetworkMonitor-Windows-Setup-x.x.x.zip` | Installer (Recommended) |
| **Windows** | `NetworkMonitor-Windows-x.x.x.zip` | Portable Version |
| **Linux** | `NetworkMonitor-Linux-x.x.x.tar.gz` | Executable |
| **macOS** | `NetworkMonitor-macOS-x.x.x.zip` | Application Bundle |

---

## 🪟 Windows Installation

### Prerequisites (One-Time Setup)

Before running NetworkMonitor, you need **Npcap** for network packet capture:

1. Download Npcap from [https://npcap.com](https://npcap.com)
2. Run the installer **as Administrator**
3. ✅ **Important**: Check the box **"Install Npcap in WinPcap API-compatible Mode"**
4. Complete the installation

### Installing NetworkMonitor

#### Method A: Using the Installer (Recommended)

1. Download `NetworkMonitor-Windows-Setup-x.x.x.zip`
2. Extract the ZIP file
3. Right-click `NetworkMonitor_Setup.exe` and select **"Run as administrator"**
4. Follow the installation wizard
5. Launch from Start Menu or Desktop shortcut

#### Method B: Portable Version (No Installation)

1. Download `NetworkMonitor-Windows-x.x.x.zip`
2. Extract to any folder (e.g., `C:\NetworkMonitor`)
3. Right-click `NetworkMonitor.exe` and select **"Run as administrator"**

### Running NetworkMonitor

```
⚠️ IMPORTANT: Always run NetworkMonitor as Administrator!
Right-click → "Run as administrator"
```

1. Double-click `NetworkMonitor.exe` (or use Start Menu shortcut)
2. A status dashboard will appear
3. Your web browser will open automatically to `http://localhost:5000`
4. You'll see all devices connected to your network!

---

## 🐧 Linux Installation

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y libpcap-dev net-tools iptables

# Fedora/RHEL
sudo dnf install -y libpcap-devel net-tools iptables

# Arch Linux
sudo pacman -S libpcap net-tools iptables
```

### Installation

```bash
# 1. Download the latest release
wget https://github.com/umerfarok/networkmonitor/releases/latest/download/NetworkMonitor-Linux-x.x.x.tar.gz

# 2. Extract the archive
tar -xzf NetworkMonitor-Linux-*.tar.gz

# 3. Make it executable
chmod +x NetworkMonitor

# 4. Run with sudo (required for network access)
sudo ./NetworkMonitor
```

### Running

```bash
# Always run with sudo for network scanning
sudo ./NetworkMonitor
```

Open your browser and go to: `http://localhost:5000`

---

## 🍎 macOS Installation

### Prerequisites

```bash
# Install libpcap (usually pre-installed, but just in case)
brew install libpcap
```

### Installation

1. Download `NetworkMonitor-macOS-x.x.x.zip`
2. Extract the ZIP file
3. If you see a security warning:
   - Go to **System Preferences** → **Security & Privacy**
   - Click **"Open Anyway"**

### Running

```bash
# Run with sudo for network access
sudo ./NetworkMonitor
```

Or right-click the app and select **"Open"**, then enter your password.

Open your browser and go to: `http://localhost:5000`

---

## 🌐 Using the Web Dashboard

Once NetworkMonitor is running, the dashboard provides:

### Features
- 📊 **Device List**: See all devices on your network
- 🔍 **Device Details**: IP, MAC, Hostname, Vendor
- ⚡ **Speed Monitoring**: Real-time bandwidth usage
- 🔒 **Protection**: Protect devices from ARP attacks
- ✂️ **Network Cut**: Disconnect devices from the network
- 🚦 **Speed Limiting**: Control bandwidth per device

### Dashboard URL
```
http://localhost:5000
```

---

## ☁️ Using with Vercel-Hosted Frontend

NetworkMonitor supports a **hybrid setup** where the beautiful dashboard is hosted on Vercel:

### How It Works

```
┌─────────────────────┐         ┌──────────────────────┐
│   Your Computer     │         │    Vercel (Cloud)    │
│                     │         │                      │
│  NetworkMonitor.exe │◄────────│  Web Dashboard       │
│  (Backend API)      │  API    │  (React Frontend)    │
│  :5000              │  calls  │                      │
└─────────────────────┘         └──────────────────────┘
```

### Setup

1. **Start the local backend** on your computer:
   ```bash
   # Windows
   NetworkMonitor.exe
   
   # Linux/macOS
   sudo ./NetworkMonitor
   ```

2. **Access the Vercel dashboard**:
   - Go to the deployed Vercel URL (e.g., `https://your-app.vercel.app`)
   - The dashboard connects to `http://localhost:5000` automatically

3. **That's it!** The cloud dashboard controls your local network.

---

## 🔧 Troubleshooting

### "Npcap not found" (Windows)

1. Download Npcap from [npcap.com](https://npcap.com)
2. Run installer as Administrator
3. ✅ Enable "WinPcap API-compatible Mode"
4. Restart NetworkMonitor

### "Permission denied" (Linux/macOS)

```bash
# Must run with sudo
sudo ./NetworkMonitor
```

### "Cannot bind to port 5000"

Another application is using port 5000. Either:
- Close the other application
- Or change the port in settings

### "No devices found"

1. Make sure you're connected to a network
2. Run as Administrator/root
3. Check firewall settings
4. Try restarting NetworkMonitor

### Dashboard shows "Cannot connect to server"

1. Make sure NetworkMonitor.exe is running
2. Check if the firewall is blocking port 5000
3. Try accessing `http://localhost:5000/api/status` in your browser

---

## 📞 Getting Help

- **GitHub Issues**: [Report a bug](https://github.com/umerfarok/networkmonitor/issues)
- **Documentation**: [Read the docs](https://umerfarok.github.io/networkmonitor)
- **Logs**: Check application logs at:
  - Windows: `%LOCALAPPDATA%\NetworkMonitor\logs`
  - Linux/macOS: `~/.networkmonitor/logs`

---

## 🎉 Quick Reference

| Action | Command/Steps |
|--------|---------------|
| **Start** | Run `NetworkMonitor.exe` as Admin |
| **Access Dashboard** | Open `http://localhost:5000` |
| **Stop** | Click "Exit" or close the window |
| **View Logs** | `%LOCALAPPDATA%\NetworkMonitor\logs` |

---

## ⚠️ Important Notes

1. **Administrator/Root Required**: Network scanning requires elevated privileges
2. **ARP Scanning**: Some networks/routers may flag ARP scanning as suspicious activity
3. **Firewall**: Make sure port 5000 is allowed through your firewall
4. **Use Responsibly**: Only use on networks you own or have permission to monitor

---

**Happy Network Monitoring! 🎯**
