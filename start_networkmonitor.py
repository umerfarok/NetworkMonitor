"""
NetworkMonitor Application Starter
This script provides a reliable entry point for starting NetworkMonitor
"""
import os
import sys
import platform
import traceback
import ctypes
import time
import logging
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor_startup.log'),
        logging.StreamHandler(sys.stdout)  # Explicitly use stdout
    ]
)
logger = logging.getLogger(__name__)

def check_admin():
    """Check if running as administrator and restart if not"""
    try:
        is_admin = False
        if platform.system() == 'Windows':
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            
        if not is_admin:
            logger.warning("NetworkMonitor requires administrator privileges.")
            print("\nNetworkMonitor requires administrator privileges.")
            print("Please run this script as administrator.")
            
            if platform.system() == 'Windows':
                # Try to restart with admin privileges
                logger.info("Attempting to restart with elevated privileges...")
                print("\nAttempting to restart with elevated privileges...")
                script = sys.argv[0]
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
                sys.exit(0)
            
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking admin privileges: {e}")
        print(f"\nError checking admin privileges: {e}")
        return False

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("NetworkMonitor Startup")
    print("="*60 + "\n")
    
    logger.info("NetworkMonitor startup initiated")
    
    try:
        # Check for admin privileges
        if not check_admin():
            print("\nPress Enter to exit...")
            input()
            return 1
            
        print(f"Running as Administrator: {ctypes.windll.shell32.IsUserAnAdmin() != 0}")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Script path: {os.path.abspath(__file__)}")
        print("Loading modules...\n")
        
        # Make sure the current directory is in the path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        # Method 1: Try importing the CLI module
        print("Method 1: Starting via CLI...")
        try:
            from networkmonitor.cli import entry_point
            logger.info("Starting via CLI entry point")
            print("Starting Network Monitor...\n")
            entry_point()
            return 0
        except Exception as e:
            logger.error(f"Error using CLI method: {e}")
            print(f"\nError using CLI method: {e}")
            traceback.print_exc()
            
        # Method 2: Try launcher directly
        print("\nMethod 2: Starting via launcher...")
        try:
            from networkmonitor.launcher import main as launcher_main
            logger.info("Starting via launcher main function")
            result = launcher_main()
            return result
        except Exception as e:
            logger.error(f"Error using launcher method: {e}")
            print(f"\nError using launcher method: {e}")
            traceback.print_exc()
            
        # Method 3: Use the run_app.py approach
        print("\nMethod 3: Starting via run_app...")
        try:
            import run_app
            logger.info("Starting via run_app module")
            result = run_app.run_with_exception_handling()
            return result
        except Exception as e:
            logger.error(f"Error using run_app method: {e}")
            print(f"\nError using run_app method: {e}")
            traceback.print_exc()
        
        logger.error("All startup methods failed")
        print("\nAll startup methods failed.")
        print("\nPress Enter to exit...")
        input()
        return 1
            
    except Exception as e:
        logger.critical(f"Critical error during startup: {e}")
        print(f"\nCRITICAL ERROR: {e}")
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        logger.info(f"Application exited with code: {exit_code}")
        print(f"\nApplication exited with code: {exit_code}")
        print("\nPress Enter to close this window...")
        input()
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception in main script: {e}")
        print(f"\nUnhandled exception in main script: {e}")
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)