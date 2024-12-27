import os
import sys
import platform
import subprocess
from pathlib import Path
import shutil
import time
import ctypes

def is_admin():
    """Check if the script has admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with admin privileges"""
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    
    try:
        print("Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas",
            sys.executable,
            params,
            None,
            1
        )
        return True
    except Exception as e:
        print(f"Error requesting admin rights: {e}")
        return False

def run_command(command, check=True, shell=True):
    """Run a shell command and handle errors"""
    try:
        print(f"Running: {command}")
        result = subprocess.run(command, shell=shell, check=check, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {str(e)}")
        return False

def install_npcap():
    """Install Npcap with user interaction"""
    print("Downloading Npcap...")
    try:
        run_command("curl -L -o npcap-installer.exe https://nmap.org/npcap/dist/npcap-1.75.exe")
        
        print("\nInstalling Npcap:")
        print("1. The Npcap installer will open")
        print("2. Follow the installation wizard")
        print("3. Use default settings when asked")
        
        os.startfile("npcap-installer.exe")
        input("\nPress Enter after completing Npcap installation...")
        
        if os.path.exists("npcap-installer.exe"):
            try:
                os.remove("npcap-installer.exe")
            except:
                pass
                
    except Exception as e:
        print(f"Error during Npcap installation: {e}")
        return False
    
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    print("Setting up virtual environment...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        try:
            shutil.rmtree(venv_path)
        except PermissionError:
            print("Unable to remove existing virtual environment. Please close any applications using it.")
            return False
    
    try:
        run_command(f'"{sys.executable}" -m venv venv')
        
        # Get the correct pip path
        if platform.system() == "Windows":
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = venv_path / "bin" / "pip"

        if not pip_path.exists():
            print("Virtual environment creation failed")
            return False

        print("Installing Python dependencies...")
        run_command(f'"{pip_path}" install --upgrade pip')
        run_command(f'"{pip_path}" install -e .')
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
            venv_activate = os.path.abspath("venv/Scripts/activate.bat")
            f.write('@echo off\n')
            f.write(f'call "{venv_activate}"\n')
            f.write('start http://localhost:5000\n')
            f.write('netmonitor start\n')
            f.write('pause\n')
            
        print(f"Created shortcut at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

def main():
    print("Starting Network Monitor installation...")
    
    if platform.system() == 'Windows':
        if not is_admin():
            run_as_admin()
            sys.exit()
    
    try:
        if platform.system() == "Windows":
            if not install_npcap():
                print("Npcap installation failed. Please install it manually from https://nmap.org/npcap/")
                return
                
        if not setup_virtual_environment():
            print("Virtual environment setup failed")
            return
            
        if not create_shortcut():
            print("Shortcut creation failed")
            
        print("\nInstallation complete!")
        print("\nYou can start Network Monitor by:")
        print("1. Running 'netmonitor start' in terminal")
        print("2. Using the desktop shortcut (NetworkMonitor.bat)")
        
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"Installation failed: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()