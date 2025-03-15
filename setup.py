"""
Setup script for NetworkMonitor
Supports both pip installation and py2app for macOS
"""
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

def read_requirements(filename):
    """Read requirements from file"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Get current version
version = '0.1.0'

# Basic setup configuration
setup(
    name="networkmonitor",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "click>=8.0.0",
        "scapy>=2.5.0",
        "psutil>=5.9.0",
        "requests>=2.0.0",
        "ifaddr>=0.1.0",
    ],
    extras_require={
        ':platform_system=="Windows"': [
            "pywin32>=300",
            "wmi>=1.5.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "networkmonitor=networkmonitor.cli:main",
        ],
    },
    python_requires=">=3.9",
)

# Additional configuration for py2app on macOS
if sys.platform == 'darwin' and 'py2app' in sys.argv:
    extra_options = {
        'setup_requires': ['py2app'],
        'app': ['networkmonitor/cli.py'],
        'options': {
            'py2app': {
                'argv_emulation': True,
                'packages': ['networkmonitor'],
                'includes': [
                    'flask',
                    'werkzeug',
                    'jinja2',
                    'click',
                    'scapy',
                    'psutil',
                    'ifaddr',
                    'requests',
                ],
                'resources': ['networkmonitor/web', 'assets'],
                'iconfile': 'assets/icon.icns',
                'plist': {
                    'CFBundleName': 'NetworkMonitor',
                    'CFBundleDisplayName': 'NetworkMonitor',
                    'CFBundleIdentifier': 'com.networkmonitor.app',
                    'CFBundleVersion': version,
                    'CFBundleShortVersionString': version,
                    'LSMinimumSystemVersion': '10.13',
                    'NSHighResolutionCapable': True,
                    'NSRequiresAquaSystemAppearance': False,
                }
            }
        }
    }
    setup_config.update(extra_options)

setup(**setup_config)
