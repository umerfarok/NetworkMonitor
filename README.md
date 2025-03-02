# Network Monitor

A powerful network monitoring and control tool with ARP protection capabilities.

## Features
- Discover all devices on your network
- Monitor network traffic and bandwidth usage
- Block unwanted devices
- Protect devices from ARP spoofing attacks
- Control device bandwidth
- RESTful API for integration

## Quick Install (Windows)
1. Download the latest installer from Releases
2. Run the installer as Administrator
3. Launch Network Monitor from the Start Menu or Desktop shortcut

## Manual Installation
If you prefer to install from source or need the latest development version:

### Prerequisites
- Python 3.8 or higher
- Administrator privileges (required for network monitoring)
- Windows: Visual C++ Redistributable
- See [DEVELOPER.md](DEVELOPER.md) for complete build requirements

### Install from Source
```bash
# Clone repository
git clone https://github.com/yourorg/networkmonitor.git
cd networkmonitor

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m networkmonitor
```

For detailed build instructions and development setup, see [DEVELOPER.md](DEVELOPER.md).

## Usage
1. Start Network Monitor (requires Administrator privileges)
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

## Security Notes
- Run as Administrator/root for full functionality
- Use device protection features responsibly
- Keep the software updated for security fixes

## License
MIT License - See LICENSE file for details
