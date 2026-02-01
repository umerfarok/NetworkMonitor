"""
Splash screen module for Network Monitor
Displays a GUI splash screen during startup to indicate status to the user
"""
import os
import sys
import time
import threading
import webbrowser
import logging
import tkinter as tk
from tkinter import ttk
from pathlib import Path

logger = logging.getLogger(__name__)

class SplashScreen:
    """Displays a splash screen during application startup"""
    
    def __init__(self, title="Network Monitor", width=500, height=300):
        """Initialize the splash screen"""
        self.width = width
        self.height = height
        self.title = title
        self.root = None
        self.progress = None
        self.status_var = None
        self.progress_var = None
        self._is_running = False
        
    def show(self):
        """Show the splash screen"""
        self.root = tk.Tk()
        self.root.title(self.title)
        
        # Set window properties
        self.root.overrideredirect(True)  # No window decorations
        self.root.attributes("-topmost", True)
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Apply styling
        self.root.configure(bg="#f0f0f0")
         
        # Create frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        title_label = ttk.Label(main_frame, text=self.title, font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Add subtitle
        subtitle = ttk.Label(main_frame, text="Starting services...", font=("Arial", 10))
        subtitle.pack(pady=5)
        
        # Add status message
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9))
        status_label.pack(pady=10)
        
        # Add progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode="determinate",
            variable=self.progress_var
        )
        self.progress.pack(pady=10, fill=tk.X)
        
        # Add details about admin privileges
        admin_text = "Running with administrator privileges" if self._check_admin() else "Not running with admin privileges (limited functionality)"
        admin_label = ttk.Label(main_frame, text=admin_text, font=("Arial", 8))
        admin_label.pack(pady=5)
        
        # Add close button
        close_button = ttk.Button(main_frame, text="Cancel", command=self.close)
        close_button.pack(pady=10)
        
        # Add version info
        try:
            from . import __version__
            version_text = f"Version {__version__}"
        except (ImportError, AttributeError):
            version_text = "Development Version"
        
        version_label = ttk.Label(main_frame, text=version_text, font=("Arial", 8))
        version_label.pack(side=tk.BOTTOM, pady=5)
        
        self._is_running = True
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        
        # Update the UI
        self.root.update()
    
    def update_status(self, message, progress=None):
        """Update the status message and optionally the progress bar"""
        if not self._is_running or not self.root:
            return
            
        try:
            self.status_var.set(message)
            if progress is not None:
                self.progress_var.set(progress)
            self.root.update()
        except (tk.TclError, RuntimeError):
            # Window might have been closed
            self._is_running = False
    
    def close(self):
        """Close the splash screen"""
        if self.root:
            self._is_running = False
            try:
                self.root.destroy()
            except tk.TclError:
                # Already destroyed
                pass
    
    def _check_admin(self):
        """Check if running with admin privileges"""
        try:
            import platform
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

def run_with_splash(target_function, *args, **kwargs):
    """
    Run a function with a splash screen
    
    Args:
        target_function: The function to run
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        The result of the target function
    """
    splash = SplashScreen()
    splash.show()
    
    result = None
    exception = None
    
    def run_target():
        nonlocal result, exception
        try:
            # Set up progress updates
            progress_steps = [
                ("Checking dependencies...", 10),
                ("Initializing network services...", 20),
                ("Starting monitoring engine...", 40),
                ("Connecting to network interfaces...", 60),
                ("Starting web server...", 80),
                ("Opening web interface...", 90),
                ("Ready", 100)
            ]
            
            for message, progress in progress_steps:
                splash.update_status(message, progress)
                time.sleep(0.5)  # Simulate work being done
                
            result = target_function(*args, **kwargs)
        except Exception as e:
            exception = e
            splash.update_status(f"Error: {str(e)}", 100)
            time.sleep(3)  # Show error for a few seconds
        finally:
            # Only close splash if we're successful or after showing error
            if exception is None or time.time() - start_time > 3:
                splash.close()
    
    start_time = time.time()
    
    # Run the target function in a separate thread
    thread = threading.Thread(target=run_target)
    thread.daemon = True
    thread.start()
    
    # Run the splash screen main loop
    try:
        splash.root.mainloop()
    except tk.TclError:
        # Already destroyed
        pass
    
    # If there was an exception, raise it
    if exception:
        raise exception
    
    return result

if __name__ == "__main__":
    # Example usage
    def example_function():
        time.sleep(5)  # Simulate work
        return "Done!"
        
    result = run_with_splash(example_function)
    print(result)