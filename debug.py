"""
NetworkMonitor Debug Script
This script helps diagnose startup issues with NetworkMonitor
"""

import os
import sys
import platform
import logging
import traceback

# Configure verbose logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("NetworkMonitorDebug")

def run_diagnostic():
    """Run diagnostic checks and attempt to start the application with detailed logging"""
    logger.info("=" * 50)
    logger.info("NetworkMonitor Diagnostics")
    logger.info("=" * 50)
    
    # Log system information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Check admin privileges
    try:
        if platform.system() == "Windows":
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            logger.info(f"Running with admin privileges: {is_admin}")
            if not is_admin:
                logger.error("NetworkMonitor requires administrator privileges")
                print("Please run this script as Administrator")
                return
    except Exception as e:
        logger.error(f"Error checking admin privileges: {e}")
    
    # Check Npcap installation
    logger.info("Checking Npcap installation...")
    try:
        # Add the networkmonitor module to path
        if os.path.exists("networkmonitor"):
            sys.path.insert(0, os.path.abspath("."))
        
        from networkmonitor.npcap_helper import initialize_npcap, get_npcap_info
        
        npcap_initialized = initialize_npcap()
        npcap_info = get_npcap_info()
        
        logger.info(f"Npcap initialized: {npcap_initialized}")
        logger.info(f"Npcap info: {npcap_info}")
    except Exception as e:
        logger.error(f"Error initializing Npcap: {e}")
        traceback.print_exc()
    
    # Check dependencies
    logger.info("Checking dependencies...")
    try:
        from networkmonitor.dependency_check import DependencyChecker
        
        checker = DependencyChecker()
        all_ok, missing, warnings = checker.check_all_dependencies()
        
        logger.info(f"All dependencies OK: {all_ok}")
        if missing:
            logger.error(f"Missing dependencies: {missing}")
        if warnings:
            logger.warning(f"Dependency warnings: {warnings}")
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        traceback.print_exc()
    
    # Try to create splash screen
    logger.info("Testing splash screen...")
    try:
        from networkmonitor.splash import SplashScreen
        
        splash = SplashScreen()
        splash.show()
        splash.update_status("Splash screen test", 50)
        import time
        time.sleep(2)
        splash.close()
        logger.info("Splash screen test completed")
    except Exception as e:
        logger.error(f"Error creating splash screen: {e}")
        traceback.print_exc()
    
    # Attempt to create network controller
    logger.info("Testing network controller initialization...")
    try:
        from networkmonitor.monitor import NetworkController
        
        controller = NetworkController()
        logger.info("NetworkController initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing network controller: {e}")
        traceback.print_exc()
    
    # Test Flask server initialization
    logger.info("Testing Flask server initialization...")
    try:
        from networkmonitor.server import create_app
        
        app = create_app()
        logger.info("Flask app created successfully")
    except Exception as e:
        logger.error(f"Error creating Flask app: {e}")
        traceback.print_exc()
    
    # Test Tkinter UI
    logger.info("Testing Tkinter UI...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window
        logger.info(f"Tkinter initialized successfully: {tk.TkVersion}")
        root.destroy()
    except Exception as e:
        logger.error(f"Error initializing Tkinter: {e}")
        traceback.print_exc()
    
    # Try explicit launcher start
    logger.info("Testing launcher...")
    try:
        from networkmonitor.launcher import create_console_window
        
        console_window = create_console_window()
        if console_window:
            logger.info("Console window created successfully")
            console_window.after(5000, lambda: console_window.destroy())
            console_window.mainloop()
        else:
            logger.error("Failed to create console window")
    except Exception as e:
        logger.error(f"Error in launcher: {e}")
        traceback.print_exc()
    
    logger.info("=" * 50)
    logger.info("Diagnostic complete")
    logger.info("=" * 50)

if __name__ == "__main__":
    try:
        run_diagnostic()
    except Exception as e:
        logger.critical(f"Unhandled exception in diagnostic: {e}")
        traceback.print_exc()