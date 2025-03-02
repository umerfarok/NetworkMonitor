# Network Monitor - Quick Start Guide

A powerful network monitoring and control tool that allows you to scan your network, monitor device bandwidth, and control network access.

## Installation Options

### Option 1: Download Pre-built Installer

1. Download the appropriate installer for your operating system:
   - **Windows**: `NetworkMonitor_Setup_0.1.0.exe`
   - **macOS**: `NetworkMonitor_0.1.0.dmg`
   - **Ubuntu/Debian**: `NetworkMonitor_0.1.0_amd64.deb`
   - **Other Linux**: `NetworkMonitor_0.1.0_linux.tar.gz`

2. Run the installer and follow the on-screen instructions

### Option 2: Install from Source

1. Download and unzip the package
2. Open terminal/command prompt in the extracted folder
3. Run:
```bash
python install.py
```

## Starting the Tool

### Method 1: Desktop Shortcut
- Double-click the NetworkMonitor shortcut created on your desktop

### Method 2: Command Line (after installation)
```bash
networkmonitor launch
```

### Method 3: Command Line (advanced options)
```bash
networkmonitor start [--host HOST] [--port PORT] [--no-browser]
```

## Using the Tool

1. The web interface will automatically open in your browser
2. Select your network interface from the dropdown
3. Click "Scan Network" to see connected devices

### Monitor Network:
- View connected devices 
- See real-time bandwidth usage
- Check device status

### Control Bandwidth:
1. Enter device IP address
2. Set bandwidth limit (in Mbps)
3. Click "Apply Limit" or "Remove Limit"

## Features

- **Network Scanning**: Discover all devices on your local network
- **Device Identification**: View device types, MAC addresses, vendors, and hostnames
- **Bandwidth Monitoring**: Track bandwidth usage for each device
- **Bandwidth Control**: Set speed limits for specific devices
- **Network Cutting**: Temporarily disconnect devices from the network
- **Device Protection**: Protect specific devices from network attacks
- **Device Organization**: Group devices by speed limits

## Building from Source

To build the distributable packages from source:

1. Install build dependencies:
```bash
pip install -r requirements-build.txt
```

2. Run the build script:
```bash
python build.py
```

3. The installer packages will be available in the `dist` directory

## Requirements
- Python 3.8 or higher
- Administrator/root privileges

## Troubleshooting

If you get permissions error:
- **Windows**: Run as Administrator
- **Linux/Mac**: Use `sudo networkmonitor launch`

If the web interface doesn't open:
- Manually navigate to `http://localhost:5000` in your browser

## Security Considerations

This tool requires elevated privileges to perform network operations like ARP scanning and packet manipulation. Only use it on networks you own or have permission to monitor.

## Support
If you need help, create an issue in the GitHub repository.
