import os
import sys
import platform
import subprocess
import ctypes
import shutil
from pathlib import Path
import logging
import urllib.request
import tempfile
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('install.log'),
        logging.StreamHandler()
    ]
)

def is_admin():
    """Check if the script has admin privileges"""
    try:
        return os.geteuid() == 0
    except AttributeError:  # Windows
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

def run_as_admin():
    """Re-run the script with admin privileges"""
    if platform.system() != 'Windows':
        print("Please run this script with sudo")
        sys.exit(1)
        
    script = os.path.abspath(sys.argv[0]) 
    params = ' '.join([script] + sys.argv[1:])
    
    try:
        print("Requesting administrator privileges...")
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas",
            sys.executable,
            params,
            None,
            1
        )
        if ret > 32:  # Success
            sys.exit(0)  # Exit the current instance
        else:
            print("Failed to elevate privileges")
            return False
    except Exception as e:
        print(f"Error requesting admin rights: {e}")
        return False

def run_command(command, check=True, shell=True, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        print(f"Running: {command}")
        kwargs = {
            'shell': shell,
            'check': check,
            'text': True,
        }
        if capture_output:
            kwargs['capture_output'] = True
        
        # Add CREATE_NO_WINDOW flag for Windows
        if platform.system() == 'Windows':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        
        result = subprocess.run(command, **kwargs)
        if capture_output and result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {str(e)}")
        if capture_output:
            if e.stdout:
                print("Output:", e.stdout)
            if e.stderr:
                print("Error output:", e.stderr)
        return False

def download_file(url, filename):
    """Download a file with progress indicator"""
    try:
        print(f"Downloading {filename}...")
        # Make sure any existing file is removed first
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass
                
        urllib.request.urlretrieve(
            url, 
            filename,
            reporthook=lambda count, block_size, total_size: print(
                f"Progress: {count * block_size * 100 / total_size:.1f}%", 
                end='\r'
            )
        )
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def install_npcap():
    """Install Npcap with user interaction"""
    try:
        # Check if Npcap is already installed
        if os.path.exists("C:\\Windows\\System32\\Npcap"):
            print("Npcap is already installed.")
            return True
            
        print("\nNpcap installation:")
        npcap_url = "https://nmap.org/npcap/dist/npcap-1.75.exe"
        npcap_installer = "npcap-installer.exe"
        
        download_file(npcap_url, npcap_installer)
        print("1. The Npcap installer will open")
        print("2. Follow the installation wizard")
        print("3. Use default settings when asked")
        
        # Run installer
        if platform.system() == "Windows":
            os.startfile(npcap_installer)
            input("\nPress Enter after completing Npcap installation...")
        else:
            print("Npcap is only required on Windows")
            
        # Clean up installer
        if os.path.exists(npcap_installer):
            try:
                os.remove(npcap_installer)
            except:
                pass
            
        # Verify installation
        if os.path.exists("C:\\Windows\\System32\\Npcap"):
            print("Npcap installation verified successfully.")
            return True
        else:
            print("Npcap installation could not be verified.")
            return False
                
    except Exception as e:
        print(f"Error during Npcap installation: {e}")
        return False

def fix_pip_permissions():
    """Fix pip permissions issues on Windows"""
    if platform.system() == "Windows":
        try:
            import site
            site_packages = site.getsitepackages()[0]
            os.chmod(site_packages, 0o777)
            return True
        except Exception as e:
            print(f"Warning: Could not fix pip permissions: {e}")
            return False
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    print("Setting up virtual environment...")
    venv_path = Path("venv")
    
    # Clean up existing venv if present
    if venv_path.exists():
        try:
            shutil.rmtree(venv_path)
        except PermissionError:
            print("Unable to remove existing virtual environment. Please close any applications using it.")
            return False
    
    try:
        # Create virtual environment
        run_command(f'"{sys.executable}" -m venv venv')
        
        # Get the correct pip path
        if platform.system() == "Windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"

        if not pip_path.exists():
            print("Virtual environment creation failed")
            return False

        print("Installing Python dependencies...")
        
        # Upgrade pip first
        run_command(f'"{python_path}" -m pip install --upgrade pip')
        
        # Fix permissions if needed
        fix_pip_permissions()
        
        # Install wheel and setuptools first
        run_command(f'"{python_path}" -m pip install wheel setuptools charset-normalizer')
        
        # Install the package in editable mode
        run_command(f'"{python_path}" -m pip install -e .')
        
        return True
        
    except Exception as e:
        print(f"Error setting up virtual environment: {e}")
        return False

def create_shortcut():
    """Create desktop shortcut"""
    try:
        desktop = Path.home() / "Desktop"
        
        # Create directory for our app if it doesn't exist
        app_dir = Path.home() / ".networkmonitor"
        app_dir.mkdir(exist_ok=True)
        
        # Create config file if it doesn't exist
        config_file = app_dir / "config.json"
        if not config_file.exists():
            config = {
                "interface": None,
                "port": 5000,
                "dark_mode": False,
                "scan_interval": 5
            }
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        
        # Create shortcut based on platform
        if platform.system() == "Windows":
            shortcut_path = desktop / "Network Monitor.lnk"
            
            # Create .bat file in the app directory
            bat_path = app_dir / "launch.bat"
            with open(bat_path, "w") as f:
                f.write('@echo off\n')
                
                # If running from source install
                venv_path = os.path.abspath("venv")
                if os.path.exists(venv_path):
                    activate_path = os.path.join(venv_path, "Scripts", "activate.bat")
                    f.write(f'cd /d "%~dp0"\n')  # Change to script directory
                    f.write(f'call "{activate_path}"\n')
                    f.write('networkmonitor launch\n')
                else:
                    # For packaged install
                    f.write('networkmonitor launch\n')
                    
                f.write('pause\n')
            
            # Create Windows shortcut
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.TargetPath = str(bat_path)
                shortcut.WorkingDirectory = str(app_dir)
                shortcut.IconLocation = f"{os.path.abspath(os.path.dirname(sys.executable))}\\python.exe,0"
                shortcut.save()
            except:
                # Fallback if pywin32 is not installed
                with open(desktop / "Network Monitor.bat", "w") as f:
                    f.write('@echo off\n')
                    f.write(f'start "" "{bat_path}"\n')
        
        elif platform.system() == "Linux":
            shortcut_path = desktop / "networkmonitor.desktop"
            with open(shortcut_path, "w") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Network Monitor\n")
                f.write("Comment=Monitor and control your network\n")
                
                # If running from source install
                venv_path = os.path.abspath("venv")
                if os.path.exists(venv_path):
                    f.write(f"Exec={venv_path}/bin/networkmonitor launch\n")
                else:
                    # For packaged install
                    f.write("Exec=networkmonitor launch\n")
                    
                f.write("Terminal=false\n")
                f.write("Categories=Network;Utility;\n")
            
            # Make executable
            os.chmod(shortcut_path, 0o755)
            
        elif platform.system() == "Darwin":  # macOS
            shortcut_path = desktop / "Network Monitor.command"
            with open(shortcut_path, "w") as f:
                f.write("#!/bin/bash\n")
                
                # If running from source install
                venv_path = os.path.abspath("venv")
                if os.path.exists(venv_path):
                    f.write(f"source {venv_path}/bin/activate\n")
                    f.write("networkmonitor launch\n")
                else:
                    # For packaged install
                    f.write("networkmonitor launch\n")
            
            # Make executable
            os.chmod(shortcut_path, 0o755)
                
        print(f"Created shortcut at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    try:
        if platform.system() == "Linux":
            # Check if we have sudo
            has_sudo = subprocess.call(["which", "sudo"], stdout=subprocess.PIPE) == 0
            
            if has_sudo:
                # Install Linux dependencies
                commands = [
                    "apt-get update",
                    "apt-get install -y libpcap-dev python3-dev",
                    "apt-get install -y net-tools",
                ]
                for cmd in commands:
                    if not run_command(f"sudo {cmd}"):
                        return False
            else:
                print("Warning: 'sudo' not found. System dependencies must be installed manually.")
                print("Please install libpcap-dev, python3-dev, and net-tools.")
                
        # Install Windows specific dependencies
        elif platform.system() == "Windows":
            if not install_npcap():
                print("Failed to install Npcap. Please install it manually.")
                return False
                
        return True
    except Exception as e:
        print(f"Error installing system dependencies: {e}")
        return False

def main():
    print("Starting Network Monitor installation...")
    
    # Check for admin privileges
    if not is_admin():
        print("This installation requires administrative privileges.")
        run_as_admin()
        sys.exit()
    
    try:
        # Install system dependencies
        if not install_system_dependencies():
            print("Failed to install system dependencies")
            return
        
        # Setup virtual environment and install dependencies
        # Skip for packaged version
        if os.path.isfile('setup.py'):
            if not setup_virtual_environment():
                print("Virtual environment setup failed")
                return
        
        # Create shortcut
        if not create_shortcut():
            print("Shortcut creation failed")
        
        print("\nInstallation complete!")
        print("\nYou can start Network Monitor by:")
        print("1. Running 'networkmonitor launch' in terminal")
        print("2. Using the desktop shortcut")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"Installation failed: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()