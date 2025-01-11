from setuptools import setup, find_packages
import platform

install_requires = [
    "flask>=2.0.1,<3.0.0",
    "flask-cors>=3.0.10,<4.0.0",
    "psutil>=5.8.0,<6.0.0",
    "scapy>=2.4.5,<3.0.0",
    "requests>=2.26.0,<3.0.0",
    "click>=8.0.0,<9.0.0",
    "ifaddr>=0.1.7,<0.2.0",
    "python-dateutil>=2.8.2,<3.0.0",
    "werkzeug>=2.0.0,<3.0.0",
    "typing-extensions>=4.0.0,<5.0.0",
]

# Windows-specific dependencies
if platform.system() == "Windows":
    install_requires.extend([
        "pywin32>=305",
        "wmi>=1.5.1",
    ])

# Linux-specific dependencies
elif platform.system() == "Linux":
    install_requires.extend([
        "python-iptables>=1.0.0",
        "netifaces>=0.11.0",
    ])

setup(
    name="networkmonitor",
    version="0.1.0",
    description="Advanced network monitoring and control tool",
    author="Your Name",
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