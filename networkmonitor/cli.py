"""
Network Monitor CLI Entry Point
This module provides the command-line interface for NetworkMonitor
"""
import os
import sys
import logging
import platform
import click
from pathlib import Path

# Fix import issues when running as executable or directly
if __package__ is None or __package__ == '':
    # Add parent directory to path for direct script execution
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from networkmonitor import dependency_check
    from networkmonitor.dependency_check import DependencyChecker
    from networkmonitor.launcher import main as launcher_main
else:
    # Normal relative imports for package imports
    from . import dependency_check
    from .dependency_check import DependencyChecker
    from .launcher import main as launcher_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@click.group(invoke_without_command=True)
@click.version_option(package_name='networkmonitor')
@click.pass_context
def cli(ctx):
    """Network Monitor - A tool for monitoring and protecting your network."""
    # If no subcommand is specified, run the GUI command
    if ctx.invoked_subcommand is None:
        logger.info("No command specified, starting GUI")
        ctx.invoke(gui)

@cli.command('gui')
@click.option('--port', default=5000, help='Port to run the server on')
@click.option('--host', default='127.0.0.1', help='Host to bind the server to')
def gui(port, host):
    """Start the Network Monitor GUI."""
    # Before launching, check dependencies
    try:
        checker = DependencyChecker()
        all_ok, missing, warnings = checker.check_all_dependencies()
        
        if missing:
            click.echo("Missing required dependencies:")
            for dep in missing:
                click.echo(f"- {dep}")
            
            click.echo("\nPlease install missing dependencies:")
            instructions = checker.get_installation_instructions()
            for dep in missing:
                if dep in instructions:
                    click.echo(f"\n{dep}:")
                    click.echo(instructions[dep])
            
            if not click.confirm("Continue anyway?"):
                return
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        # Continue anyway to show the UI with error message
    
    # Launch the GUI
    launcher_main()

@cli.command('check')
def check_dependencies():
    """Check if all dependencies are installed."""
    click.echo("Checking dependencies...")
    checker = DependencyChecker()
    all_ok, missing, warnings = checker.check_all_dependencies()
    
    if all_ok:
        click.echo("✅ All required dependencies are installed.")
    else:
        click.echo("❌ Some dependencies are missing:")
        for dep in missing:
            click.echo(f"- {dep}")
    
    if warnings:
        click.echo("\nWarnings:")
        for warning in warnings:
            click.echo(f"- {warning}")

@cli.command('install')
def install():
    """Install required system dependencies."""
    if platform.system() == 'Windows':
        # Windows needs admin privileges
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            click.echo("❌ This command needs to be run as Administrator.")
            return
    
    click.echo("Installing dependencies...")
    
    # Import the install module and run installation
    try:
        # Try to find the install script
        install_script = Path(__file__).parent.parent / "install.py"
        if install_script.exists():
            # Run the install script
            sys.path.insert(0, str(install_script.parent))
            import install
            result = install.main()
            if result == 0:
                click.echo("✅ Dependencies installed successfully.")
            else:
                click.echo("❌ Failed to install dependencies.")
        else:
            click.echo("❌ Installation script not found.")
    except Exception as e:
        click.echo(f"❌ Error during installation: {e}")

def entry_point():
    """Entry point for console_script."""
    try:
        cli()
    except Exception as e:
        logger.exception(f"Error in CLI: {e}")
        click.echo(f"Error: {e}", err=True)
        
        # Keep the window open if there's an error
        if getattr(sys, 'frozen', False):
            click.echo("\nPress Enter to exit...")
            input()
        sys.exit(1)

if __name__ == '__main__':
    entry_point()