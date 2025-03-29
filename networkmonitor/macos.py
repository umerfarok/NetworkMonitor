"""
macOS-specific network monitoring functionality
"""
import logging
import subprocess
import re
import socket
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class MacOSNetworkMonitor:
    """macOS specific network functionality"""
    def __init__(self):
        self.airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    
    def get_interfaces(self) -> List[Dict]:
        """Get all network interfaces"""
        interfaces = []
        try:
            # Use networksetup to list network interfaces
            output = subprocess.check_output(["networksetup", "-listallhardwareports"], text=True)
            
            # Process output
            current_interface = {}
            for line in output.splitlines():
                line = line.strip()
                
                if line.startswith("Hardware Port:"):
                    if current_interface and "name" in current_interface:
                        interfaces.append(current_interface)
                    current_interface = {"name": line.split(":", 1)[1].strip()}
                
                elif line.startswith("Device:") and current_interface:
                    current_interface["device"] = line.split(":", 1)[1].strip()
                
                elif line.startswith("Ethernet Address:") and current_interface:
                    current_interface["mac"] = line.split(":", 1)[1].strip()
            
            # Add the last interface
            if current_interface and "name" in current_interface:
                interfaces.append(current_interface)
            
            # Get IP addresses for interfaces
            for interface in interfaces:
                if "device" in interface:
                    try:
                        output = subprocess.check_output(["ipconfig", "getifaddr", interface["device"]], text=True)
                        interface["ip"] = output.strip()
                    except:
                        pass
                        
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []
    
    def get_wifi_interfaces(self) -> List[Dict]:
        """Get WiFi interfaces"""
        wifi_interfaces = []
        
        try:
            interfaces = self.get_interfaces()
            for interface in interfaces:
                if "name" in interface and any(wifi_term in interface["name"].lower() for wifi_term in ["wi-fi", "airport", "wireless"]):
                    wifi_interfaces.append(interface)
            return wifi_interfaces
        except Exception as e:
            logger.error(f"Error getting WiFi interfaces: {e}")
            return []
    
    def get_wifi_signal_strength(self) -> Dict[str, Dict]:
        """Get WiFi signal strength information"""
        signal_info = {}
        
        try:
            # Use airport command to get WiFi information
            output = subprocess.check_output([self.airport_path, "-I"], text=True)
            
            current_interface = None
            interface_info = {}
            
            for line in output.splitlines():
                line = line.strip()
                
                # Parse signal strength
                if "agrCtlRSSI" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        interface_info["signal_strength"] = int(parts[1].strip())
                
                # Parse BSSID (MAC address of connected access point)
                elif "BSSID" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        interface_info["bssid"] = parts[1].strip()
                
                # Parse SSID (network name)
                elif "SSID" in line and "BSSID" not in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        interface_info["ssid"] = parts[1].strip()
                        current_interface = interface_info["ssid"]
            
            if current_interface and interface_info:
                signal_info[current_interface] = interface_info
                
            return signal_info
        except Exception as e:
            logger.error(f"Error getting WiFi signal strength: {e}")
            return {}
    
    def limit_device_speed(self, ip: str, limit_kbps: int) -> bool:
        """
        Limit device download/upload speed using pfctl (macOS firewall)
        
        Args:
            ip: IP address of device to limit
            limit_kbps: Speed limit in Kbps
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a temporary pf rule file
            rule_file = "/tmp/networkmonitor_pf_rules"
            
            with open(rule_file, "w") as f:
                f.write(f"table <limited_devices> {{ {ip} }}\n")
                f.write(f"queue limit_q on en0 bandwidth {limit_kbps}Kb/s\n")
                f.write("block return out quick on en0 from any to <limited_devices> queue limit_q\n")
                f.write("block return in quick on en0 from <limited_devices> to any queue limit_q\n")
            
            # Load the rules
            subprocess.run(["sudo", "pfctl", "-f", rule_file], check=True)
            # Enable pf if not already enabled
            subprocess.run(["sudo", "pfctl", "-e"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"Error limiting device speed: {e}")
            return False
    
    def block_device(self, ip: str) -> bool:
        """
        Block a device on the network using pfctl
        
        Args:
            ip: IP address of device to block
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a temporary pf rule file
            rule_file = "/tmp/networkmonitor_pf_block"
            
            with open(rule_file, "w") as f:
                f.write(f"table <blocked_devices> {{ {ip} }}\n")
                f.write("block return in quick on en0 from <blocked_devices> to any\n")
                f.write("block return out quick on en0 from any to <blocked_devices>\n")
            
            # Load the rules
            subprocess.run(["sudo", "pfctl", "-f", rule_file], check=True)
            # Enable pf if not already enabled
            subprocess.run(["sudo", "pfctl", "-e"], check=True)
            
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
        try:
            # Create a temporary pf rule file that excludes the blocked device
            rule_file = "/tmp/networkmonitor_pf_rules"
            
            # Get current blocked devices except the one we're unblocking
            blocked_devices = []
            try:
                output = subprocess.check_output(["sudo", "pfctl", "-t", "blocked_devices", "-T", "show"], text=True)
                for line in output.splitlines():
                    if line.strip() and line.strip() != ip:
                        blocked_devices.append(line.strip())
            except:
                pass
            
            # Recreate the rules file without the unblocked device
            with open(rule_file, "w") as f:
                if blocked_devices:
                    f.write(f"table <blocked_devices> {{ {', '.join(blocked_devices)} }}\n")
                    f.write("block return in quick on en0 from <blocked_devices> to any\n")
                    f.write("block return out quick on en0 from any to <blocked_devices>\n")
                else:
                    # Empty rules just to clear previous rules
                    f.write("# No blocked devices\n")
                    
            # Load the rules
            subprocess.run(["sudo", "pfctl", "-f", rule_file], check=True)
            
            return True
        except Exception as e:
            logger.error(f"Error unblocking device: {e}")
            return False