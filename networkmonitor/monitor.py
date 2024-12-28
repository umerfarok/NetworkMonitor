import platform
import psutil
import subprocess
import logging
import time
import socket
from scapy.all import ARP, Ether, srp
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import ifaddr  # Using ifaddr instead of netifaces
import requests
import threading
import queue
import os  # Add this import

@dataclass
class Device:
    ip: str
    mac: str
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    signal_strength: Optional[int] = None  # RSSI value in dBm
    connection_type: str = "WiFi"
    status: str = "active"
    speed_limit: Optional[float] = None
    current_speed: float = 0.0
    last_seen: datetime = None

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.now()

class NetworkMonitor:
    def __init__(self):
        self.os_type = platform.system()
        self.devices: Dict[str, Device] = {}
        self.mac_vendor_cache: Dict[str, str] = {}
        self.setup_logging()
        self._stop_event = threading.Event()
        self.monitoring_thread = None
        self.speed_tracking = {}
        self.device_groups = {"unlimited": [], "limited": []}
        self.speed_update_queue = queue.Queue()
        
        # Set system commands based on OS
        if self.os_type == "Windows":
            self.ipconfig_path = self._get_windows_command_path("ipconfig.exe")
            self.netsh_path = self._get_windows_command_path("netsh.exe")

    def _get_windows_command_path(self, command):
        """Get full path for Windows system commands"""
        system32 = os.path.join(os.environ['SystemRoot'], 'System32')
        command_path = os.path.join(system32, command)
        return command_path if os.path.exists(command_path) else command

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('networkmonitor.log'),
                logging.StreamHandler()
            ]
        )

    def get_interfaces(self) -> List[Dict]:
        """Get all network interfaces"""
        interfaces = []
        adapters = ifaddr.get_adapters()
        
        for adapter in adapters:
            for ip in adapter.ips:
                # Only handle IPv4
                if isinstance(ip.ip, str):
                    interfaces.append({
                        'name': adapter.nice_name,
                        'ip': ip.ip,
                        'network_mask': ip.network_bits if hasattr(ip, 'network_bits') else 24,
                        'stats': self._get_interface_stats(adapter.nice_name)
                    })
        return interfaces

    def get_wifi_interfaces(self) -> List[str]:
        """Get list of WiFi interfaces"""
        wifi_interfaces = []
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output([self.netsh_path, "wlan", "show", "interfaces"], 
                                              text=True, 
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                if "Name" in output:
                    for line in output.split('\n'):
                        if "Name" in line:
                            wifi_interfaces.append(line.split(":")[1].strip())
            else:  # Linux/MacOS
                interfaces = self.get_interfaces()
                for interface in interfaces:
                    if interface['name'].startswith(('wlan', 'wifi', 'wi-fi', 'wl')):
                        wifi_interfaces.append(interface['name'])
        except Exception as e:
            logging.error(f"Error getting WiFi interfaces: {e}")
        return wifi_interfaces

    def get_default_interface(self) -> str:
        """Get default network interface"""
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output([self.ipconfig_path], 
                                              text=True, 
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                for line in output.split('\n'):
                    if "Wireless LAN adapter" in line:
                        return line.split("adapter")[-1].strip().strip(':')
                    # Fallback to first Ethernet adapter if no wireless
                    elif "Ethernet adapter" in line:
                        return line.split("adapter")[-1].strip().strip(':')
            else:
                # Get default interface on Linux/MacOS using ifaddr
                adapters = ifaddr.get_adapters()
                for adapter in adapters:
                    for ip in adapter.ips:
                        if isinstance(ip.ip, str) and not ip.ip.startswith('127.'):
                            return adapter.nice_name
        except Exception as e:
            logging.error(f"Error getting default interface: {e}")
        return None

    def get_interface_ip(self, interface: str) -> str:
        """Get IP address of specified interface"""
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output([self.ipconfig_path], 
                                              text=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                current_adapter = None
                for line in output.split('\n'):
                    if interface in line:
                        current_adapter = interface
                    elif current_adapter and "IPv4 Address" in line:
                        return line.split(":")[-1].strip().strip('(Preferred)')
            else:
                addrs = ifaddr.get_adapters()
                for adapter in addrs:
                    if adapter.nice_name == interface:
                        for ip in adapter.ips:
                            if isinstance(ip.ip, str):
                                return ip.ip
        except Exception as e:
            logging.error(f"Error getting interface IP: {e}")
        return None

    def get_connected_devices(self, interface: str = None) -> List[Device]:
        """Scan network for connected devices"""
        try:
            if not interface:
                interface = self.get_default_interface()
            
            if not interface:
                raise Exception("No valid network interface found")

            # Get subnet for scanning
            ip = self.get_interface_ip(interface)
            if not ip:
                raise Exception(f"Could not get IP for interface {interface}")

            subnet = self.get_subnet(ip)
            logging.info(f"Scanning subnet: {subnet}/24")

            # Perform ARP scan
            arp = ARP(pdst=f"{subnet}/24")
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            result = srp(packet, timeout=3, verbose=0, iface=interface)[0]
            
            current_time = datetime.now()
            
            for sent, received in result:
                ip_addr = received.psrc
                mac_addr = received.hwsrc.upper()
                
                # Get device details
                hostname = self.get_hostname(ip_addr)
                vendor = self.get_vendor(mac_addr)
                signal_strength = self.get_signal_strength(mac_addr)
                device_type = self.guess_device_type(hostname, vendor)
                
                device = Device(
                    ip=ip_addr,
                    mac=mac_addr,
                    hostname=hostname,
                    vendor=vendor,
                    device_type=device_type,
                    signal_strength=signal_strength,
                    last_seen=current_time
                )
                
                self.devices[ip_addr] = device

            # Update status of devices not seen in this scan
            for ip, device in self.devices.items():
                if device.last_seen != current_time:
                    device.status = "inactive"

            return list(self.devices.values())

        except Exception as e:
            logging.error(f"Error scanning network: {e}")
            return []

    def get_subnet(self, ip: str) -> str:
        """Get subnet from IP address"""
        try:
            return '.'.join(ip.split('.')[:-1]) + '.0'
        except Exception as e:
            logging.error(f"Error getting subnet: {e}")
            return None

    def get_hostname(self, ip: str) -> Optional[str]:
        """Get hostname for IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return None

    def get_vendor(self, mac: str) -> Optional[str]:
        """Get vendor from MAC address using macvendors.com API"""
        try:
            if mac in self.mac_vendor_cache:
                return self.mac_vendor_cache[mac]

            mac = mac.replace(':', '').upper()[:6]
            response = requests.get(f'https://api.macvendors.com/{mac}')
            
            if response.status_code == 200:
                vendor = response.text
                self.mac_vendor_cache[mac] = vendor
                return vendor
        except:
            pass
        return None

    def get_signal_strength(self, mac: str) -> Optional[int]:
        """Get WiFi signal strength for device"""
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output([self.netsh_path, "wlan", "show", "interfaces"], 
                                              text=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                if mac.replace(':', '-').upper() in output:
                    for line in output.split('\n'):
                        if "Signal" in line:
                            return int(line.split(':')[1].strip().strip('%'))
        except:
            pass
        return None

    def guess_device_type(self, hostname: str, vendor: str) -> str:
        """Guess device type based on hostname and vendor"""
        if not hostname and not vendor:
            return "Unknown"

        hostname = (hostname or "").lower()
        vendor = (vendor or "").lower()

        patterns = {
            "smartphone": ["iphone", "android", "phone", "samsung", "huawei", "xiaomi"],
            "laptop": ["laptop", "macbook", "notebook", "dell", "lenovo", "hp", "asus"],
            "tablet": ["ipad", "tablet", "kindle"],
            "smart tv": ["tv", "roku", "firestick", "chromecast", "samsung tv", "lg tv"],
            "gaming": ["playstation", "xbox", "nintendo", "ps4", "ps5"],
            "iot": ["camera", "thermostat", "doorbell", "nest", "ring", "echo", "alexa"],
            "desktop": ["desktop", "pc", "imac", "workstation"]
        }

        for device_type, keywords in patterns.items():
            if any(keyword in hostname or keyword in vendor for keyword in keywords):
                return device_type.title()

        return "Unknown"

    def start_monitoring(self):
        """Start continuous device monitoring"""
        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self._stop_event.clear()
            self.monitoring_thread = threading.Thread(target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop device monitoring"""
        self._stop_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _monitor_loop(self):
        """Background monitoring loop"""
        while not self._stop_event.is_set():
            try:
                self.get_connected_devices()
                self._update_device_speeds()
                time.sleep(5)  # Scan every 5 seconds
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _update_device_speeds(self):
        """Update current speeds for all devices"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            for ip, device in self.devices.items():
                if device.status == "active":
                    total_bytes = sum(s.bytes_sent + s.bytes_recv for s in stats.values())
                    device.current_speed = total_bytes / 1_000_000  # Convert to Mbps
        except Exception as e:
            logging.error(f"Error updating device speeds: {e}")

    def get_device_details(self, ip: str) -> Optional[Dict]:
        """Get detailed information about a specific device"""
        device = self.devices.get(ip)
        if device:
            return {
                "ip": device.ip,
                "mac": device.mac,
                "hostname": device.hostname,
                "vendor": device.vendor,
                "device_type": device.device_type,
                "signal_strength": device.signal_strength,
                "connection_type": device.connection_type,
                "status": device.status,
                "current_speed": device.current_speed,
                "speed_limit": device.speed_limit,
                "last_seen": device.last_seen.isoformat()
            }
        return None

    def get_network_summary(self) -> Dict:
        """Get summary of network devices"""
        active_devices = [d for d in self.devices.values() if d.status == "active"]
        return {
            "total_devices": len(self.devices),
            "active_devices": len(active_devices),
            "device_types": {
                device_type: len([d for d in active_devices if d.device_type == device_type])
                for device_type in set(d.device_type for d in active_devices)
            },
            "total_bandwidth": sum(d.current_speed for d in active_devices)
        }