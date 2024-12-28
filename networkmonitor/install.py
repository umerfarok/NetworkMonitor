import os
import sys
import platform
import subprocess
import ctypes
import shutil
from pathlib import Path
import logging

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('install.log'),
            logging.StreamHandler()
        ]
    )

def is_admin():
    """Check if script has admin privileges"""
    try:
        return os.geteuid() == 0  # Unix-like
    except AttributeError:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()  # Windows
        except:
            return False

def run_as_admin():
    """Re-run the script with admin privileges"""
    if platform.system() == "Windows":
        if not is_admin():
            logging.info("Requesting administrator privileges...")
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    " ".join([sys.argv[0]] + sys.argv[1:]),
                    None,
                    1
                )
                return True
            except Exception as e:
                logging.error(f"Failed to get admin rights: {e}")
                return False
    return True

def run_command(command, check=True, shell=True, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        logging.info(f"Running command: {command}")
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            text=True,
            capture_output=capture_output
        )
        if result.stdout:
            logging.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running command: {command}")
        logging.error(f"Error details: {str(e)}")
        if e.stderr:
            logging.error(f"Error output: {e.stderr}")
        return False

def install_npcap():
    """Install Npcap with user interaction"""
    logging.info("Starting Npcap installation...")
    try:
        # Download Npcap installer
        npcap_url = "https://nmap.org/npcap/dist/npcap-1.75.exe"
        logging.info(f"Downloading Npcap from {npcap_url}")
        
        # Use curl if available, otherwise use python's urllib
        if shutil.which('curl'):
            success = run_command(f'curl -L -o npcap-installer.exe "{npcap_url}"')
        else:
            import urllib.request
            urllib.request.urlretrieve(npcap_url, "npcap-installer.exe")
            success = True

        if not success:
            raise Exception("Failed to download Npcap installer")

        # Run installer
        logging.info("\nInstalling Npcap:")
        logging.info("1. The Npcap installer will open")
        logging.info("2. Follow the installation wizard")
        logging.info("3. Use default settings when asked")
        
        if platform.system() == "Windows":
            os.startfile("npcap-installer.exe")
            input("\nPress Enter after completing Npcap installation...")
        else:
            logging.warning("Npcap is only required on Windows")
            return True

        # Clean up installer
        if os.path.exists("npcap-installer.exe"):
            try:
                os.remove("npcap-installer.exe")
            except Exception as e:
                logging.warning(f"Could not remove installer: {e}")

        return True

    except Exception as e:
        logging.error(f"Error during Npcap installation: {e}")
        return False

def setup_virtual_environment():
    """Create and configure virtual environment"""
    logging.info("Setting up virtual environment...")
    venv_path = Path("venv")

    try:
        # Remove existing venv if present
        if venv_path.exists():
            shutil.rmtree(venv_path)

        # Create new venv
        run_command(f'"{sys.executable}" -m venv venv')

        # Get pip path
        if platform.system() == "Windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"

        if not pip_path.exists():
            raise Exception("Virtual environment creation failed")

        # Upgrade pip
        run_command(f'"{pip_path}" install --upgrade pip')

        # Install package
        run_command(f'"{pip_path}" install -e .')

        return True

    except Exception as e:
        logging.error(f"Error setting up virtual environment: {e}")
        return False

def create_shortcut():
    """Create desktop shortcut"""
    try:
        desktop = Path.home() / "Desktop"
        
        if platform.system() == "Windows":
            shortcut_path = desktop / "NetworkMonitor.bat"
            with open(shortcut_path, "w") as f:
                f.write('@echo off\n')
                f.write('start http://localhost:5000\n')
                f.write('networkmonitor start\n')
                f.write('pause\n')
        else:
            shortcut_path = desktop / "networkmonitor.sh"
            with open(shortcut_path, "w") as f:
                f.write('#!/bin/bash\n')
                f.write('xdg-open http://localhost:5000\n')
                f.write('networkmonitor start\n')
            os.chmod(shortcut_path, 0o755)

        logging.info(f"Created shortcut at: {shortcut_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create shortcut: {e}")
        return False

def check_prerequisites():
    """Check and verify prerequisites"""
    logging.info("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        logging.error("Python 3.8 or higher is required")
        return False
    
    # Check pip installation
    try:
        import pip
    except ImportError:
        logging.error("pip is not installed")
        return False

    return True

def create_config_directory():
    """Create configuration directory"""
    try:
        config_dir = Path.home() / ".networkmonitor"
        config_dir.mkdir(exist_ok=True)
        
        # Create basic config file if it doesn't exist
        config_file = config_dir / "config.json"
        if not config_file.exists():
            import json
            default_config = {
                "interface": None,
                "port": 5000,
                "scan_interval": 5,
                "debug": False
            }
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=4)
        
        return True
    except Exception as e:
        logging.error(f"Error creating config directory: {e}")
        return False

def main():
    """Main installation function"""
    setup_logging()
    logging.info("Starting Network Monitor installation...")

    try:
        # Check if running with admin rights
        if platform.system() == "Windows" and not is_admin():
            run_as_admin()
            return

        # Check prerequisites
        if not check_prerequisites():
            logging.error("Prerequisites check failed")
            return

        # Create config directory
        if not create_config_directory():
            logging.error("Failed to create configuration directory")
            return

        # Install Npcap on Windows
        if platform.system() == "Windows":
            if not install_npcap():
                logging.error("Npcap installation failed")
                logging.info("Please install Npcap manually from https://nmap.org/npcap/")
                return

        # Setup virtual environment
        if not setup_virtual_environment():
            logging.error("Virtual environment setup failed")
            return

        # Create shortcut
        if not create_shortcut():
            logging.warning("Shortcut creation failed")

        logging.info("\nInstallation complete!")
        logging.info("\nYou can start Network Monitor by:")
        logging.info("1. Running 'networkmonitor start' in terminal")
        logging.info("2. Using the desktop shortcut")

        input("\nPress Enter to exit...")

    except Exception as e:
        logging.error(f"Installation failed: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()