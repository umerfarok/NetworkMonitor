import click
import webbrowser
import time
from .server import app
from .monitor import NetworkMonitor

monitor = NetworkMonitor()

@click.group()
def main():
    """Network Monitor CLI"""
    pass

@main.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--no-browser', is_flag=True, help='Do not open browser automatically')
def start(host, port, no_browser):
    """Start the Network Monitor server"""
    click.echo(f"Starting Network Monitor on {host}:{port}")
    
    # Start the monitoring in background
    monitor.start_monitoring()
    
    # Open browser after a short delay
    if not no_browser:
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://{host}:{port}')
        
        from threading import Thread
        Thread(target=open_browser, daemon=True).start()
    
    # Start the Flask server
    app.run(host=host, port=port)

@main.command()
def install():
    """Install required dependencies"""
    from .install import main as install_main
    install_main()

if __name__ == '__main__':
    main()