# NetworkMonitor Developer Guide

## Development Environment Setup

1. Install system dependencies:
   - Python 3.9 or later from python.org
   - Npcap from npcap.com (Windows only)
   - Node.js and npm for web interface development

2. Clone the repository and set up a virtual environment:
   ```bash
   git clone https://github.com/networkmonitor/networkmonitor.git
   cd networkmonitor
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

4. Install web interface dependencies:
   ```bash
   cd networkmonitor/web
   npm install
   ```

## Prerequisites

### System Requirements
- Windows 10 or later (64-bit)
- Python 3.9 or later
- [Npcap](https://npcap.com/) for packet capture (Windows)
  - Make sure to select "Install Npcap in WinPcap API-compatible Mode" during installation

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
   - Run the installer and select **Complete** installation
   - **IMPORTANT:** Make sure to check "Add to PATH" option during installation
   - After installation, verify that the GTK3 bin directory (e.g., `C:\Program Files\GTK3-Runtime Win64\bin`) is in your PATH
   - **Restart your terminal/IDE after installation**
   - To verify installation: Open a new command prompt and run `gdk-pixbuf-query-loaders --version`
   - If you continue to have issues with Cairo:
     1. Download the latest GTK3 bundle from MSYS2: https://www.msys2.org/
     2. Install MSYS2
     3. Open MSYS2 terminal and run: `pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-cairo`
     4. Add the MSYS2 bin directory to your PATH (e.g., `C:\msys64\mingw64\bin`)

#### 3. Visual C++ Build Tools
   - Download Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run the installer and select:
     - C++ build tools
     - Windows 10 SDK
     - Python development support (optional)

### For Linux Users
- Install system packages:
  ```bash
  sudo apt install net-tools iptables tcpdump
  ```

### Ubuntu/Linux Requirements

#### 1. System Dependencies
```bash
# Install basic build dependencies
sudo apt update
sudo apt install -y build-essential python3-dev python3-pip

# Install Cairo and GTK3 for icon conversion
sudo apt install -y libcairo2-dev libgirepository1.0-dev pkg-config

# Install networking tools
sudo apt install -y net-tools iptables tcpdump

# Install NSIS (for creating installers on Linux)
sudo apt install -y nsis
```

#### 2. Python Libraries
```bash
pip3 install cairosvg pillow pyinstaller
```

### For macOS Users
- Install Homebrew packages:
  ```bash
  brew install libpcap tcpdump
  ```

### macOS Requirements

#### 1. System Dependencies
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cairo pkg-config
brew install gtk+3
brew install python3

# Optional: Install NSIS (for cross-building Windows installers)
brew install makensis
```

#### 2. Python Libraries
```bash
pip3 install cairosvg pillow pyinstaller
```

### Python Dependencies

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

2. Install runtime dependencies:
```bash
pip install -r requirements.txt
```

3. Install build dependencies (only needed for packaging):
```bash
pip install -r requirements-build.txt
```

## Setup Development Environment

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

2. Install runtime dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install build dependencies (only needed for packaging):
   ```bash
   pip install -r requirements-build.txt
   ```

## Running for Development

Run the application in debug mode:
```bash
python start_networkmonitor.py
```

Or use the batch file on Windows (includes additional debug output):
```bash
run_networkmonitor.bat
```

## Building from Source

