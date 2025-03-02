import click
import webbrowser
import time
from pathlib import Path
import sys
import os
import platform
from .server import create_app
from .monitor import NetworkController

def get_controller(): 
    """Get or create NetworkController instance"""
    if not hasattr(get_controller, 'instance'):
        get_controller.instance = NetworkController()
    return get_controller.instance

@click.group()
def main():
    """Network Monitor CLI"""
    pass

@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--no-browser', is_flag=True, help='Do not open browser automatically')
def start(host, port, no_browser):
    """Start the Network Monitor server"""
    # Create Flask app
    app = create_app()
    controller = get_controller()
    
    click.echo(f"Starting Network Monitor on http://{host}:{port}")
    
    # Start the monitoring in background
    try:
        controller.start_monitoring()
        click.echo("Network monitoring started successfully")
    except Exception as e:
        click.echo(f"Error starting monitoring: {e}", err=True)
        sys.exit(1)
    
    # Open browser after a short delay
    if not no_browser:
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://{host}:{port}')
        
        from threading import Thread
        Thread(target=open_browser, daemon=True).start()
    
    # Start the Flask server
    try:
        app.run(host=host, port=port)
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        controller.stop_monitoring()
        sys.exit(1)

@main.command()
def install():
    """Install required dependencies"""
    from .install import main as install_main
    install_main()

@main.command()
def stop():
    """Stop the Network Monitor server and monitoring"""
    controller = get_controller()
    controller.stop_monitoring()
    click.echo("Network Monitor stopped")

@main.command()
def status():
    """Check the status of Network Monitor"""
    controller = get_controller()
    if controller.monitoring_thread and controller.monitoring_thread.is_alive():
        click.echo("Network Monitor is running")
    else:
        click.echo("Network Monitor is not running")

@main.command()
def launch():
    """Launch the Network Monitor application (GUI mode)"""
    try:
        from .launcher import main as launch_main
        sys.exit(launch_main())
    except ImportError:
        click.echo("Launcher module not found. Using standard CLI.")
        start.callback(host='127.0.0.1', port=5000, no_browser=False)

def check_admin_privileges():
    """Check if running with admin/root privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def startup_checks():
    """Perform startup checks before running"""
    # Check for admin privileges
    if not check_admin_privileges():
        click.echo("WARNING: Network Monitor requires administrator privileges for some features.")
        click.echo("Consider running this application as Administrator (Windows) or with sudo (Linux/Mac).")
    
    # Check Python version
    if sys.version_info < (3, 8):
        click.echo("ERROR: Python 3.8 or higher is required.")
        sys.exit(1)
    
    return True

# Entry point with startup checks
def entry_point():
    """Entry point for the application with startup checks"""
    startup_checks()
    
    # If no arguments, default to GUI launch
    if len(sys.argv) == 1:
        sys.argv.append('launch')
    
    # Run the CLI
    main()

if __name__ == '__main__':
    entry_point()