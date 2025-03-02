# Developer Guide

This guide explains how to set up your development environment and build NetworkMonitor from source.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Windows-specific Requirements

#### 1. NSIS (Nullsoft Scriptable Install System)
   - Download from: https://nsis.sourceforge.io/Download
   - Run the installer and select full installation
   - Add NSIS installation directory to PATH (usually `C:\Program Files (x86)\NSIS`)
   - Install required NSIS plugins:
     1. Download EnvVarUpdate plugin: https://nsis.sourceforge.io/mediawiki/images/7/7f/EnvVarUpdate.7z
     2. Extract the files to your NSIS installation:
        - Copy `Include\EnvVarUpdate.nsh` to `C:\Program Files (x86)\NSIS\Include`
        - Copy `Plugin\x86-ansi\EnvVarUpdate.dll` to `C:\Program Files (x86)\NSIS\Plugins\x86-ansi`
        - Copy `Plugin\x86-unicode\EnvVarUpdate.dll` to `C:\Program Files (x86)\NSIS\Plugins\x86-unicode`

#### 2. GTK3 Runtime (for icon conversion)
   - Download GTK3 runtime installer: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Run the installer and ensure "Add to PATH" is selected
   - **Important**: Restart your terminal/IDE after installation

#### 3. Visual C++ Build Tools
   - Download Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run the installer and select:
     - C++ build tools
     - Windows 10 SDK
     - Python development support (optional)

### Python Dependencies

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

2. Install build dependencies:
```bash
pip install -r requirements-build.txt
```

3. Install runtime dependencies:
```bash
pip install -r requirements.txt
```

## Building from Source

1. Clone the repository:
```bash
git clone https://github.com/yourorg/networkmonitor.git
cd networkmonitor
```

2. Build the package:
```bash
python build.py
```

The build process will:
1. Clean previous builds
2. Convert SVG icon to ICO format (if GTK3 runtime is installed)
3. Create a standalone executable
4. Create an installer (on Windows, if NSIS is installed)

Build outputs will be available in the `dist` directory:
- `NetworkMonitor.exe`: Standalone executable
- `NetworkMonitor_Setup_0.1.0.exe`: Windows installer (if NSIS was available)

## Common Build Issues

### Icon Conversion Issues
If you see "cairo library not found" errors:
1. Install GTK3 runtime as described in prerequisites
2. Add GTK3 bin directory to PATH
3. Install Python packages: `pip install cairosvg Pillow`
4. Restart your terminal/IDE
5. Run build again

### NSIS Issues
If installer creation fails:
1. Ensure NSIS is installed and in PATH
2. Install EnvVarUpdate plugin as described in prerequisites
3. Check if the NSIS Include and Plugins directories contain the required files
4. Run `makensis /VERSION` in terminal to verify NSIS is accessible

### Missing DLL Errors
If you see missing DLL errors when running the built executable:
1. Install Visual C++ Redistributable 2015-2022
2. Install GTK3 runtime if using icon conversion
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Document public functions and classes

### Testing
```bash
python -m pytest tests/
```

### Adding Dependencies
1. Add runtime dependencies to `requirements.txt`
2. Add build dependencies to `requirements-build.txt`
3. Update `setup.py` for runtime dependencies

## Releasing

1. Update version in:
   - `setup.py`
   - `build.py`
   - `networkmonitor/__init__.py`

2. Create a new build:
```bash
python build.py
```

3. Test the installer from `dist` directory

## Troubleshooting

### Build Environment Issues
- Run `python -m pip check` to verify dependencies
- Use `python -m pip install --upgrade pip setuptools wheel` to update basic tools
- Clear pip cache if needed: `python -m pip cache purge`

### Installation Issues
- Run the installer as Administrator
- Check Windows Event Viewer for installation errors
- Look for error logs in `%TEMP%` directory

### Runtime Issues
- Check logs in `networkmonitor.log`
- Run with `--debug` flag for verbose output
- Verify all dependencies are installed