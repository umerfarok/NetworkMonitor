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
from datetime import datetime, timedelta
import threading
import queue
import netifaces
import requests

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

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('networkmonitor.log'),
                logging.StreamHandler()
            ]
        )

    def get_wifi_interfaces(self) -> List[str]:
        """Get list of WiFi interfaces"""
        wifi_interfaces = []
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
                if "Name" in output:
                    for line in output.split('\n'):
                        if "Name" in line:
                            wifi_interfaces.append(line.split(":")[1].strip())
            else:  # Linux/MacOS
                interfaces = netifaces.interfaces()
                for interface in interfaces:
                    if interface.startswith(('wlan', 'wifi', 'wi-fi', 'wl')):
                        wifi_interfaces.append(interface)
        except Exception as e:
            logging.error(f"Error getting WiFi interfaces: {e}")
        return wifi_interfaces

    def get_connected_devices(self, interface: str = None) -> List[Device]:
        """Scan network for connected devices"""
        try:
            if not interface:
                interface = self.get_default_interface()

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

    def get_default_interface(self) -> str:
        """Get default network interface"""
        try:
            if self.os_type == "Windows":
                # Get default interface on Windows
                result = subprocess.check_output("ipconfig", shell=True).decode()
                for line in result.split('\n'):
                    if "Wireless LAN adapter" in line:
                        return line.split("adapter")[-1].strip().strip(':')
            else:
                # Get default interface on Linux/MacOS
                gateways = netifaces.gateways()
                if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                    return gateways['default'][netifaces.AF_INET][1]
        except Exception as e:
            logging.error(f"Error getting default interface: {e}")
        return None

    def get_interface_ip(self, interface: str) -> str:
        """Get IP address of specified interface"""
        try:
            if self.os_type == "Windows":
                output = subprocess.check_output(f"ipconfig", shell=True).decode()
                current_adapter = None
                for line in output.split('\n'):
                    if interface in line:
                        current_adapter = interface
                    elif current_adapter and "IPv4 Address" in line:
                        return line.split(":")[-1].strip()
            else:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
        except Exception as e:
            logging.error(f"Error getting interface IP: {e}")
        return None

    def get_subnet(self, ip: str) -> str:
        """Get subnet from IP address"""
        try:
            # Simple subnet calculation - assumes /24 network
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

            # Format MAC address and get first 6 characters (OUI)
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
                output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
                if mac.replace(':', '-').upper() in output:
                    for line in output.split('\n'):
                        if "Signal" in line:
                            return int(line.split(':')[1].strip().strip('%'))
            else:  # Linux
                output = subprocess.check_output(f"iwconfig", shell=True).decode()
                if mac.upper() in output:
                    for line in output.split('\n'):
                        if "Signal level" in line:
                            return int(line.split('=')[1].split()[0])
        except:
            pass
        return None

    def guess_device_type(self, hostname: str, vendor: str) -> str:
        """Guess device type based on hostname and vendor"""
        if not hostname and not vendor:
            return "Unknown"

        hostname = (hostname or "").lower()
        vendor = (vendor or "").lower()

        # Define device type patterns
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
                # Calculate current speeds
                self._update_device_speeds()
                time.sleep(5)  # Scan every 5 seconds
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def _update_device_speeds(self):
        """Update current speeds for all devices"""
        try:
            # Get network interface statistics
            stats = psutil.net_io_counters(pernic=True)
            for ip, device in self.devices.items():
                if device.status == "active":
                    # Calculate speed based on bytes sent/received
                    # This is a simplified calculation - you might want to implement
                    # more sophisticated speed tracking
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

    def limit_bandwidth(self, ip: str, limit: float) -> bool:
        try:
            if self.os_type == "Linux":
                self._limit_linux(ip, limit)
            elif self.os_type == "Darwin":
                self._limit_macos(ip, limit)
            elif self.os_type == "Windows":
                self._limit_windows(ip, limit)
                
            # Update device speed limit
            if ip in self.devices:
                self.devices[ip].speed_limit = limit
                
            return True
        except Exception as e:
            logging.error(f"Bandwidth limit failed: {str(e)}")
            return False

    def _limit_linux(self, ip: str, limit: float):
        commands = [
            f"tc qdisc add dev {self.interface} root handle 1: htb",
            f"tc class add dev {self.interface} parent 1: classid 1:1 htb rate {limit}mbit",
            f"tc filter add dev {self.interface} protocol ip parent 1: prio 1 u32 match ip dst {ip} flowid 1:1"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)

    def _limit_macos(self, ip: str, limit: float):
        commands = [
            "pfctl -e",
            f"echo 'dummynet in proto tcp from any to {ip} pipe 1' | pfctl -f -",
            f"dnctl pipe 1 config bw {limit}Mbit/s"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)

    def _limit_windows(self, ip: str, limit: float):
        # Implement Windows-specific bandwidth limiting
        interface = self.interface
        commands = [
            f"netsh interface ipv4 set subinterface \"{interface}\" mtu={int(limit * 1000)} store=persistent",
            f"netsh interface ipv4 set subinterface \"{interface}\" mtu={int(limit * 1000)}"
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)

    def remove_limit(self, ip: str) -> bool:
        try:
            # Remove speed limit from device
            if ip in self.devices:
                self.devices[ip].speed_limit = None
                
            if self.os_type == "Linux":
                subprocess.run(f"tc qdisc del dev {self.interface} root", shell=True, check=True)
            elif self.os_type == "Darwin":
                subprocess.run("pfctl -F all -f /etc/pf.conf", shell=True, check=True)
            elif self.os_type == "Windows":
                interface = self.interface
                subprocess.run(f"netsh interface ipv4 set subinterface \"{interface}\" mtu=1500 store=persistent", shell=True, check=True)
                subprocess.run(f"netsh interface ipv4 set subinterface \"{interface}\" mtu=1500", shell=True, check=True)
                
            return True
        except Exception as e:
            logging.error(f"Remove limit failed: {str(e)}")
            return False

    def _get_interface_stats(self, interface: str) -> Dict:
        try:
            stats = psutil.net_io_counters(pernic=True)[interface]
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errin': stats.errin,
                'errout': stats.errout,
                'dropin': stats.dropin,
                'dropout': stats.dropout
            }
        except:
            return {}

    def _get_hostname(self, ip: str) -> Optional[str]:
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None

    def _get_vendor(self, mac: str) -> Optional[str]:
        try:
            # First 6 characters of MAC address represent the vendor
            vendor_prefix = mac[:8].upper().replace(':', '')
            # This would normally query a MAC address vendor database
            return "Unknown Vendor"
        except:
            return None

    def _get_subnet(self, interface: str) -> Optional[str]:
        adapters = ifaddr.get_adapters()
        for adapter in adapters:
            if adapter.nice_name == interface:
                for ip in adapter.ips:
                    if isinstance(ip.ip, str):
                        return ip.ip
        return None