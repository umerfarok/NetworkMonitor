"""
Simple launcher script for NetworkMonitor that will show all errors
"""
import os
import sys
import traceback
import logging
import tkinter as tk
from tkinter import messagebox
import time
import threading
import webbrowser

# Configure very verbose logging
log_handlers = [
    logging.FileHandler('networkmonitor_startup.log'),
    logging.StreamHandler(sys.stdout)  # Explicitly use stdout
]

# Add console handler with a more visible format
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('\n%(levelname)s: %(message)s'))
log_handlers.append(console_handler)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger("NetworkMonitorLauncher")

def show_error_dialog(message, detail=None):
    """Show an error dialog to the user"""
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        full_message = message
        if detail:
            full_message += f"\n\nDetails:\n{detail}"
            
        messagebox.showerror("NetworkMonitor Error", full_message)
        root.destroy()
    except:
        # If dialog fails, fall back to console
        print("\nERROR:", message)
        if detail:
            print("\nDetails:", detail)

def create_status_window():
    """Create a status window that keeps the application running"""
    root = tk.Tk()
    root.title("NetworkMonitor Status")
    root.geometry("400x200")
    
    # Add icon if available
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        logger.warning(f"Could not load icon: {e}")
    
    # Status label
    status_var = tk.StringVar(value="Starting NetworkMonitor...")
    status_label = tk.Label(root, textvariable=status_var, font=("Arial", 12))
    status_label.pack(pady=20)
    
    # URL label
    url_label = tk.Label(root, text="Web interface available at:", font=("Arial", 10))
    url_label.pack(pady=5)
    
    url_var = tk.StringVar(value="http://localhost:5000")
    url_value = tk.Label(root, textvariable=url_var, font=("Arial", 10, "underline"), fg="blue")
    url_value.pack(pady=5)
    
    # Add button to open browser
    def open_browser():
        webbrowser.open(url_var.get())
    
    open_button = tk.Button(root, text="Open in Browser", command=open_browser)
    open_button.pack(pady=10)
    
    # Add exit button
    exit_button = tk.Button(root, text="Exit NetworkMonitor", command=lambda: (root.destroy(), os._exit(0)))
    exit_button.pack(pady=10)
    
    return root, status_var, url_var

def run_with_exception_handling():
    """Run the application with detailed exception handling"""
    try:
        logger.info("Starting NetworkMonitor application")
        print("\nStarting NetworkMonitor application...")
        
        # Check if we're running as admin
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        logger.info(f"Running as admin: {is_admin}")
        print(f"Running as admin: {is_admin}")
        
        if not is_admin:
            msg = "Administrator privileges required.\nPlease run as administrator."
            logger.warning(msg)
            show_error_dialog(msg)
            return 1
        
        # Create status window first
        status_window, status_var, url_var = create_status_window()
        
        # Start the launcher in a background thread to prevent blocking the UI
        server_started = False
        server_error = None
        server_controller = None
        
        def run_launcher():
            nonlocal server_started, server_error, server_controller
            try:
                # First ensure Npcap is initialized
                try:
                    # Try relative import first
                    from networkmonitor.npcap_helper import initialize_npcap, verify_npcap_installation
                except ImportError:
                    # Add parent directory to path
                    parent_dir = os.path.dirname(os.path.abspath(__file__))
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    from networkmonitor.npcap_helper import initialize_npcap, verify_npcap_installation
                
                logger.info("Initializing Npcap support")
                npcap_initialized = initialize_npcap()
                if not npcap_initialized:
                    status_var.set("Npcap initialization failed!")
                    server_error = "Failed to initialize Npcap. Please install Npcap from https://npcap.com/"
                    logger.error(server_error)
                    return 1
                
                logger.info("Npcap initialized successfully")
                status_var.set("Starting network monitoring...")
                
                # Now launch the server
                try:
                    from networkmonitor.launcher import start_server
                    status_var.set("Starting server...")
                    success, controller = start_server(host='127.0.0.1', port=5000)
                    server_controller = controller
                    
                    if success:
                        server_started = True
                        status_var.set("NetworkMonitor is running")
                        logger.info("Server started successfully")
                        return 0
                    else:
                        server_error = "Failed to start server"
                        status_var.set("Failed to start server")
                        logger.error(server_error)
                        return 1
                except Exception as e:
                    error_detail = traceback.format_exc()
                    server_error = f"Error starting server: {str(e)}"
                    status_var.set("Error starting server")
                    logger.error(f"{server_error}\n{error_detail}")
                    return 1
                    
            except Exception as e:
                error_detail = traceback.format_exc()
                server_error = f"Error in launcher: {str(e)}"
                status_var.set("Error in launcher")
                logger.error(f"{server_error}\n{error_detail}")
                return 1
        
        # Start launcher thread
        launcher_thread = threading.Thread(target=run_launcher, daemon=True)
        launcher_thread.start()
        
        # Update status periodically
        def update_status():
            if server_started:
                status_var.set("NetworkMonitor is running")
            elif server_error:
                status_var.set(f"Error: {server_error[:40]}...")
                # Show error dialog after a delay to ensure it appears after the window
                status_window.after(1000, lambda: show_error_dialog("NetworkMonitor Error", server_error))
            else:
                status_var.set("Starting NetworkMonitor...")
                status_window.after(1000, update_status)
        
        status_window.after(100, update_status)
        
        # Keep the application running
        status_window.protocol("WM_DELETE_WINDOW", lambda: (status_window.destroy(), os._exit(0)))
        status_window.mainloop()
        
        # Clean up on exit
        if server_controller:
            try:
                server_controller.stop_monitoring()
            except:
                pass
        
        return 0
            
    except Exception as e:
        error_msg = "Critical error starting NetworkMonitor"
        detail = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        logger.critical(f"{error_msg}\n{detail}")
        show_error_dialog(error_msg, detail)
        return 1

if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("NetworkMonitor Debug Launcher")
        print("=" * 60 + "\n")
        
        exit_code = run_with_exception_handling()
        
        if exit_code != 0:
            print(f"\nApplication exited with error code: {exit_code}")
            print("Check networkmonitor_startup.log for details")
            print("\nPress Enter to exit...")
            input()
        
        sys.exit(exit_code)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)