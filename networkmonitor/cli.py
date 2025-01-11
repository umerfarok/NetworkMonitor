import click
import webbrowser
import time
from pathlib import Path
import sys
import os
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

if __name__ == '__main__':
    main()