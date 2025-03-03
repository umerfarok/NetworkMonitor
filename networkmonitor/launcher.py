"""
Network Monitor Application Launcher
This script launches both the backend server and opens the web interface
"""
import os
import sys
import time
import platform
import threading
import webbrowser
import logging
import traceback
import tempfile
import ctypes
import requests
import socket
import tkinter as tk
from pathlib import Path
from .dependency_check import check_system_requirements

# Setup consistent logging across all modules
def setup_logging():
    """Configure logging to write to both file and console with proper formatting"""
    if getattr(sys, 'frozen', False):
        # We're running in a PyInstaller bundle
        base_dir = os.path.dirname(sys.executable)
    else:
        # We're running in a normal Python environment
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Setup log directory
    if platform.system() == 'Windows':
        log_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'NetworkMonitor', 'logs')
    else:
        log_dir = os.path.join(os.path.expanduser('~'), '.networkmonitor', 'logs')

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'networkmonitor.log')

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to DEBUG for development

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file at {log_file}: {e}")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    return log_file

# Initialize logging first thing
log_file = setup_logging()
logger = logging.getLogger(__name__)

# Log startup information
logger.info("="*50)
logger.info("Network Monitor Starting")
logger.info("="*50)
logger.info(f"Python version: {sys.version}")
logger.info(f"Platform: {platform.platform()}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Log file: {log_file}")