1. Clone the repository:
```bash
git clone https://github.com/umerfarok/networkmonitor.git
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
- Windows: `NetworkMonitor.exe` and `NetworkMonitor_Setup_0.1.0.exe`
- Linux: `NetworkMonitor` executable
- macOS: `NetworkMonitor` executable or `.app` bundle

## Platform-Specific Build Notes

### Linux (Ubuntu/Debian)
Building on Linux creates a standalone executable that can be run on similar Linux distributions:
```bash
# Make the executable executable
chmod +x dist/NetworkMonitor
# Run the application
sudo ./dist/NetworkMonitor
```

### macOS
Building on macOS creates a standalone executable:
```bash
# Make the executable executable
chmod +x dist/NetworkMonitor
# Run the application
sudo ./dist/NetworkMonitor
```

### Windows
The Windows executable requires Administrator privileges to run properly:
- Right-click on the executable
- Select "Run as Administrator"

## Common Build Issues

### Icon Conversion Issues
If you see "cairo library not found" errors:
1. Make sure GTK3 is properly installed as described in the prerequisites
2. Verify that GTK3 bin directory is in your PATH environment variable
3. Install Python packages: `pip install cairosvg Pillow`
4. Try installing Cairo directly: `pip install pycairo`
5. For Windows, consider using MSYS2 to install Cairo:
   - Install MSYS2: https://www.msys2.org/
   - Run: `pacman -S mingw-w64-x86_64-cairo`
6. Restart your terminal/IDE completely (not just the command prompt)
7. Run build again

### NSIS Issues
If installer creation fails:
1. Ensure NSIS is installed and in PATH
2. Install EnvVarUpdate plugin as described in prerequisites (Windows only)
3. Check if the NSIS Include and Plugins directories contain the required files
4. Run `makensis -VERSION` in terminal to verify NSIS is accessible

### Missing DLL Errors
If you see missing DLL errors when running the built executable:
1. Windows: Install Visual C++ Redistributable 2015-2022
2. Linux: Install required system libraries using apt
3. macOS: Install required libraries using brew
4. Ensure all dependencies are installed: `pip install -r requirements.txt`

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

### Dependency Management

1. Keep dependencies organized:
   - requirements.txt: Runtime dependencies
   - requirements-build.txt: Build-time dependencies
   - package.json: Web interface dependencies

2. Version constraints:
   - Use >= for minimum version requirements
   - Test thoroughly with latest versions
   - Document any version-specific issues

3. System dependencies:
   - Document clearly in README.md
   - Provide detailed installation instructions
   - Include version requirements

### Testing

1. Test installation scenarios:
   - Clean Windows installation
   - Various Python versions
   - Different Npcap versions
   - With/without admin rights

2. Test dependency checks:
   - Missing Python
   - Missing Npcap
   - Missing packages
   - Version conflicts

### Error Handling

Implement graceful fallbacks and clear error messages for:
1. Missing system dependencies
2. Package installation failures
3. Permission issues
4. Version compatibility problems

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

## Release Process

1. Update version numbers:
   - pyproject.toml
   - installer.nsi
   - package.json

2. Build release artifacts:
   ```bash
   python build.py
   ```

3. Test installation package:
   - Fresh Windows installation
   - Different Python versions
   - Verify dependency handling
   - Check error messages

4. Create release checklist:
   - Version numbers updated
   - Changelog updated
   - Dependencies documented
   - Installation tested
   - Release notes complete

## Troubleshooting

### Build Environment Issues
- Run `python -m pip check` to verify dependencies
- Use `python -m pip install --upgrade pip setuptools wheel` to update basic tools
- Clear pip cache if needed: `python -m pip cache purge`

### Installation Issues
- Run the installer as Administrator (Windows)
- Run with sudo on Linux/macOS
- Check system logs for installation errors

### Runtime Issues
- Check logs in `networkmonitor.log`
- Run with `--debug` flag for verbose output
- Verify all dependencies are installed

## Project Structure

```
networkmonitor/
├── __init__.py         # Package initialization
├── cli.py             # Command-line interface
├── dependency_check.py # Dependency verification
├── launcher.py        # Application launcher
├── monitor.py         # Core monitoring functionality
├── npcap_helper.py    # Windows Npcap support
├── server.py          # Web server component
├── splash.py          # Splash screen UI
└── web/              # Web interface files
```

## UI Components

### Status Dashboard

The status dashboard is built using Tkinter with a modern, dark theme design. The implementation can be found in `run_app.py` and `launcher.py`. Here are the key technical details:

#### Color Scheme
The UI uses a consistent color scheme defined as:
- Background: #1e1e1e (Dark background)
- Foreground: #e0e0e0 (Light text)
- Accent: #007acc (Blue accent)
- Success: #2ecc71 (Green)
- Error: #e74c3c (Red)
- Warning: #f1c40f (Yellow)
- Header Background: #252526
- Button Background: #333333
- Button Hover: #404040

#### UI Components Structure

1. Header Section
   - Professional gradient background effect
   - Centered title with Segoe UI bold font
   - Application icon integration
   - Fixed height with proper padding

2. Status Section
   - Dynamic status indicator with smooth color transitions
   - Clear status message display
   - Color-coded states (running/error/warning)
   - Background highlighting for better visibility

3. URL Display
   - Interactive URL label with hover effects
   - One-click copy functionality
   - Visual feedback on interactions
   - Direct browser launch capability

4. Control Panel
   - Modern flat-design buttons
   - Consistent button sizing and spacing
   - Hover effects for better UX
   - Background operation support
   - Safe exit handling

#### System Tray Integration

The application now supports system tray operation with:
- Custom tray icon display
- Right-click context menu
- Status preservation while minimized
- Quick restore functionality
- Clean application exit

### Implementation Guidelines

1. Window Configuration
   - Minimum size: 500x300 pixels
   - Responsive layout adaptation
   - DPI-aware scaling
   - Multi-monitor support
   - Proper window manager hints

2. Font Usage
   - Primary UI: Segoe UI (Windows system font)
   - Fallback fonts for cross-platform compatibility
   - Size scaling based on screen resolution
   - Consistent font weights

3. Layout Standards
   - Standard padding: 20px horizontal, 15px vertical
   - Consistent component spacing
   - Proper alignment and anchoring
   - Responsive grid system

4. Event Handling
   - Non-blocking UI operations
   - Threaded server management
   - Periodic status updates
   - Clean exit procedures
   - Error handling and recovery

## Development Guidelines

### Adding New UI Elements

1. Follow the color scheme:
```python
element = tk.Widget(
    parent,
    bg=COLORS['bg'],
    fg=COLORS['fg'],
    activebackground=COLORS['button_hover']
)
```

2. Use the button creation helper:
```python
new_button = create_button(
    text="Action",
    command=handler_function,
    width=15
)
```

3. Status Updates:
```python
def update_status(state, message):
    # Update indicator color
    color = COLORS[state] if state in COLORS else COLORS['warning']
    status_indicator.update_color(color)
    # Update message
    status_var.set(message)
    # Trigger UI update
    root.update_idletasks()
