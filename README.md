# NetworkMonitor

A powerful network monitoring and analysis tool.

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
   - The application will open in your default web browser

2. If you see any dependency warnings:
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