def is_admin():
    """Check if the application is running with admin privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.error(f"Error checking admin privileges: {e}")
        return False

def restart_as_admin():
    """Restart the current script with admin privileges"""
    if platform.system() == "Windows":
        script = sys.argv[0]
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
        except Exception as e:
            logger.error(f"Failed to restart as admin: {e}")
            print(f"Error requesting admin privileges: {e}")
        sys.exit()
    else:
        # For Linux/Mac, suggest using sudo
        print("Please run this application with sudo privileges")
        sys.exit(1)

def is_port_in_use(port, host='127.0.0.1'):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def wait_for_server(url, max_retries=30, retry_delay=1):
    """
    Wait for server to be available
    
    Args:
        url (str): URL to check
        max_retries (int): Maximum number of retries
        retry_delay (float): Delay between retries in seconds
    
    Returns:
        bool: True if server is available, False otherwise
    """
    logger.info(f"Waiting for server at {url}")
    
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                logger.info(f"Server is available at {url}")
                return True
            else:
                logger.debug(f"Server returned status {response.status_code}")
        except requests.RequestException:
            pass
        
        # Wait before retrying
        if i < max_retries - 1:
            time.sleep(retry_delay)
    
    logger.error(f"Server not available after {max_retries} attempts")
    return False

def open_browser(url):
    """Open web browser to specified URL"""
    try:
        logger.info(f"Opening web browser to {url}")
        webbrowser.open(url)
        return True
    except Exception as e:
        logger.error(f"Failed to open web browser: {e}")
        return False

def create_console_window():
    """Create a modern, user-friendly console window to display logs and status"""
    if platform.system() == "Windows":
        try:
            from tkinter import scrolledtext, ttk
            import threading
            import webbrowser
            
            # Configure font sizes based on screen resolution
            try:
                root = tk.Tk()
                screen_width = root.winfo_screenwidth()
                font_size = 10 if screen_width > 1920 else 9
                button_font_size = 10 if screen_width > 1920 else 9
                root.destroy()
            except:
                font_size = 9
                button_font_size = 9
            
            # Create and style the main window
            console_root = tk.Tk()
            console_root.title("Network Monitor Dashboard")
            console_root.geometry("900x600")
            console_root.minsize(800, 500)
            
            # Set dark mode colors
            COLORS = {
                'bg': '#1e1e1e',  # Dark background
                'fg': '#e0e0e0',  # Light text
                'accent': '#007acc',  # Blue accent
                'success': '#2ecc71',  # Green
                'error': '#e74c3c',  # Red
                'warning': '#f1c40f',  # Yellow
                'header_bg': '#252526',  # Slightly lighter than bg
                'button_bg': '#333333',  # Button background
                'button_hover': '#404040',  # Button hover
                'input_bg': '#2d2d2d'  # Input background
            }
            
            # Configure the window style
            style = ttk.Style()
            
            # Configure common styles
            style.configure('Main.TFrame', background=COLORS['bg'])
            style.configure('Header.TFrame', background=COLORS['header_bg'])
            style.configure('Header.TLabel', 
                          font=('Segoe UI', 20, 'bold'), 
                          background=COLORS['header_bg'], 
                          foreground=COLORS['fg'])
            style.configure('Status.TLabel', 
                          font=('Segoe UI', font_size), 
                          background=COLORS['bg'], 
                          foreground=COLORS['fg'])
            style.configure('URL.TLabel', 
                          font=('Segoe UI', font_size, 'underline'), 
                          foreground=COLORS['accent'], 
                          background=COLORS['bg'])
            
            # Configure custom button style
            style.configure('Custom.TButton',
                          font=('Segoe UI', button_font_size),
                          background=COLORS['button_bg'],
                          foreground=COLORS['fg'],
                          borderwidth=0,
                          padding=10)
            style.map('Custom.TButton',
                     background=[('active', COLORS['button_hover'])])
            
            # Set window icon if available
            try:
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    
                icon_path = os.path.join(base_path, "assets", "icon.ico")
                if os.path.exists(icon_path):
                    console_root.iconbitmap(icon_path)
            except Exception as e:
                logger.debug(f"Could not set window icon: {e}")
            
            # Configure root window
            console_root.configure(bg=COLORS['bg'])
            
            # Create main container with padding
            main_frame = ttk.Frame(console_root, style='Main.TFrame', padding=(20, 15, 20, 15))
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header section with gradient effect
            header_frame = ttk.Frame(main_frame, style='Header.TFrame')
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Create gradient canvas for header background
            header_canvas = tk.Canvas(header_frame, 
                                   height=60, 
                                   bg=COLORS['header_bg'], 
                                   highlightthickness=0)
            header_canvas.pack(fill=tk.X)
            
            # Add header text
            header_label = tk.Label(header_canvas, 
                                  text="Network Monitor", 
                                  font=('Segoe UI', 24, 'bold'),
                                  bg=COLORS['header_bg'],
                                  fg=COLORS['fg'])
            header_label.place(relx=0.02, rely=0.5, anchor='w')
            
            # Status section with modern styling
            status_frame = ttk.Frame(main_frame, style='Main.TFrame')
            status_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Create a canvas for status background
            status_canvas = tk.Canvas(status_frame, 
                                    height=40, 
                                    bg=COLORS['bg'], 
                                    highlightthickness=0)
            status_canvas.pack(fill=tk.X)
            
            # Draw rounded rectangle for status background
            status_canvas.create_rectangle(0, 0, 900, 40, 
                                         fill=COLORS['header_bg'],
                                         width=0)
            
            status_var = tk.StringVar(value="Starting services...")
            status_label = tk.Label(status_canvas, 
                                  textvariable=status_var,
                                  font=('Segoe UI', font_size),
                                  bg=COLORS['header_bg'],
                                  fg=COLORS['fg'])
            status_label.place(relx=0.02, rely=0.5, anchor='w')
            
            # Server status indicator (animated dot)
            server_running = tk.BooleanVar(value=False)
            status_indicator = tk.Canvas(status_canvas, 
                                      width=12, height=12,
                                      bg=COLORS['header_bg'],
                                      highlightthickness=0)
            status_indicator.place(relx=0.98, rely=0.5, anchor='e')
            
            def update_status_indicator(is_running=None):
                color = COLORS['success'] if server_running.get() else COLORS['error']
                status_indicator.delete('all')
                # Draw glowing dot effect
                status_indicator.create_oval(2, 2, 10, 10, 
                                          fill=color,
                                          outline=color,
                                          width=2)
            
            # URL section with modern styling
            url_frame = ttk.Frame(main_frame, style='Main.TFrame')
            url_frame.pack(fill=tk.X, pady=(0, 15))
            
            url_var = tk.StringVar(value="http://localhost:5000")
            url_label = tk.Label(url_frame, 
                               text="Web Interface:",
                               font=('Segoe UI', font_size),
                               bg=COLORS['bg'],
                               fg=COLORS['fg'])
            url_label.pack(side=tk.LEFT)
            
            url_value = tk.Label(url_frame,
                               textvariable=url_var,
                               font=('Segoe UI', font_size, 'underline'),
                               bg=COLORS['bg'],
                               fg=COLORS['accent'],
                               cursor='hand2')
            url_value.pack(side=tk.LEFT, padx=(5, 10))
            url_value.bind('<Button-1>', lambda e: webbrowser.open(url_var.get()))
            url_value.bind('<Enter>', lambda e: url_value.configure(fg=COLORS['success']))
            url_value.bind('<Leave>', lambda e: url_value.configure(fg=COLORS['accent']))
            
            def copy_url():
                console_root.clipboard_clear()
                console_root.clipboard_append(url_var.get())
                copy_button.configure(text="✓ Copied")
                console_root.after(2000, lambda: copy_button.configure(text="Copy"))
            
            copy_button = ttk.Button(url_frame,
                                   text="Copy",
                                   command=copy_url,
                                   style='Custom.TButton',
                                   width=8)
            copy_button.pack(side=tk.LEFT)
            
            # Log display with improved styling
            log_frame = ttk.Frame(main_frame, style='Main.TFrame')
            log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            log_label = tk.Label(log_frame,
                               text="Application Log:",
                               font=('Segoe UI', font_size),
                               bg=COLORS['bg'],
                               fg=COLORS['fg'])
            log_label.pack(anchor=tk.W)
            
            # Custom scrolled text widget with dark theme
            log_display = scrolledtext.ScrolledText(
                log_frame,
                height=15,
                font=("Cascadia Code", font_size),
                bg=COLORS['input_bg'],
                fg=COLORS['fg'],
                insertbackground=COLORS['fg'],
                selectbackground=COLORS['accent'],
                selectforeground=COLORS['fg'],
                relief=tk.FLAT,
                padx=10,
                pady=10
            )
            log_display.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Control buttons frame
            button_frame = ttk.Frame(main_frame, style='Main.TFrame')
            button_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Create minimize to tray functionality
            def minimize_to_tray():
                console_root.withdraw()  # Hide the window
                # Create system tray icon
                try:
                    import pystray
                    from PIL import Image
                    
                    def show_window(icon, item):
                        icon.stop()
                        console_root.after(0, console_root.deiconify)
                    
                    def exit_app(icon, item):
                        icon.stop()
                        console_root.after(0, lambda: os._exit(0))
                    
                    # Create tray icon menu
                    menu = pystray.Menu(
                        pystray.MenuItem("Show Dashboard", show_window),
                        pystray.MenuItem("Exit", exit_app)
                    )
                    
                    # Create and run tray icon
                    icon_path = os.path.join(base_path, "assets", "icon.ico")
                    if os.path.exists(icon_path):
                        icon_image = Image.open(icon_path)
                    else:
                        # Create a default icon if the icon file is not found
                        icon_image = Image.new('RGB', (64, 64), color='#1e88e5')
                    
                    icon = pystray.Icon("NetworkMonitor", icon_image, "Network Monitor", menu)
                    icon.run()
                except ImportError:
                    logger.warning("pystray not installed, minimizing to taskbar instead")
                    console_root.iconify()
            
            minimize_button = ttk.Button(
                button_frame,
                text="Run in Background",
                command=minimize_to_tray,
                style='Custom.TButton',
                width=20
            )
            minimize_button.pack(side=tk.LEFT, padx=(0, 5))
            
            open_button = ttk.Button(
                button_frame,
                text="Open in Browser",
                command=lambda: webbrowser.open(url_var.get()),
                style='Custom.TButton',
                state=tk.DISABLED,
                width=15
            )
            open_button.pack(side=tk.LEFT, padx=5)
            
            restart_button = ttk.Button(
                button_frame,
                text="Restart Service",
                command=lambda: restart_server(),
                style='Custom.TButton',
                width=15
            )
            restart_button.pack(side=tk.LEFT, padx=5)
            
            exit_button = ttk.Button(
                button_frame,
                text="Exit",
                command=lambda: confirm_exit(),
                style='Custom.TButton',
                width=10
            )
            exit_button.pack(side=tk.RIGHT)
            
            # Add exit confirmation dialog
            def confirm_exit():
                if tk.messagebox.askokcancel(
                    "Exit Network Monitor",
                    "Are you sure you want to exit Network Monitor?\nThis will stop the monitoring service."
                ):
                    os._exit(0)
            
            # Update function for status display with color transitions
            def update_status_display(is_running=None, message=None):
                if is_running is not None:
                    server_running.set(is_running)
                    
                if server_running.get():
                    status_var.set("Status: Running")
                    status_label.configure(fg=COLORS['success'])
                    open_button.configure(state=tk.NORMAL)
                else:
                    status_msg = message if message else "Not Running"
                    status_var.set(f"Status: {status_msg}")
                    status_label.configure(fg=COLORS['error'])
                    open_button.configure(state=tk.DISABLED)
                
                update_status_indicator()
                console_root.update_idletasks()
            
            # Server controller reference
            server_controller = {"instance": None, "url": None, "thread": None}
            
            # Function to restart the server
            def restart_server():
                nonlocal server_controller
                try:
                    update_status_display(False, "Restarting...")
                    log_display.insert(tk.END, "\nRestarting server...\n")
                    log_display.see(tk.END)
                    
                    # Stop existing controller if running
                    if server_controller["instance"] is not None:
                        try:
                            server_controller["instance"].stop_monitoring()
                            log_display.insert(tk.END, "Stopped previous monitoring.\n")
                        except Exception as e:
                            log_display.insert(tk.END, f"Error stopping previous monitor: {e}\n")
                    
                    # Wait for previous thread to finish
                    if server_controller["thread"] is not None and server_controller["thread"].is_alive():
                        server_controller["thread"].join(timeout=5)
                    
                    # Start new server
                    log_display.insert(tk.END, "Starting new server...\n")
                    
                    # Get host and port from URL
                    url = url_var.get()
                    host = "127.0.0.1"  # Default
                    port = 5000  # Default
                    
                    if "://" in url:
                        url_parts = url.split("://")[1].split(":")
                        if len(url_parts) > 0:
                            host_part = url_parts[0]
                            if host_part:
                                host = host_part
                        if len(url_parts) > 1:
                            port_part = url_parts[1].split("/")[0]
                            if port_part.isdigit():
                                port = int(port_part)
                    
                    # Create thread to start server
                    server_thread = threading.Thread(
                        target=lambda: start_server_with_feedback(host, port, update_status_display, log_display),
                        daemon=True
                    )
                    server_thread.start()
                    server_controller["thread"] = server_thread
                    
                except Exception as e:
                    log_display.insert(tk.END, f"Error restarting server: {e}\n")
                    log_display.see(tk.END)
            
            # Function to update log display
            def update_logs():
                try:
                    with open(log_file, 'r') as f:
                        # Start from the end of the file if it's large
                        if f.seek(0, 2) > 10000:  # If file is > 10KB
                            f.seek(-10000, 2)  # Read last 10KB
                            f.readline()  # Skip partial line
                        else:
                            f.seek(0)  # Otherwise read from start
                        log_text = f.read()
                    
                    log_display.delete(1.0, tk.END)
                    log_display.insert(tk.END, log_text)
                    log_display.see(tk.END)
                except Exception as e:
                    log_display.insert(tk.END, f"\nError reading log: {e}\n")
                
                # Schedule next update
                console_root.after(2000, update_logs)
            
            # Function to start server with UI feedback
            def start_server_with_feedback(host, port, update_status_fn, log_widget):
                nonlocal server_controller
                try:
                    log_widget.insert(tk.END, f"Starting server on {host}:{port}...\n")
                    log_widget.see(tk.END)
                    
                    # Start the server and store controller reference
                    success, controller = start_server(host, port)
                    server_controller["instance"] = controller
                    server_controller["url"] = f"http://{host}:{port}"
                    
                    if success:
                        log_widget.insert(tk.END, "Server started successfully.\n")
                        # Update URL if it was changed
                        if server_controller["url"] != url_var.get():
                            url_var.set(server_controller["url"])
                        update_status_fn(True)
                    else:
                        log_widget.insert(tk.END, "Failed to start server.\n")
                        update_status_fn(False, "Failed")
                    
                    log_widget.see(tk.END)
                except Exception as e:
                    log_widget.insert(tk.END, f"Error starting server: {e}\n")
                    log_widget.see(tk.END)
                    update_status_fn(False, "Error")
            
            # Set up periodic log updates
            update_logs()
            
            # Start server automatically after a short delay
            console_root.after(1000, restart_server)
            
            # Handle window close with confirmation
            console_root.protocol("WM_DELETE_WINDOW", confirm_exit)
            
            return console_root
        except Exception as e:
            logger.error(f"Failed to create console window: {e}")
            return None
    
    return None

def start_server(host='127.0.0.1', port=5000):
    """
    Start the Flask server with proper error handling
    
    Returns:
        Tuple[bool, NetworkController]: Success flag and the controller instance if successful
    """
    # First try relative imports and then fall back to absolute imports
    controller = None
    
    # Define SplashScreen class first to ensure it's available in all code paths
    class SimpleSplashScreen:
        def update_status(self, msg, progress=None):
            logger.info(msg)
        def close(self):
            pass
    
    # Create a splash instance that will be available throughout this function
    splash = SimpleSplashScreen()
    
    try:
        # Try importing the proper splash screen
        try:
            from .splash import SplashScreen
            splash = SplashScreen()
        except ImportError:
            try:
                from networkmonitor.splash import SplashScreen
                splash = SplashScreen()
            except ImportError:
                # We're already using the SimpleSplashScreen defined above
                pass
        
        # Show the splash if it has a show method
        if hasattr(splash, 'show'):
            splash.show()
        
        # Try to import server components
        try:
            # Try relative import first
            from .server import create_app
            from .monitor import NetworkController
            splash.update_status("Imported server modules", 30)
        except ImportError:
            # Try absolute import if relative fails
            try:
                import networkmonitor.server
                import networkmonitor.monitor
                from networkmonitor.server import create_app
                from networkmonitor.monitor import NetworkController
                splash.update_status("Imported server modules", 30)
            except ImportError as e:
                logger.error(f"ImportError: Failed to import server modules: {e}")
                splash.update_status(f"Error: Failed to import server modules. {e}", 100)
                return False, None
        except Exception as e:
            logger.error(f"Critical error importing server components: {e}")
            splash.update_status(f"Error importing modules: {e}", 100)
            return False, None
        
        try:
            # Initialize controller
            logger.info("Initializing network controller")
            splash.update_status("Initializing network controller", 40)
            controller = NetworkController()
            
            # Start monitoring
            logger.info("Starting network monitoring")
            splash.update_status("Starting network monitoring", 50)
            controller.start_monitoring()
            logger.info("Network monitoring started")
        except Exception as e:
            logger.warning(f"Error setting up network monitoring: {e}")
            splash.update_status(f"Error setting up network monitoring: {e}", 60)
            # Continue anyway to try to start the web interface
        
        try:
            # Create and start Flask app
            logger.info(f"Starting Flask server on {host}:{port}")
            splash.update_status("Starting web server", 70)
            app = create_app(host=host, port=port)
            
            # Start Flask app in a separate thread to avoid blocking
            server_thread = threading.Thread(
                target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
                daemon=False  # Changed to non-daemon so it keeps running
            )
            server_thread.start()
            
            # Wait for server to come online
            splash.update_status("Waiting for server to start", 80)
            server_url = f"http://{host}:{port}"
            if wait_for_server(server_url):
                # Server started successfully, open browser
                splash.update_status("Opening web browser", 90)
                open_browser(server_url)
                splash.update_status("Application started successfully", 100)
                time.sleep(1)  # Give time to see the success message
                return True, controller
            else:
                # Server failed to start
                splash.update_status("Server failed to start", 100)
                logger.error("Server failed to start in time")
                if controller:
                    controller.stop_monitoring()
                time.sleep(3)  # Show error message for a while
                return False, None
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
            splash.update_status(f"Error starting web server: {e}", 100)
            if controller:
                controller.stop_monitoring()
            return False, None
            
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        traceback.print_exc()
        if 'controller' in locals() and controller:
            controller.stop_monitoring()
        splash.update_status(f"Error: {str(e)}", 100)
        time.sleep(3)  # Show error message for a while
        return False, None

def ensure_dependencies():
    """Ensure all required dependencies are available"""
    passed, message = check_system_requirements()
    if not passed:
        error_message = f"""
