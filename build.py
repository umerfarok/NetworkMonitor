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
WEB_DIR = "networkmonitor/web"

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

def build_frontend():
    """Build the Next.js frontend"""
    if os.path.exists(WEB_DIR):
        print("Building frontend...")
        os.chdir(WEB_DIR)
        
        # Make sure node_modules exists
        if not os.path.exists('node_modules'):
            print("Installing frontend dependencies...")
            if platform.system() == "Windows":
                subprocess.call("npm install", shell=True)
            else:
                subprocess.call("npm install", shell=True)
        
        # Build the frontend
        if platform.system() == "Windows":
            subprocess.call("npm run build", shell=True)
        else:
            subprocess.call("npm run build", shell=True)
            
        os.chdir("../..")  # Return to root directory
        print("Frontend build complete")
    else:
        print(f"Warning: Frontend directory not found at {WEB_DIR}")

def convert_icon():
    """Convert SVG icon to platform-specific format"""
    if not os.path.exists(ICON_PATH):
        print(f"Warning: Icon file not found at {ICON_PATH}")
        return None
    
    # For Windows, we need ICO
    if platform.system() == "Windows":
        try:
            from cairosvg import svg2png
            from PIL import Image
            import io
            
            print("Converting SVG icon to ICO...")
            ico_path = "assets/icon.ico"
            
            # First convert to PNG
            png_data = svg2png(url=ICON_PATH, output_width=256, output_height=256)
            png_image = Image.open(io.BytesIO(png_data))
            
            # Convert to ICO with multiple sizes
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
            print(f"Icon converted and saved to {ico_path}")
            return ico_path
        except ImportError:
            print("Warning: cairosvg or PIL not installed. Using SVG icon directly.")
            return ICON_PATH
        except Exception as e:
            print(f"Error converting icon: {e}")
            return ICON_PATH
    
    # For other platforms, return the original icon
    return ICON_PATH

def build_binary():
    """Build binary using PyInstaller"""
    print(f"Building {APP_NAME} for {platform.system()}...")
    
    # Convert icon for the platform
    icon_path = convert_icon() or ICON_PATH
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--clean",
        "--add-data", f"{WEB_DIR}/out;networkmonitor/web/out",  # Include built frontend
        "--add-data", "networkmonitor/requirements.txt;networkmonitor",
        "--add-data", f"assets;assets",  # Include assets directory
    ]
    
    # Add icon if exists
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Add platform-specific options
    if platform.system() == "Windows":
        cmd.append("--noconsole")
        cmd.append("--uac-admin")  # Request admin privileges on Windows
    
    # Add entry point
    cmd.append(ENTRY_POINT)
    
    # Run PyInstaller
    subprocess.call(cmd)
    print("Binary build complete")

