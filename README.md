# 🌐 NetworkMonitor

**A powerful network monitoring and control tool - Better than NetCut!**

[![Release](https://img.shields.io/github/v/release/umerfarok/networkmonitor?style=for-the-badge)](https://github.com/umerfarok/networkmonitor/releases)
[![Downloads](https://img.shields.io/github/downloads/umerfarok/networkmonitor/total?style=for-the-badge)](https://github.com/umerfarok/networkmonitor/releases)
[![License](https://img.shields.io/github/license/umerfarok/networkmonitor?style=for-the-badge)](LICENSE)

📖 **Documentation**: [umerfarok.github.io/networkmonitor](https://umerfarok.github.io/networkmonitor)

---

## 🎯 One-Click Installation (Windows)

**Just download and run - everything is included!**

### [⬇️ Download NetworkMonitor Installer](https://github.com/umerfarok/networkmonitor/releases/latest)

1. **Download** `NetworkMonitor-Windows-Setup-*.exe`
2. **Double-click** to install (right-click → Run as administrator)
3. **Done!** Dashboard opens automatically

> ✅ **No manual setup required!** The installer automatically installs:
> - NetworkMonitor application
> - Npcap driver (for network scanning)
> - All required components
> - Firewall rules

---

## 📱 Other Platforms

| Platform | Download | Notes |
|----------|----------|-------|
| **Linux** | [Download](https://github.com/umerfarok/networkmonitor/releases/latest) | Run with `sudo ./NetworkMonitor` |
| **macOS** | [Download](https://github.com/umerfarok/networkmonitor/releases/latest) | Run with `sudo ./NetworkMonitor` |

> 📚 **Need help?** See [QUICK_START.md](QUICK_START.md) or [INSTALLATION.md](INSTALLATION.md)

---

## ✨ Features

- 🖥️ **Device Discovery**: See all devices on your network
- ✂️ **Network Cut/Restore**: Disconnect devices using ARP spoofing
- 🔒 **Protection**: Protect devices from ARP attacks
- ⚡ **Speed Limiting**: Control bandwidth per device
- 📊 **Real-time Monitoring**: Live bandwidth and connection stats
- 🌐 **Modern Web Dashboard**: Beautiful React-based UI
- 🖱️ **Drag & Drop**: Easy device management
- 💻 **Cross-Platform**: Windows, Linux, macOS support
- ☁️ **Vercel Support**: Host dashboard in cloud, run backend locally

## Running NetworkMonitor

1. Launch NetworkMonitor from the Start Menu or desktop shortcut.
   - Ensure you run it as administrator
   - A modern status dashboard will appear showing the application status
   - The web interface will open automatically in your default browser

2. Using the Status Dashboard:
   - Monitor application status through the visual indicator
   - Click "Open in Browser" to access the web interface
   - Use "Run in Background" to minimize to system tray
   - Copy the web interface URL with one click
   - Exit safely using the Exit button

3. System Tray Features:
   - Minimize the application to system tray for background operation
   - Right-click the tray icon for quick access to common actions
   - Double-click to restore the dashboard window

4. If you see any dependency warnings:
   - Verify that all prerequisites are installed
   - Check that Python packages are installed correctly
   - Refer to the troubleshooting section below

## Troubleshooting

### Common Issues

1. "Npcap not found" error:
   - Ensure Npcap is installed from https://npcap.com
   - Try reinstalling Npcap with "WinPcap API-compatible Mode" checked

2. Python package errors:
   - Open an administrator command prompt
   - Run: `pip install -r "C:\Program Files\NetworkMonitor\requirements.txt"`

3. "Administrator privileges required":
   - Right-click NetworkMonitor shortcut
   - Select "Run as administrator"

4. UI Display Issues:
   - Ensure your Windows theme is set to 100% scaling
   - Update your graphics drivers
   - Try running with compatibility mode if needed

### Getting Help

If you encounter issues:
1. Check the application logs at `%LOCALAPPDATA%\NetworkMonitor\logs`
2. Open an issue on our GitHub repository
3. Include error messages and logs when reporting issues

## Quick Start (Easy Installation)

1. **Download** NetworkMonitor to your computer

2. **Run the installer** (as Administrator):
   ```cmd
   install.bat
   ```

3. **Start the application**:
   ```cmd
   start.bat
   ```

4. **Open your browser** and go to: http://localhost:5000

That's it! The dashboard will show all devices on your network.

## Using with Vercel (Cloud Dashboard)

NetworkMonitor supports a **hybrid architecture** where the frontend is hosted on Vercel and connects to your local backend:

### How it Works
- **Frontend (Vercel)**: Beautiful, responsive dashboard accessible from anywhere
- **Backend (Local)**: Runs on your computer with admin privileges for network scanning

### Setup

1. **Start the local backend**:
   ```cmd
   start.bat
   ```

2. **Access the Vercel-hosted dashboard** at your deployment URL

3. The dashboard will automatically connect to `http://localhost:5000`

### Environment Variables (Vercel)

Set `NEXT_PUBLIC_API_URL` in your Vercel project settings if using a different backend URL.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Your Computer                              │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────┐    ┌─────────────────────────────┐  │
│  │   Local Backend    │    │    Network Interface        │  │
│  │   (Flask API)      │───▶│    (WiFi/Ethernet)          │  │
│  │   Port 5000        │    │                             │  │
│  └────────────────────┘    └─────────────────────────────┘  │
│           ▲                                                   │
└───────────│───────────────────────────────────────────────────┘
            │
            │ CORS-enabled API calls
            │
┌───────────▼───────────────────────────────────────────────────┐
│                    Vercel (Cloud)                              │
├───────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  Next.js Frontend                       │  │
│  │                  (React Dashboard)                      │  │
│  │           https://your-app.vercel.app                   │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/umerfarok/networkmonitor.git
   ```

2. Install development dependencies:
   ```
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

3. Install Node.js dependencies for the web interface:
   ```
   cd networkmonitor/web
   npm install
   ```

4. Run the backend (with admin privileges):
   ```
   python -m networkmonitor
   ```

5. Run the frontend (in another terminal):
   ```
   cd networkmonitor/web
   npm run dev
   ```

6. Access the dashboard at http://localhost:3000

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Check server status |
| `/api/devices` | GET | List all discovered devices |
| `/api/device/block` | POST | Block a device by IP |
| `/api/device/cut` | POST | Cut device network access (ARP spoof) |
| `/api/device/restore` | POST | Restore device network access |
| `/api/device/protect` | POST | Protect a device from attacks |
| `/api/device/limit` | POST | Set speed limit for a device |
| `/api/network/gateway` | GET | Get gateway information |
| `/api/wifi/interfaces` | GET | List network interfaces |

## Security Notes

- NetworkMonitor requires **Administrator/Root** privileges
- All API endpoints validate IP addresses to prevent injection attacks
- The backend uses secure subprocess calls (no shell=True with user input)
- CORS is configured to allow Vercel deployments

## License

MIT License - See LICENSE file for details
