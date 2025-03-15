"""
Command-line interface for NetworkMonitor
"""
import sys
import click
from .launcher import start_server
from .dependency_check import check_system_requirements

@click.group()
def cli():
    """NetworkMonitor - Network monitoring and analysis tool"""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind the server to')
@click.option('--port', default=5000, help='Port to run the server on')
@click.option('--check-only', is_flag=True, help='Only check dependencies without starting server')
def start(host, port, check_only):
    """Start the NetworkMonitor server"""
    # Check dependencies first
    ok, message = check_system_requirements()
    if not ok:
        click.echo(f"Error: {message}", err=True)
        sys.exit(1)
    
    if check_only:
        click.echo("All system requirements met!")
        sys.exit(0)
    
    # Start the server
    click.echo(f"Starting NetworkMonitor server on {host}:{port}")
    success, controller = start_server(host=host, port=port)
    
    if not success:
        click.echo("Failed to start server", err=True)
        sys.exit(1)
    
    try:
        # Keep the server running
        controller.wait_for_shutdown()
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
        controller.stop_monitoring()

@cli.command()
def check():
    """Check system requirements and dependencies"""
    ok, message = check_system_requirements()
    if ok:
        click.echo("All system requirements met!")
    else:
        click.echo(f"Error: {message}", err=True)
        sys.exit(1)

@cli.command()
def version():
    """Show version information"""
    from . import __version__
    click.echo(f"NetworkMonitor v{__version__}")

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 