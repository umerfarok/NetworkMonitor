"""Network Monitor Package"""
try:
    from .monitor import NetworkController
    from .server import create_app
    from .cli import cli

    __version__ = "0.1.0"
    __all__ = ["NetworkController", "create_app", "cli"]
except ImportError as e:
    print(f"Error importing dependencies: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install psutil flask flask-cors scapy-python3 requests click ifaddr pywin32")