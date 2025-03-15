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
    """Create a modern, professional status window that keeps the application running"""
    root = tk.Tk()
    root.title("NetworkMonitor Status")
    root.geometry("500x300")  # Increased size for better visibility
    root.minsize(500, 300)  # Set minimum size
    
    # Define color scheme
    COLORS = {
        'bg': '#1e1e1e',  # Dark background
        'fg': '#e0e0e0',  # Light text
        'accent': '#007acc',  # Blue accent
        'success': '#2ecc71',  # Green
        'error': '#e74c3c',  # Red
        'warning': '#f1c40f',  # Yellow
        'header_bg': '#252526',  # Slightly lighter than bg
        'button_bg': '#333333',  # Button background
        'button_hover': '#404040'  # Button hover
    }
    
    # Configure root window
    root.configure(bg=COLORS['bg'])
    
    # Add icon if available
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        logger.warning(f"Could not load icon: {e}")
    
    # Create main container with padding
    main_frame = tk.Frame(root, bg=COLORS['bg'], padx=20, pady=15)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header with gradient effect
    header_frame = tk.Frame(main_frame, bg=COLORS['header_bg'], height=60)
    header_frame.pack(fill=tk.X, pady=(0, 15))
    header_frame.pack_propagate(False)  # Maintain fixed height
    
    header_label = tk.Label(
        header_frame, 
        text="NetworkMonitor",
        font=("Segoe UI", 18, "bold"),
        bg=COLORS['header_bg'],
        fg=COLORS['fg']
    )
    header_label.place(relx=0.5, rely=0.5, anchor='center')
    
    # Status section with background
    status_frame = tk.Frame(main_frame, bg=COLORS['header_bg'], height=40)
    status_frame.pack(fill=tk.X, pady=(0, 15))
    status_frame.pack_propagate(False)
    
    status_var = tk.StringVar(value="Starting NetworkMonitor...")
    status_label = tk.Label(
        status_frame,
        textvariable=status_var,
        font=("Segoe UI", 10),
        bg=COLORS['header_bg'],
        fg=COLORS['fg']
    )
    status_label.place(relx=0.02, rely=0.5, anchor='w')
    
    # Status indicator dot
    status_indicator = tk.Canvas(
        status_frame,
        width=10,
        height=10,
        bg=COLORS['header_bg'],
        highlightthickness=0
    )
    status_indicator.place(relx=0.98, rely=0.5, anchor='e')
    
    # Draw initial status dot
    status_indicator.create_oval(0, 0, 10, 10, fill=COLORS['warning'], outline='')
    
    # URL section with modern styling
    url_frame = tk.Frame(main_frame, bg=COLORS['bg'])
    url_frame.pack(fill=tk.X, pady=(0, 15))
    
    url_label = tk.Label(
        url_frame,
        text="Web Interface:",
        font=("Segoe UI", 10),
        bg=COLORS['bg'],
        fg=COLORS['fg']
    )
    url_label.pack(side=tk.LEFT, padx=(0, 5))
    
    url_var = tk.StringVar(value="http://localhost:5000")
    url_value = tk.Label(
        url_frame,
        textvariable=url_var,
        font=("Segoe UI", 10, "underline"),
        bg=COLORS['bg'],
        fg=COLORS['accent'],
        cursor="hand2"
    )
    url_value.pack(side=tk.LEFT, padx=(0, 10))
    
    # Add hover effect for URL
    def on_url_hover(event): url_value.configure(fg=COLORS['success'])
    def on_url_leave(event): url_value.configure(fg=COLORS['accent'])
    url_value.bind('<Enter>', on_url_hover)
    url_value.bind('<Leave>', on_url_leave)
    url_value.bind('<Button-1>', lambda e: webbrowser.open(url_var.get()))
    
    # Add copy button with modern styling
    def copy_url():
        root.clipboard_clear()
        root.clipboard_append(url_var.get())
        copy_button.configure(text="✓ Copied")
        root.after(2000, lambda: copy_button.configure(text="Copy"))
    
    copy_button = tk.Button(
        url_frame,
        text="Copy",
        command=copy_url,
        font=("Segoe UI", 9),
        bg=COLORS['button_bg'],
        fg=COLORS['fg'],
        activebackground=COLORS['button_hover'],
        activeforeground=COLORS['fg'],
        relief=tk.FLAT,
        padx=10
    )
    copy_button.pack(side=tk.LEFT)
    
    # Button container
    button_frame = tk.Frame(main_frame, bg=COLORS['bg'])
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Create modern-styled button
    def create_button(text, command, width=15, **kwargs):
        btn = tk.Button(
            button_frame,
            text=text,
            command=command,
            font=("Segoe UI", 9),
            bg=COLORS['button_bg'],
            fg=COLORS['fg'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['fg'],
            relief=tk.FLAT,
            width=width,
            padx=10,
            pady=5,
            **kwargs
        )
        return btn
    
    # Add buttons with hover effect
    open_button = create_button("Open in Browser", lambda: webbrowser.open(url_var.get()))
    open_button.pack(side=tk.LEFT, padx=(0, 5))
    
    def minimize_to_tray():
        root.withdraw()
        # Add tray icon functionality here if needed
        # This will be handled by the system tray implementation
    
    minimize_button = create_button("Run in Background", minimize_to_tray, width=20)
    minimize_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = create_button("Exit", lambda: (root.destroy(), os._exit(0)), width=10)
    exit_button.pack(side=tk.RIGHT)
    
    # Function to update status
    def update_status(running=False, message=None):
        if running:
            status_var.set("NetworkMonitor is running")
            status_indicator.delete('all')
            status_indicator.create_oval(0, 0, 10, 10, fill=COLORS['success'], outline='')
            open_button.configure(state=tk.NORMAL)
        else:
            status_msg = message if message else "Starting..."
            status_var.set(status_msg)
            status_indicator.delete('all')
            status_indicator.create_oval(0, 0, 10, 10, fill=COLORS['warning'], outline='')
            open_button.configure(state=tk.DISABLED)
    
    # Initial status update
    update_status(False, "Starting NetworkMonitor...")
    
    return root, status_var, url_var, update_status

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
        status_window, status_var, url_var, update_status = create_status_window()
        
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
        def update_status_periodically():
            if server_started:
                update_status(True)
            elif server_error:
                update_status(False, f"Error: {server_error[:40]}...")
                # Show error dialog after a delay to ensure it appears after the window
                status_window.after(1000, lambda: show_error_dialog("NetworkMonitor Error", server_error))
            else:
                update_status(False, "Starting NetworkMonitor...")
                status_window.after(1000, update_status_periodically)
        
        status_window.after(100, update_status_periodically)
        
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