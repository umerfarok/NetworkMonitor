# netmon/cli.py
import click
import webbrowser
from .server import app
import threading
import os

@click.group()
def main():
    """Network Monitor CLI"""
    pass

@main.command()
@click.option('--port', default=5000, help='Port to run the server on')
def start(port):
    """Start the Network Monitor server"""
    def open_browser():
        webbrowser.open(f'http://localhost:{port}')

    threading.Timer(1.5, open_browser).start()
    try:
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)

if __name__ == '__main__':
    main()