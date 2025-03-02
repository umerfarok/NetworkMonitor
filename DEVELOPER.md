# Network Monitor - Developer Guide

This document provides detailed technical information for developers who want to contribute to the Network Monitor project or understand how its installation, development, and build processes work.

## Project Structure

```
networkmonitor/
├── assets/                     # Icons and resources for the application
├── networkmonitor/            
│   ├── __init__.py             # Package initialization
│   ├── cli.py                  # Command-line interface
│   ├── launcher.py             # Application launcher (GUI mode)
│   ├── monitor.py              # Core network monitoring functionality
│   ├── server.py               # Flask web server that exposes the API
│   ├── windows.py              # Windows-specific functionality
│   ├── scripts/                # CLI entrypoint scripts
│   └── web/                    # Next.js web frontend
│       ├── components/         # React components
│       ├── pages/              # Next.js pages and API routes
│       ├── public/             # Static assets
│       └── styles/             # CSS files
├── build.py                    # Build script for creating distributables
├── install.py                  # Installation script
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # User documentation
├── requirements-build.txt      # Build dependencies
└── setup.py                    # Package setup script
```

## Development Environment Setup

### Prerequisites

1. **Python 3.8+** - Required for core functionality
2. **Node.js 14+** - Required for frontend development
3. **Platform-specific tools**:
   - **Windows**: Administrator access, Npcap
   - **Linux**: sudo access, libpcap-dev, net-tools
   - **macOS**: Developer tools, libpcap

### Setting up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/umerfarok/networkmonitor.git
   cd networkmonitor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

4. **Install frontend dependencies**:
   ```bash
   cd networkmonitor/web
   npm install
   cd ../..
   ```

### Running the Application in Development Mode

#### Backend Development

Run the backend server with:
```bash
# With default options
networkmonitor start

# With specific options
networkmonitor start --host 0.0.0.0 --port 8000 --no-browser
```

#### Frontend Development

For frontend development, you can run the Next.js development server:
```bash
cd networkmonitor/web
npm run dev
```

Then point your browser to `http://localhost:3000`. The frontend will connect to your backend API running on port 5000.

## Installation Process

The `install.py` script handles the installation process. Here's how it works:

1. **Privilege Check**: Verifies if the script has the necessary permissions and requests them if needed
2. **System Dependencies**: Installs required system-level dependencies (Npcap on Windows, libpcap-dev on Linux)
3. **Python Environment**: Sets up a virtual environment (if running from source)
4. **Application Installation**: Installs the Python package
5. **Shortcut Creation**: Creates desktop shortcuts for easy access

### Installation Flow Diagram

```
Start Installation
    ├─> Check Admin/Root Privileges
    │       ├─> If not elevated, request elevation
    │       └─> Exit if elevation fails
    ├─> Install System Dependencies
    │       ├─> Windows: Install Npcap
    │       └─> Linux: Install libpcap-dev, net-tools
    ├─> Setup Virtual Environment (source install only)
    │       ├─> Create Python virtual environment
    │       ├─> Upgrade pip
    │       └─> Install package in editable mode
    ├─> Create Desktop Shortcut
    │       ├─> Windows: .bat file + shortcut
    │       ├─> Linux: .desktop file
    │       └─> macOS: .command file
    └─> Create Config Directory and Files
```

## Build Process

The `build.py` script handles building distributable packages. Here's how it works:

1. **Environment Cleanup**: Removes previous build artifacts
2. **Frontend Build**: Builds the Next.js frontend into static assets
3. **Binary Creation**: Uses PyInstaller to create standalone executables
4. **Installer Generation**: Creates platform-specific installers

### Build Dependencies

Install build dependencies with:
```bash
pip install -r requirements-build.txt
```

### Building Distributable Packages

```bash
python build.py
```

This will create the following in the `dist` directory:

- **Windows**: `NetworkMonitor_Setup_0.1.0.exe` (NSIS installer)
- **macOS**: `NetworkMonitor_0.1.0.dmg` (Disk image)
- **Linux**: 
  - `NetworkMonitor_0.1.0_amd64.deb` (Debian package)
  - `NetworkMonitor_0.1.0_linux.tar.gz` (Fallback tarball)

### Build Flow Diagram

```
Start Build
    ├─> Clean Previous Builds
    │       └─> Remove build/, dist/, *.egg-info/
    ├─> Build Frontend
    │       ├─> Install npm dependencies
    │       └─> Run Next.js build
    ├─> Build Binary
    │       ├─> PyInstaller configuration
    │       └─> Generate standalone executable
    └─> Create Installer
            ├─> Windows: NSIS installer
            ├─> macOS: DMG file
            └─> Linux: DEB package or tarball
```

## Architecture

The Network Monitor application consists of three main components:

1. **Backend (Python)**
   - `monitor.py`: Core functionality for network scanning and monitoring
   - `server.py`: Flask web server that exposes the network functionality via REST API
   - `cli.py`: Command-line interface
   - `launcher.py`: GUI application launcher

2. **Frontend (Next.js/React)**
   - Web-based user interface that consumes the API
   - Responsive design for desktop and mobile
   - Real-time network visualization

3. **Distribution Layer**
   - `build.py`: Packaging and installer creation
   - `install.py`: Installation and setup
   - Platform-specific integration

### Communication Flow

```
User Interface (Browser)
       ↕ HTTP/JSON
Flask Web Server (port 5000)
       ↕ Python API
Network Controller
       ↕ 
System Network Interfaces
       ↕
Network Devices
```

## Adding New Features

When adding new features:

1. **Backend**: Add functionality to the NetworkController class in `monitor.py`
2. **API**: Add new endpoints in `server.py`
3. **Frontend**: Add components in `web/components/` and update pages in `web/pages/`

## Common Development Tasks

### Adding a New API Endpoint

1. Open `networkmonitor/server.py`
2. Add a new route function:
   ```python
   @app.route('/api/new-endpoint', methods=['GET'])
   def new_endpoint():
       try:
           # Implementation
           return jsonify(response(True, data))
       except Exception as e:
           logging.error(f"Error: {str(e)}")
           return jsonify(response(False, error=str(e))), 500
   ```

### Adding a New CLI Command

1. Open `networkmonitor/cli.py`
2. Add a new command:
   ```python
   @main.command()
   @click.option('--option', help='Description')
   def new_command(option):
       """Command description"""
       click.echo("Implementing new command")
       # Implementation
   ```

### Updating the Frontend

1. Navigate to the frontend directory: `cd networkmonitor/web`
2. Make your changes to components or pages
3. Test with the development server: `npm run dev`
4. Build for production: `npm run build`

## Troubleshooting Development Issues

### Backend Issues

- **Permission errors**: Make sure to run with admin/root privileges
- **Missing dependencies**: Check requirements.txt and run `pip install -e .`
- **Port conflicts**: Change the port with `--port` option or check for running instances

### Frontend Issues

- **API connection errors**: Ensure the backend server is running on the expected port
- **Build errors**: Check Node.js version (14+ required) and npm dependencies

### Build Issues

- **PyInstaller errors**: Check PyInstaller version and Python compatibility
- **Frontend build failures**: Ensure all Node.js dependencies are installed
- **Installer creation failures**: Check for platform-specific tools (NSIS on Windows)

## Release Process

1. Update version in `pyproject.toml`, `setup.py`, and `networkmonitor/__init__.py`
2. Build distributions with `python build.py`
3. Test installations on target platforms
4. Create a GitHub release with the distributable files
5. Update user documentation

## Contributing Guidelines

1. Fork the repository and create a feature branch
2. Make your changes following the coding style
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with a clear description of changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.