```

### Testing Requirements

1. Visual Testing
   - Window sizing and minimum constraints
   - HiDPI display compatibility
   - Color contrast verification
   - Animation smoothness
   - Font rendering quality

2. Functionality Testing
   - Button interactions
   - Status updates
   - URL handling
   - Copy functionality
   - System tray operations
   - Exit handling

3. Performance Testing
   - UI responsiveness
   - Memory usage
   - CPU utilization
   - Thread management
   - Resource cleanup

## Build Requirements

Ensure all UI-related dependencies are installed:

```bash
pip install -r requirements.txt
```

Critical packages:
- tkinter (built into Python)
- pystray>=0.19.0 (system tray support)
- Pillow>=10.0.0 (image processing)

## Contribution Guidelines

1. UI Changes
   - Maintain dark theme consistency
   - Follow existing color scheme
   - Use proper padding and spacing
   - Ensure responsive behavior
   - Add appropriate documentation

2. Code Style
   - Follow PEP 8 guidelines
   - Document all UI components
   - Use type hints where applicable
   - Include error handling
   - Write modular, reusable code

3. Pull Requests
   - Include UI screenshots if applicable
   - Document visual changes
   - Test across different resolutions
   - Verify system tray functionality
   - Check resource usage

# Developer Documentation

# Developer Guide

## Setup Development Environment

1. Prerequisites:
   - Python 3.9 or later
   - Npcap (Windows only)
   - Git

2. Clone and Setup:
   ```bash
   git clone https://github.com/umerfarok/netmoniter.git
   cd netmoniter
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

## Building

```bash
python build.py
```

## Testing

```bash
python -m pytest tests/
```

## Contributing

See CONTRIBUTING.md for guidelines.