NetworkMonitor requires additional software to run properly.

{message}

Please install the missing dependencies and try again.

For Npcap (Windows only):
1. Download from https://npcap.com
2. Run the installer as administrator
3. Select "Install Npcap in WinPcap API-compatible Mode"

For Python packages:
Run: pip install -r requirements.txt

See the documentation for detailed setup instructions."""
        logger.error(error_message)
        return False
    return True

def main():
    """Main entry point for the launcher"""
    logger.info("Starting Network Monitor...")
    
    # Display info about execution environment
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Executable: {sys.executable}")
    logger.info(f"Is frozen executable: {getattr(sys, 'frozen', False)}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Log file: {log_file}")
    
    # Import here to avoid circular imports
    try:
        from .splash import run_with_splash, SplashScreen
    except ImportError:
        try:
            from networkmonitor.splash import run_with_splash, SplashScreen
        except ImportError:
            # If splash screen can't be imported, create a minimal version
            class SplashScreen:
                def update_status(self, msg, progress=None):
                    logger.info(msg)
                
                def show(self):
                    pass
                
                def close(self):
                    pass
            
            def run_with_splash(target_function, *args, **kwargs):
                return target_function(*args, **kwargs)
    
    # Create splash screen
    splash = SplashScreen()
    
    try:
        # Check for admin privileges
        if not is_admin():
            logger.warning("Not running with admin privileges, requesting elevation")
            print("Network Monitor requires administrator privileges.")
            print("Attempting to restart with admin privileges...")
            restart_as_admin()
            return 1
        
        splash.show()  # Show splash screen
        logger.info("Running with admin privileges")
        splash.update_status("Checking admin privileges", 10)
        
        # Default settings
        host = '127.0.0.1'
        port = 5000
        
        # Check if port is already in use
        if is_port_in_use(port, host):
            logger.warning(f"Port {port} is already in use. Network Monitor might already be running.")
            splash.update_status(f"Port {port} already in use, trying alternative port", 20)
            
            # Try to find an available port
            for test_port in range(5001, 5020):
                if not is_port_in_use(test_port, host):
                    port = test_port
                    logger.info(f"Selected alternative port: {port}")
                    break
            
            # Check if we found an available port
            if is_port_in_use(port, host):
                message = f"Could not find an available port. Please close any applications using port {port} and try again."
                logger.error(message)
                splash.update_status(message, 100)
                time.sleep(3)
                return 1
        
        url = f"http://{host}:{port}"
        logger.info(f"Network Monitor will be available at {url}")
        
        # Always create a console window to keep the application visible
        console_window = create_console_window()
        
        if console_window:
            # If we have a console window, it will manage the server
            logger.info("Application is running with console window")
            splash.close()  # Close splash since we have the main window
            
            # Run the Tkinter main loop - this keeps the app alive
            if isinstance(console_window, tk.Tk):
                console_window.mainloop()
            
            return 0
        else:
            # No console window, fallback to direct server start
            logger.info("Application is running in background mode (no GUI)")
            # Start server with splash screen
            success, controller = start_server(host, port)
            if not success:
                return 1
                
            # Keep main thread alive while server is running
            try:
                # Keep the main thread alive to prevent the application from exiting
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Application stopped by user")
                if controller:
                    controller.stop_monitoring()
                
            return 0
        
    except KeyboardInterrupt:
        logger.info("Network Monitor stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error launching Network Monitor: {e}")
        traceback.print_exc()
        if 'splash' in locals():
            splash.update_status(f"Error: {str(e)}", 100)
            time.sleep(3)
        return 1
    finally:
        # Make sure splash screen is closed
        if 'splash' in locals() and hasattr(splash, 'close'):
            splash.close()

if __name__ == "__main__":
    sys.exit(main())