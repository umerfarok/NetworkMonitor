from setuptools import setup, find_packages

setup(
    name="netmonitor",  # Changed back to netmonitor
    version="0.1.0",
    packages=find_packages(),  # This will find all packages
    include_package_data=True,
    install_requires=[
        "flask>=2.0.1",
        "flask-cors>=3.0.10",
        "psutil>=5.8.0",
        "scapy>=2.4.5",
        "mitmproxy>=9.0.1",
        "requests>=2.26.0",
        "click>=8.0.0",
        "ifaddr>=0.1.7",
        "wmi>=1.5.1; platform_system=='Windows'",
        "pywin32>=305; platform_system=='Windows'"
    ],
    entry_points={
        "console_scripts": [
            "netmonitor=netmonitor.cli:main"  # Changed back to netmonitor
        ],
    },
    python_requires=">=3.8",
)