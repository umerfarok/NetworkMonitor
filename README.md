# NetworkMonitor

A powerful network monitoring and analysis tool.
https://umerfarok.github.io/netmoniter/

## Prerequisites

Before installing NetworkMonitor, ensure you have the following prerequisites installed:

### System Requirements
1. Windows 10 or later (64-bit)
2. Python 3.9 or later
   - Download from: https://python.org
   - During installation, check "Add Python to PATH"
3. Npcap (Windows only)
   - Download from: https://npcap.com
   - Install with "WinPcap API-compatible Mode" option

### Administrator Privileges
NetworkMonitor requires administrator privileges to capture network traffic.

## Features

- Modern dark-themed user interface
- System tray support for background operation
- Real-time network monitoring and analysis
- Interactive status dashboard
- One-click web interface access
- Professional status indicators and notifications
- Background operation support

## Installation

1. Download the latest NetworkMonitor installer from the releases page.

2. Run the installer with administrator privileges.

3. After installation, open a command prompt with administrator privileges and install the required Python packages:
   ```
   pip install -r "C:\Program Files\NetworkMonitor\requirements.txt"
   ```

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

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/networkmonitor/networkmonitor.git
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

4. Build the application:
   ```
   python build.py
   ```

## License

[Add license information here]
