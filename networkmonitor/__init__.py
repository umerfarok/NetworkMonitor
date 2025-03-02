"""Network Monitor Package"""
import logging
import sys
import platform
import os
from pathlib import Path

__version__ = "0.1.0"

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Npcap early if on Windows
if platform.system() == "Windows":
    try:
        logger.info("Initializing Npcap support")
        from .npcap_helper import initialize_npcap, get_npcap_info
        
        npcap_initialized = initialize_npcap()
        if npcap_initialized:
            npcap_info = get_npcap_info()
            logger.info(f"Npcap initialized successfully: {npcap_info}")
        else:
            logger.warning("Failed to initialize Npcap - some features may not work correctly")
    except Exception as e:
        logger.error(f"Error during Npcap initialization: {e}")

# Import core dependencies after Npcap is initialized
try:
    # Core dependencies check
    import flask
    import click
    import scapy
    import psutil
    
    # OS-specific dependencies
    if platform.system() == "Windows":
        import wmi
        import win32com
    elif platform.system() == "Linux":
        try:
            import iptc
        except ImportError:
            logger.warning("python-iptables not installed. Some Linux-specific features may not work.")
    elif platform.system() == "Darwin":  # macOS
        try:
            import netifaces
        except ImportError:
            logger.warning("netifaces not installed. Some macOS-specific features may not work.")
            
except ImportError as e:
    logger.error(f"Missing dependency: {e}")
    # Don't exit here - let the dependency_check module handle this properly
    # This allows the app to show a proper error page to the user