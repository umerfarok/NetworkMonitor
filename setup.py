from setuptools import setup, find_packages
import sys

install_requires = [
    "flask>=2.0.1,<3.0.0",
    "flask-cors>=3.0.10,<4.0.0",
    "psutil>=5.9.0,<6.0.0",
    "scapy>=2.5.0,<3.0.0",
    "requests>=2.28.0,<3.0.0",
    "click>=8.0.0,<9.0.0",
    "ifaddr>=0.1.7,<0.2.0",
    "python-dateutil>=2.8.2,<3.0.0",
    "werkzeug>=2.0.0,<3.0.0",
    "typing-extensions>=4.0.0,<5.0.0",
]

extras_require = {
    "windows": [
        "pywin32>=305",
        "wmi>=1.5.1",
        "comtypes>=1.1.14",
    ],
    "linux": [
        "python-iptables>=1.0.0",
        "netifaces>=0.11.0",
    ],
    "macos": [
        "pyobjc-framework-SystemConfiguration>=8.0",
        "netifaces>=0.11.0",
    ],
}

# Auto-include OS-specific dependencies
if sys.platform.startswith("win"):
    install_requires.extend(extras_require["windows"])
elif sys.platform.startswith("linux"):
    install_requires.extend(extras_require["linux"])
elif sys.platform.startswith("darwin"):
    install_requires.extend(extras_require["macos"])

setup(
    name="networkmonitor",
    version="0.1.0",
    description="Advanced network monitoring and control tool",
    author="Network Monitor Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,  # Allows manual OS-specific installs
    entry_points={
        'console_scripts': [
            'networkmonitor=networkmonitor.cli:entry_point',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Networking :: Monitoring",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
)
