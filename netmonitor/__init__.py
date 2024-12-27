# netmonitor/__init__.py
"""Network monitoring package"""

from .cli import main
from .server import app
from .monitor import NetworkMonitor

__version__ = "0.1.0"
__all__ = ['main', 'app', 'NetworkMonitor']