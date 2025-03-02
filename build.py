import os
import platform
import shutil
import subprocess
from pathlib import Path
import sys

# Configuration
APP_NAME = "NetworkMonitor"
APP_VERSION = "0.1.0"
ENTRY_POINT = "networkmonitor/cli.py"
ICON_PATH = "assets/icon.svg"  # SVG icon file
OUTPUT_DIR = "dist"

def clean_previous_builds():
    """Remove previous build artifacts"""
    print("Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist', f'{APP_NAME}.egg-info']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Removed {dir_name}/")
            except Exception as e:
                print(f"Error removing {dir_name}: {e}")

def convert_icon():
    """Convert SVG icon to platform-specific format"""
    if not os.path.exists(ICON_PATH):
        print(f"Warning: Icon file not found at {ICON_PATH}")
        return None
    
    # For Windows, we need ICO
    if platform.system() == "Windows":
        try:
            # Check if Cairo is installed
            try:
                import cairosvg
                from PIL import Image
            except ImportError:
                print("Warning: Cairo and/or Pillow libraries not found.")
                print("To enable icon conversion, install GTK3 runtime and required Python packages:")
                print("1. Download GTK3 runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
                print("2. Install Python packages: pip install cairosvg Pillow")
                print("Skipping icon conversion - using default icon")
                return None

            print("Converting SVG icon to ICO...")
            ico_path = "assets/icon.ico"
            
            # First convert to PNG
            png_path = "assets/icon.png"
            cairosvg.svg2png(url=ICON_PATH, write_to=png_path, output_width=256, output_height=256)
            
            # Load PNG and convert to ICO
            with Image.open(png_path) as png_image:
                # Create multiple sizes
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                icon_images = []
                
                for size in sizes:
                    resized_img = png_image.resize(size, Image.LANCZOS)
                    icon_images.append(resized_img)
                
                # Save as ICO
                icon_images[0].save(
                    ico_path, 
                    format="ICO", 
                    sizes=[(img.width, img.height) for img in icon_images],
                    append_images=icon_images[1:]
                )
            
            # Clean up temporary PNG
            os.remove(png_path)
            
            print(f"Icon converted and saved to {ico_path}")
            return ico_path
            
        except Exception as e:
            print(f"Error converting icon: {e}")
            print("Icon conversion skipped - using default icon")
            return None
    
    # For other platforms, return the original icon
    return ICON_PATH

def build_binary():
    """Build binary using PyInstaller"""
    print(f"Building {APP_NAME} for {platform.system()}...")
    
    # Convert icon for the platform
    icon_path = convert_icon()
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon if exists
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add platform-specific options
    if platform.system() == "Windows":
        cmd.append("--noconsole")
        cmd.append("--uac-admin")  # Request admin privileges on Windows
    
    # Add required files
    if os.path.exists("networkmonitor/requirements.txt"):
        cmd.extend(["--add-data", "networkmonitor/requirements.txt;networkmonitor"])
    if os.path.exists("assets"):
        cmd.extend(["--add-data", "assets;assets"])
    
    # Add entry point
    cmd.append(ENTRY_POINT)
    
    try:
        # Run PyInstaller
        subprocess.check_call(cmd)
        print("Binary build complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building binary: {e}")
        return False

def _find_nsis():
    """Find NSIS installation directory"""
    possible_paths = [
        r"C:\Program Files (x86)\NSIS",
        r"C:\Program Files\NSIS",
        os.path.expandvars(r"%ProgramFiles(x86)%\NSIS"),
        os.path.expandvars(r"%ProgramFiles%\NSIS"),
    ]
    
    # Check if makensis is in PATH
    try:
        subprocess.run(["makensis", "/VERSION"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Check known installation paths
        for path in possible_paths:
            makensis = os.path.join(path, "makensis.exe")
            if os.path.exists(makensis):
                os.environ["PATH"] = os.environ["PATH"] + ";" + path
                return True
    return False

def create_windows_installer():
    """Create Windows installer using NSIS"""
    print("Creating installer for Windows...")
    try:
        # Check if NSIS is installed
        if not _find_nsis():
            print("NSIS not found in PATH or standard locations.")
            print("Please install NSIS:")
            print("1. Download from https://nsis.sourceforge.io/Download")
            print("2. Run the installer")
            print("3. Add NSIS installation directory to PATH")
            print("4. Restart your terminal/IDE")
            return False

        # Generate NSIS script (without requiring EnvVarUpdate)
        nsis_script = f"""
        !include "MUI2.nsh"
        
        !define APP_NAME "{APP_NAME}"
        !define APP_VERSION "{APP_VERSION}"
        !define EXE_NAME "{APP_NAME}.exe"
        
        Name "${{APP_NAME}} ${{APP_VERSION}}"
        OutFile "dist\\{APP_NAME}_Setup_${{APP_VERSION}}.exe"
        InstallDir "$PROGRAMFILES\\{APP_NAME}"
        
        RequestExecutionLevel admin
        
        # Modern UI
        !insertmacro MUI_PAGE_WELCOME
        !insertmacro MUI_PAGE_DIRECTORY
        !insertmacro MUI_PAGE_INSTFILES
        !insertmacro MUI_PAGE_FINISH
        
        !insertmacro MUI_UNPAGE_CONFIRM
        !insertmacro MUI_UNPAGE_INSTFILES
        
        !insertmacro MUI_LANGUAGE "English"
        
        # Default section
        Section
            SetOutPath "$INSTDIR"
            
            # Copy main executable
            File "dist\\${{EXE_NAME}}"
            
            # Create shortcuts
            CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
            CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
            CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
            
            # Write uninstaller
            WriteUninstaller "$INSTDIR\\Uninstall.exe"
            
            # Add to PATH (basic method without EnvVarUpdate)
            ExecWait 'cmd.exe /c setx PATH "%PATH%;$INSTDIR" /M'
            
            # Add uninstall information to Add/Remove Programs
            WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
            WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$\\"$INSTDIR\\Uninstall.exe$\\""
            WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
            WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "Network Monitor Team"
        SectionEnd

        # Uninstaller section
        Section "Uninstall"
            Delete "$INSTDIR\\${{EXE_NAME}}"
            Delete "$INSTDIR\\Uninstall.exe"
            Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
            Delete "$DESKTOP\\${{APP_NAME}}.lnk"
            
            RMDir "$SMPROGRAMS\\${{APP_NAME}}"
            RMDir "$INSTDIR"
            
            # Remove uninstall information
            DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
        SectionEnd
        """
        
        # Write NSIS script
        with open("installer.nsi", "w") as f:
            f.write(nsis_script)
        
        # Run NSIS compiler
        subprocess.run(["makensis", "installer.nsi"], check=True)
        print(f"Windows installer created successfully in dist/{APP_NAME}_Setup_{APP_VERSION}.exe")
        return True
        
    except Exception as e:
        print(f"Error creating Windows installer: {e}")
        return False

def main():
    """Main build function"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Clean previous builds
    clean_previous_builds()
    
    # Build binary
    if build_binary():
        # Create installer for current platform
        if platform.system() == "Windows":
            create_windows_installer()
    
    print(f"Build complete. Files available in the '{OUTPUT_DIR}' directory.")
    return 0

if __name__ == "__main__":
    sys.exit(main())