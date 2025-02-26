import os
import sys
import platform
import subprocess
from pathlib import Path
import shutil
import time
import ctypes
import urllib.request
import tempfile

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
        print("1. Please download Npcap from: https://nmap.org/npcap/")
        print("2. Run the installer and follow the installation wizard")
        print("3. Use default settings when asked")
        
        input("\nPress Enter after completing Npcap installation...")
        
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
        shortcut_path = desktop / "NetworkMonitor.bat"
        
        with open(shortcut_path, "w") as f:
            venv_path = os.path.abspath("venv")
            if platform.system() == "Windows":
                activate_path = os.path.join(venv_path, "Scripts", "activate.bat")
                f.write('@echo off\n')
                f.write(f'cd /d "%~dp0"\n')  # Change to script directory
                f.write(f'call "{activate_path}"\n')
                f.write('start http://localhost:5000\n')
                f.write('networkmonitor start\n')
                f.write('pause\n')
            else:
                activate_path = os.path.join(venv_path, "bin", "activate")
                f.write('#!/bin/bash\n')
                f.write(f'source "{activate_path}"\n')
                f.write('xdg-open http://localhost:5000\n')
                f.write('networkmonitor start\n')
                os.chmod(shortcut_path, 0o755)  # Make executable on Unix
                
        print(f"Created shortcut at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

def install_system_dependencies():
    """Install system-level dependencies"""
    try:
        if platform.system() == "Linux":
            # Install Linux dependencies
            commands = [
                "apt-get update",
                "apt-get install -y libpcap-dev python3-dev",
                "apt-get install -y net-tools",
            ]
            for cmd in commands:
                if not run_command(f"sudo {cmd}"):
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
        
        # Install Npcap on Windows
        if platform.system() == "Windows":
            if not install_npcap():
                print("Npcap installation failed. Please install it manually from https://nmap.org/npcap/")
                return
        
        # Setup virtual environment and install dependencies
        if not setup_virtual_environment():
            print("Virtual environment setup failed")
            return
        
        # Create shortcut
        if not create_shortcut():
            print("Shortcut creation failed")
        
        print("\nInstallation complete!")
        print("\nYou can start Network Monitor by:")
        print("1. Running 'networkmonitor start' in terminal")
        print("2. Using the desktop shortcut")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"Installation failed: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()