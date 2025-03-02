# Network Monitor

A powerful network monitoring and control tool with ARP protection capabilities.

## Features
- Discover all devices on your network
- Monitor network traffic and bandwidth usage
- Block unwanted devices
- Protect devices from ARP spoofing attacks
- Control device bandwidth
- RESTful API for integration

## Quick Install 

### Windows
1. Download the latest installer from Releases
2. Run the installer as Administrator
3. Launch Network Monitor from the Start Menu or Desktop shortcut

### Ubuntu/Linux
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-dev libcairo2-dev net-tools iptables

# Install Network Monitor
pip3 install networkmonitor

# Run with admin privileges
sudo networkmonitor
```

### macOS
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cairo python3

# Install Network Monitor
pip3 install networkmonitor

# Run with admin privileges
sudo networkmonitor
```

## Manual Installation
If you prefer to install from source or need the latest development version:

### Prerequisites
- Python 3.8 or higher
- Administrator privileges (required for network monitoring)
- Platform-specific dependencies:
  - Windows: Visual C++ Redistributable
  - Linux: net-tools, iptables
  - macOS: cairo library
- See [DEVELOPER.md](DEVELOPER.md) for complete build requirements

### Install from Source
```bash
# Clone repository
git clone https://github.com/yourorg/networkmonitor.git
cd networkmonitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application (with admin privileges)
# Windows: Run as Administrator
python -m networkmonitor

# Linux/Mac:
sudo python -m networkmonitor
```

For detailed build instructions and development setup, see [DEVELOPER.md](DEVELOPER.md).

## Usage
1. Start Network Monitor (requires Administrator/root privileges)
2. Access web interface at http://localhost:5000
3. View connected devices and monitor network activity
4. Use protection features as needed

### Using the API
Network Monitor provides a RESTful API for automation:

```bash
# Get network status
curl http://localhost:5000/api/status

# List connected devices
curl http://localhost:5000/api/devices

# Protect a device
curl -X POST http://localhost:5000/api/device/protect -d '{"ip":"192.168.1.100"}'
```

Full API documentation available at http://localhost:5000/api/docs when running.

## Platform Support

### Windows
- Windows 10 or higher recommended
- Requires Administrator privileges
- Uses Npcap for packet capture

### Linux
- Ubuntu 20.04 or higher recommended
- Debian, Fedora, and other major distributions supported
- Requires root privileges

### macOS
- macOS 11 (Big Sur) or higher recommended
- Requires root privileges

## Security Notes
- Run as Administrator/root for full functionality
- Use device protection features responsibly
- Keep the software updated for security fixes

## License
MIT License - See LICENSE file for details