def create_installer():
    """Create platform-specific installers"""
    system = platform.system()
    print(f"Creating installer for {system}...")
    
    if system == "Windows":
        # Use NSIS to create Windows installer
        # You need to have NSIS installed and in PATH
        try:
            # Generate NSIS script
            nsis_script = f"""
            !define APP_NAME "{APP_NAME}"
            !define APP_VERSION "{APP_VERSION}"
            !define EXE_NAME "{APP_NAME}.exe"
            
            Name "${{APP_NAME}} ${{APP_VERSION}}"
            OutFile "{OUTPUT_DIR}/{APP_NAME}_Setup_${{APP_VERSION}}.exe"
            InstallDir "$PROGRAMFILES\\{APP_NAME}"
            
            # Request admin privileges
            RequestExecutionLevel admin
            
            # Pages
            Page directory
            Page instfiles
            
            # Sections
            Section "Install"
                SetOutPath $INSTDIR
                
                # Copy executable
                File "dist\\${{EXE_NAME}}"
                
                # Create Start Menu shortcut
                CreateDirectory "$SMPROGRAMS\\{APP_NAME}"
                CreateShortcut "$SMPROGRAMS\\{APP_NAME}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
                
                # Create Desktop shortcut
                CreateShortcut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{EXE_NAME}}"
                
                # Create uninstaller
                WriteUninstaller "$INSTDIR\\uninstall.exe"
            SectionEnd
            
            # Uninstaller
            Section "Uninstall"
                Delete "$INSTDIR\\${{EXE_NAME}}"
                Delete "$INSTDIR\\uninstall.exe"
                
                # Remove shortcuts
                Delete "$SMPROGRAMS\\{APP_NAME}\\${{APP_NAME}}.lnk"
                RMDir "$SMPROGRAMS\\{APP_NAME}"
                Delete "$DESKTOP\\${{APP_NAME}}.lnk"
                
                RMDir "$INSTDIR"
            SectionEnd
            """
            
            # Write NSIS script
            with open("installer.nsi", "w") as f:
                f.write(nsis_script)
            
            # Run NSIS compiler
            subprocess.call(["makensis", "installer.nsi"])
            
            # Clean up
            os.remove("installer.nsi")
            
            print(f"Windows installer created: {OUTPUT_DIR}/{APP_NAME}_Setup_{APP_VERSION}.exe")
        except Exception as e:
            print(f"Error creating Windows installer: {e}")
            print("Make sure NSIS is installed and in your PATH")

    elif system == "Darwin":  # macOS
        try:
            # Create DMG file
            dmg_path = f"{OUTPUT_DIR}/{APP_NAME}_{APP_VERSION}.dmg"
            app_path = f"dist/{APP_NAME}.app"
            
            # Check if app exists (PyInstaller should create it)
            if not os.path.exists(app_path):
                print(f"Error: {app_path} not found. PyInstaller may not have created a proper .app bundle.")
                return
            
            # Create DMG
            subprocess.call([
                "hdiutil", "create",
                "-volname", f"{APP_NAME} {APP_VERSION}",
                "-srcfolder", app_path,
                "-ov", "-format", "UDZO",
                dmg_path
            ])
            
            print(f"macOS DMG created: {dmg_path}")
        except Exception as e:
            print(f"Error creating macOS DMG: {e}")

    elif system == "Linux":
        try:
            # Create DEB package (for Debian/Ubuntu)
            deb_dir = "deb_build"
            os.makedirs(f"{deb_dir}/DEBIAN", exist_ok=True)
            os.makedirs(f"{deb_dir}/usr/bin", exist_ok=True)
            os.makedirs(f"{deb_dir}/usr/share/applications", exist_ok=True)
            os.makedirs(f"{deb_dir}/usr/share/pixmaps", exist_ok=True)
            
            # Copy binary
            shutil.copy(f"dist/{APP_NAME}", f"{deb_dir}/usr/bin/{APP_NAME.lower()}")
            
            # Create desktop file
            with open(f"{deb_dir}/usr/share/applications/{APP_NAME.lower()}.desktop", "w") as f:
                f.write(f"""[Desktop Entry]
Name={APP_NAME}
Comment=Network monitoring and control tool
Exec=/usr/bin/{APP_NAME.lower()}
Icon={APP_NAME.lower()}
Terminal=false
Type=Application
Categories=Network;Utility;
""")
            
            # Copy icon
            if os.path.exists(ICON_PATH):
                shutil.copy(ICON_PATH, f"{deb_dir}/usr/share/pixmaps/{APP_NAME.lower()}.svg")
            
            # Create control file
            with open(f"{deb_dir}/DEBIAN/control", "w") as f:
                f.write(f"""Package: {APP_NAME.lower()}
Version: {APP_VERSION}
Section: net
Priority: optional
Architecture: amd64
Depends: libpcap0.8, net-tools
Maintainer: {APP_NAME} Team
Description: Network monitoring and control tool
 Allows scanning of local network, monitoring bandwidth,
 and controlling network access for devices.
""")
            
            # Build DEB package
            deb_file = f"{OUTPUT_DIR}/{APP_NAME}_{APP_VERSION}_amd64.deb"
            subprocess.call(["dpkg-deb", "--build", deb_dir, deb_file])
            
            # Clean up
            shutil.rmtree(deb_dir)
            
            print(f"Debian package created: {deb_file}")
            
            # Also create generic tarball for other Linux distros
            tar_file = f"{OUTPUT_DIR}/{APP_NAME}_{APP_VERSION}_linux.tar.gz"
            subprocess.call([
                "tar", "czf", tar_file,
                "-C", "dist", APP_NAME
            ])
            
            print(f"Linux tarball created: {tar_file}")
        except Exception as e:
            print(f"Error creating Linux packages: {e}")
            # Create a fallback tarball
            try:
                tar_file = f"{OUTPUT_DIR}/{APP_NAME}_{APP_VERSION}_linux.tar.gz"
                subprocess.call([
                    "tar", "czf", tar_file,
                    "-C", "dist", APP_NAME
                ])
                print(f"Linux tarball created: {tar_file}")
            except Exception as e2:
                print(f"Error creating Linux tarball: {e2}")

def main():
    """Main build function"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check if we have required tools
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Please run: pip install -r requirements-build.txt")
        return 1
    
    clean_previous_builds()
    build_frontend()
    build_binary()
    create_installer()
    
    print(f"Build complete. Installers available in the '{OUTPUT_DIR}' directory.")
    return 0

if __name__ == "__main__":
    sys.exit(main())