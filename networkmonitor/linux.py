"""
Linux/Ubuntu-specific network monitoring functionality
"""
import logging
import subprocess
import re
import socket
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LinuxNetworkMonitor:
    """Linux specific network functionality"""
    def __init__(self):
        self.is_admin = os.geteuid() == 0
        if not self.is_admin:
            logger.warning("Not running with root privileges - some features may be limited")
    
    def get_interfaces(self) -> List[Dict]:
        """Get all network interfaces"""
        interfaces = []
        try:
            # Use ip addr command to list interfaces
            output = subprocess.check_output(["ip", "addr"], text=True)
            
            current_interface = None
            for line in output.splitlines():
                line = line.strip()
                
                # New interface definition starts with a number
                if line[0].isdigit() and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        interface_name = parts[1].strip().split()[0]
                        current_interface = {"name": interface_name, "ip": None, "mac": None}
                        interfaces.append(current_interface)
                
                # MAC address line
                elif current_interface and "link/ether" in line:
                    mac = line.split()[1]
                    current_interface["mac"] = mac
                
                # IP address line
                elif current_interface and "inet " in line:
                    ip_with_prefix = line.split()[1]
                    ip = ip_with_prefix.split("/")[0]
                    current_interface["ip"] = ip
            
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []
    
    def get_wifi_interfaces(self) -> List[Dict]:
        """Get WiFi interfaces"""
        wifi_interfaces = []
        
        try:
            # First try using iwconfig
            try:
                output = subprocess.check_output(["iwconfig"], text=True, stderr=subprocess.STDOUT)
                for line in output.splitlines():
                    if "IEEE 802.11" in line:  # Indicates WiFi interface
                        interface_name = line.split()[0]
                        wifi_interfaces.append({"name": interface_name})
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to checking /sys/class/net for wireless devices
                for interface in os.listdir("/sys/class/net"):
                    if os.path.exists(f"/sys/class/net/{interface}/wireless"):
                        wifi_interfaces.append({"name": interface})
            
            # Get more details for the WiFi interfaces
            all_interfaces = self.get_interfaces()
            for wifi_interface in wifi_interfaces:
                for interface in all_interfaces:
                    if interface["name"] == wifi_interface["name"]:
                        wifi_interface.update(interface)
                        break
            
            return wifi_interfaces
        except Exception as e:
            logger.error(f"Error getting WiFi interfaces: {e}")
            return []
    
    def get_wifi_signal_strength(self) -> Dict[str, Dict]:
        """Get WiFi signal strength information"""
        signal_info = {}
        
        try:
            # Try using iw dev command
            wifi_interfaces = self.get_wifi_interfaces()
            
            for interface in wifi_interfaces:
                try:
                    output = subprocess.check_output(["iw", "dev", interface["name"], "link"], text=True)
                    
                    interface_info = {}
                    
                    # Parse signal strength
                    signal_match = re.search(r"signal: (-\d+) dBm", output)
                    if signal_match:
                        signal_dbm = int(signal_match.group(1))
                        # Convert dBm to percentage-like scale (roughly)
                        # -50dBm or higher is excellent (100%), -100dBm or lower is poor (0%)
                        signal_percent = max(0, min(100, 2 * (signal_dbm + 100)))
                        interface_info["signal_strength"] = signal_percent
                    
                    # Parse BSSID (MAC address of connected access point)
                    bssid_match = re.search(r"Connected to ([0-9a-fA-F:]{17})", output)
                    if bssid_match:
                        interface_info["bssid"] = bssid_match.group(1)
                    
                    # Parse SSID (network name)
                    ssid_match = re.search(r"SSID: (.+)$", output, re.MULTILINE)
                    if ssid_match:
                        interface_info["ssid"] = ssid_match.group(1)
                    
                    if interface_info:
                        signal_info[interface["name"]] = interface_info
                        
                except Exception as e:
                    logger.debug(f"Error getting signal info for {interface['name']}: {e}")
            
            return signal_info
        except Exception as e:
            logger.error(f"Error getting WiFi signal strength: {e}")
            return {}
    
    def limit_device_speed(self, ip: str, limit_kbps: int) -> bool:
        """
        Limit device speed using tc (Traffic Control)
        
        Args:
            ip: IP address of device to limit
            limit_kbps: Speed limit in Kbps
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_admin:
            logger.error("Root privileges required to limit device speed")
            return False
            
        try:
            # Find default interface
            output = subprocess.check_output(["ip", "route"], text=True)
            default_interface = None
            for line in output.splitlines():
                if line.startswith("default"):
                    parts = line.split()
                    default_interface = parts[4]
                    break
            
            if not default_interface:
                logger.error("Could not find default interface")
                return False
            
            # Clean up any existing tc rules
            subprocess.call(["tc", "qdisc", "del", "dev", default_interface, "root"], stderr=subprocess.DEVNULL)
            
            # Set up tc hierarchy
            subprocess.run(["tc", "qdisc", "add", "dev", default_interface, "root", "handle", "1:", "htb", "default", "30"], check=True)
            subprocess.run(["tc", "class", "add", "dev", default_interface, "parent", "1:", "classid", "1:1", "htb", "rate", "1000mbit"], check=True)
            subprocess.run(["tc", "class", "add", "dev", default_interface, "parent", "1:1", "classid", "1:10", "htb", "rate", f"{limit_kbps}kbit", "ceil", f"{limit_kbps}kbit", "prio", "1"], check=True)
            
            # Add filter for the specific IP
            subprocess.run(["tc", "filter", "add", "dev", default_interface, "parent", "1:0", "protocol", "ip", "prio", "1", "u32", "match", "ip", "dst", ip, "flowid", "1:10"], check=True)
            subprocess.run(["tc", "filter", "add", "dev", default_interface, "parent", "1:0", "protocol", "ip", "prio", "1", "u32", "match", "ip", "src", ip, "flowid", "1:10"], check=True)
            
            logger.info(f"Speed limit of {limit_kbps}Kbps set for {ip}")
            return True
        except Exception as e:
            logger.error(f"Error limiting device speed: {e}")
            return False
    
    def block_device(self, ip: str) -> bool:
        """
        Block a device on the network using iptables
        
        Args:
            ip: IP address of device to block
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_admin:
            logger.error("Root privileges required to block device")
            return False
            
        try:
            # Block incoming and outgoing traffic for the IP
            subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-A", "FORWARD", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-A", "FORWARD", "-d", ip, "-j", "DROP"], check=True)
            
            logger.info(f"Device {ip} blocked")
            return True
        except Exception as e:
            logger.error(f"Error blocking device: {e}")
            return False
    
    def unblock_device(self, ip: str) -> bool:
        """
        Unblock a device on the network
        
        Args:
            ip: IP address of device to unblock
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_admin:
            logger.error("Root privileges required to unblock device")
            return False
            
        try:
            # Remove blocking rules for the IP
            subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-D", "OUTPUT", "-d", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-D", "FORWARD", "-s", ip, "-j", "DROP"], check=True)
            subprocess.run(["iptables", "-D", "FORWARD", "-d", ip, "-j", "DROP"], check=True)
            
            logger.info(f"Device {ip} unblocked")
            return True
        except Exception as e:
            logger.error(f"Error unblocking device: {e}")
            return False