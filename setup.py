from setuptools import setup, find_packages
import platform

# Base dependencies
install_requires = [
    "flask>=2.0.1",
    "flask-cors>=3.0.10",
    "psutil>=5.8.0",
    "scapy>=2.4.5",
    "requests>=2.26.0",
    "click>=8.0.0",
    "ifaddr>=0.1.7",
]

# Add Windows-specific dependencies
if platform.system() == "Windows":
    install_requires.extend([
        "pywin32>=305",
        "wmi>=1.5.1",
    ])

setup(
    name="networkmonitor",
    version="0.1.0",
    description="Network monitoring and bandwidth control tool",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'networkmonitor=networkmonitor.cli:main',
        ],
    },
    python_requires=">=3.8",
)