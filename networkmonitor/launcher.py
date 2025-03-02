#!/usr/bin/env python
"""
Network Monitor Application Launcher
This script launches both the backend server and opens the web interface
"""
import sys
import os
import time
import logging
import threading
import webbrowser
import platform
import subprocess
import signal
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor_launcher.log'),
        logging.StreamHandler()
    ]
)

def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_backend(host='127.0.0.1', port=5000):
    """Start the backend server"""
    from .server import create_app
    from .monitor import NetworkController

    # Initialize controller
    controller = NetworkController()
    
    try:
        # Start monitoring
        controller.start_monitoring()
        logging.info("Network monitoring started")
        
        # Create and start Flask app
        app = create_app()
        app.run(host=host, port=port)
    except Exception as e:
        logging.error(f"Error starting backend: {e}")
        if controller:
            controller.stop_monitoring()
        raise

def open_browser(url):
    """Open web browser after a short delay"""
    def _open_browser():
        time.sleep(2)  # Wait for server to start
        webbrowser.open(url)
    
    browser_thread = threading.Thread(target=_open_browser)
    browser_thread.daemon = True
    browser_thread.start()

def main():
    """Main entry point for the launcher"""
    logging.info("Starting Network Monitor...")
    
    # Default settings
    host = '127.0.0.1'
    port = 5000
    
    # Check if port is already in use
    if is_port_in_use(port):
        logging.warning(f"Port {port} is already in use. Network Monitor might already be running.")
        response = input(f"Port {port} is already in use. Try a different port? (Y/n): ")
        if response.lower() != 'n':
            port = 5001
            while is_port_in_use(port) and port < 5010:
                port += 1
    
    url = f"http://{host}:{port}"
    logging.info(f"Network Monitor will be available at {url}")
    
    # Open web browser
    open_browser(url)
    
    try:
        # Start backend server
        start_backend(host, port)
    except KeyboardInterrupt:
        logging.info("Network Monitor stopped by user")
    except Exception as e:
        logging.error(f"Error running Network Monitor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())