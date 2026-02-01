# netmonitor/windows.py
import wmi
import win32com.client
import socket
import subprocess
import re
import time
import logging
import psutil
from typing import List, Dict, Optional, Tuple
import os

class WindowsNetworkMonitor:
    def __init__(self):
        try:
            self.wmi = wmi.WMI()
            self.logger = logging.getLogger(__name__)
            self._setup_commands()
        except Exception as e:
            self.logger.error(f"Failed to initialize WMI: {e}")
            raise RuntimeError(f"Failed to initialize Windows network monitoring: {e}")

    def _setup_commands(self):
        """Setup paths to Windows system commands"""
        system32 = os.path.join(os.environ['SystemRoot'], 'System32')
        self.netsh_path = os.path.join(system32, "netsh.exe")
        self.ipconfig_path = os.path.join(system32, "ipconfig.exe")
        self.arp_path = os.path.join(system32, "arp.exe")
        self.ping_path = os.path.join(system32, "ping.exe")
     
    def get_interfaces(self) -> List[Dict]: 
        interfaces = []
        try:
            # First try WMI
            try:
                wmi_interfaces = self.wmi.Win32_NetworkAdapter(PhysicalAdapter=True)
                config_interfaces = self.wmi.Win32_NetworkAdapterConfiguration(IPEnabled=True)
                mac_to_config = {c.MACAddress: c for c in config_interfaces if c.MACAddress}
                
                for interface in wmi_interfaces:
                    if interface.NetConnectionStatus != 2:  # Skip if not connected
                        continue
                    if not interface.MACAddress:
                        continue
                    
                    config = mac_to_config.get(interface.MACAddress)
                    if not config:
                        continue
                    
                    ip_addresses = config.IPAddress
                    ip_address = ip_addresses[0] if ip_addresses else None
                    
                    interfaces.append({
                        'name': interface.Name,
                        'description': interface.Description,
                        'mac': interface.MACAddress,
                        'ip': ip_address,
                        'type': self._get_interface_type(interface),
                        'speed': interface.Speed,
                        'status': 'up' if interface.NetConnectionStatus == 2 else 'down'
                    })
            except Exception as wmi_error:
                self.logger.debug(f"WMI interface detection failed: {wmi_error}")
                
                # Fallback to ipconfig parsing
                output = subprocess.check_output([self.ipconfig_path], 
                                              text=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                
                current_adapter = None
                current_info = {}
                
                for line in output.splitlines():
                    line = line.strip()
                    
                    if line.endswith(':'):
                        if current_adapter and current_info.get('ip'):
                            interfaces.append(current_info)
                            
                        # Extract adapter name
                        adapter_name = line[:-1].strip()
                        if adapter_name.startswith('Ethernet adapter '):
                            adapter_name = adapter_name[len('Ethernet adapter '):]
                        elif adapter_name.startswith('Wireless LAN adapter '):
                            adapter_name = adapter_name[len('Wireless LAN adapter '):]
                            
                        current_adapter = adapter_name
                        current_info = {
                            'name': adapter_name,
                            'description': adapter_name,
                            'type': 'wifi' if 'wireless' in line.lower() else 'ethernet',
                            'status': 'unknown'
                        }
                    elif current_adapter:
                        if "IPv4 Address" in line and ":" in line:
                            current_info['ip'] = line.split(":")[-1].strip().split('(')[0].strip()
                            current_info['status'] = 'up'
                        elif "Physical Address" in line and ":" in line:
                            current_info['mac'] = line.split(":")[-1].strip().replace('-', ':')
                        elif "Media State" in line and "disconnected" in line.lower():
                            current_info['status'] = 'down'
                
                # Add last adapter
                if current_adapter and current_info.get('ip'):
                    interfaces.append(current_info)
                
        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
            
        return interfaces
    
    def _get_interface_type(self, interface) -> str:
        """Determine interface type based on various properties"""
        desc = interface.Description.lower() if interface.Description else ""
        
        if "wi-fi" in desc or "wireless" in desc or "wlan" in desc:
            return "wifi"
        elif "ethernet" in desc or "gigabit" in desc:
            return "ethernet"
        elif "bluetooth" in desc:
            return "bluetooth"
        elif "virtual" in desc or "vmware" in desc or "virtualbox" in desc:
            return "virtual"
        elif "loopback" in desc or "localhost" in desc:
            return "loopback"
        else:
            return "other"
    
    def _get_interface_stats(self, interface_name: str) -> Dict:
        """Get interface statistics including bytes in/out"""
        stats = {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}
        
        try:
            # Try to find the interface by name or description in psutil
            for nic_name, nic_stats in psutil.net_io_counters(pernic=True).items():
                # Match partial name since interface names can be different across APIs
                if interface_name.lower() in nic_name.lower():
                    stats['bytes_sent'] = nic_stats.bytes_sent
                    stats['bytes_recv'] = nic_stats.bytes_recv
                    stats['packets_sent'] = nic_stats.packets_sent
                    stats['packets_recv'] = nic_stats.packets_recv
                    break
        except Exception as e:
            self.logger.error(f"Error getting interface stats: {e}")
        
        return stats
    
    def get_default_gateway(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the default gateway IP and interface name"""
        try:
            # Use ipconfig to find default gateway
            output = subprocess.check_output(
                [self.ipconfig_path], 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            current_adapter = None
            gateway = None
            
            for line in output.splitlines():
                line = line.strip()
                
                # New adapter section
                if line.endswith(':'):
                    current_adapter = line[:-1].strip()
                    
                # Look for Default Gateway
                if "Default Gateway" in line and ": " in line:
                    gateway_ip = line.split(": ")[1].strip()
                    if gateway_ip and gateway_ip != "0.0.0.0":
                        gateway = gateway_ip
                        return gateway, current_adapter
                        
            return gateway, current_adapter
        except Exception as e:
            self.logger.error(f"Error getting default gateway: {e}")
            return None, None
    
    def get_arp_table(self) -> List[Dict]:
        """Get ARP table entries"""
        devices = []
        try:
            # Run ARP command to get the table
            output = subprocess.check_output(
                [self.arp_path, '-a'], 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Parse the output
            for line in output.splitlines():
                line = line.strip()
                
                # Skip header and empty lines
                if not line or "Interface" in line or "Internet Address" in line:
                    continue
                    
                parts = re.split(r'\s+', line)
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]
                    
                    # Skip invalid or incomplete entries
                    if ip == "0.0.0.0" or mac == "00-00-00-00-00-00":
                        continue
                        
                    devices.append({
                        'ip': ip,
                        'mac': mac.replace('-', ':'),  # Standardize MAC format
                        'interface': None
                    })
        except Exception as e:
            self.logger.error(f"Error getting ARP table: {e}")
            
        return devices
    
    def get_wifi_signal_strength(self) -> Dict[str, Dict]:
        """Get WiFi signal strength and details for all connected devices"""
        signal_info = {}
        
        try:
            # Get WLAN interfaces using netsh
            output = subprocess.check_output(
                [self.netsh_path, "wlan", "show", "interfaces"],
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            current_interface = None
            current_info = {}
            
            for line in output.splitlines():
                line = line.strip()
                
                if line.startswith("Name"):
                    if current_interface and current_info:
                        signal_info[current_interface] = current_info
                    current_interface = line.split(":")[1].strip()
                    current_info = {}
                elif current_interface:
                    if "Signal" in line:
                        try:
                            signal = int(line.split(":")[1].strip().rstrip('%'))
                            current_info['signal_strength'] = signal
                        except:
                            pass
                    elif "BSSID" in line:
                        try:
                            bssid = line.split(":")[1].strip()
                            current_info['bssid'] = bssid
                        except:
                            pass
                    elif "Channel" in line:
                        try:
                            channel = line.split(":")[1].strip()
                            current_info['channel'] = channel
                        except:
                            pass
                    elif "Radio type" in line:
                        try:
                            radio = line.split(":")[1].strip()
                            current_info['radio_type'] = radio
                        except:
                            pass
            
            # Add last interface
            if current_interface and current_info:
                signal_info[current_interface] = current_info
                
        except Exception as e:
            self.logger.error(f"Error getting WiFi signal strength: {e}")
            
        return signal_info

    def _ensure_wlan_service(self) -> bool:
        """Ensure WLAN service is running"""
        try:
            # First try using SC command
            service_check = subprocess.run(
                ["sc", "query", "WlanSvc"],
                text=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if "RUNNING" not in service_check.stdout:
                # Try PowerShell if SC command failed or service not running
                try:
                    # Check service status using PowerShell
                    status_cmd = subprocess.run(
                        ["powershell", "-Command", "Get-Service -Name WlanSvc | Select-Object -ExpandProperty Status"],
                        text=True,
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if "Running" not in status_cmd.stdout:
                        # Try to start service using PowerShell
                        start_cmd = subprocess.run(
                            ["powershell", "-Command", "Start-Service -Name WlanSvc"],
                            text=True,
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        
                        if start_cmd.returncode == 0:
                            self.logger.info("Successfully started WLAN Service using PowerShell")
                            return True
                        else:
                            self.logger.error(f"Failed to start WLAN Service using PowerShell: {start_cmd.stderr}")
                            return False
                    else:
                        return True
                        
                except Exception as e:
                    self.logger.error(f"Error using PowerShell to manage WLAN Service: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking WLAN Service: {e}")
            return False

    def get_wifi_interfaces(self) -> List[Dict]:
        """Get details of all WiFi interfaces"""
        interfaces = []
        try:
            # Ensure WLAN service is running
            if not self._ensure_wlan_service():
                return interfaces

            # Try getting interfaces through WMI first
            try:
                wlan_interfaces = self.wmi.Win32_NetworkAdapter(
                    AdapterTypeId=9,  # WLAN
                    PhysicalAdapter=True
                )
                
                for iface in wlan_interfaces:
                    if iface.NetEnabled:
                        interfaces.append({
                            'name': iface.NetConnectionID,
                            'state': 'connected' if iface.NetConnectionStatus == 2 else 'disconnected',
                            'description': iface.Description,
                            'type': 'wifi'
                        })
            except Exception as wmi_error:
                self.logger.debug(f"WMI WiFi detection failed: {wmi_error}")

            # If no interfaces found through WMI, try netsh
            if not interfaces:
                output = subprocess.check_output(
                    [self.netsh_path, "wlan", "show", "interfaces"],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                current_interface = {}
                for line in output.splitlines():
                    line = line.strip()
                    
                    if line.startswith("Name"):
                        if current_interface:
                            interfaces.append(current_interface)
                        current_interface = {
                            'name': line.split(":", 1)[1].strip(),
                            'type': 'wifi'
                        }
                    elif current_interface:
                        for key in ['State', 'SSID', 'BSSID', 'Radio type', 'Channel']:
                            if line.startswith(key):
                                key_name = key.lower().replace(' ', '_')
                                current_interface[key_name] = line.split(":", 1)[1].strip()
                
                # Add last interface
                if current_interface:
                    interfaces.append(current_interface)
                    
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Error running netsh command: {e}")
        except Exception as e:
            self.logger.error(f"Error getting WiFi interfaces: {e}")
            
        return interfaces

    def is_wifi_enabled(self) -> bool:
        """Check if WiFi is enabled"""
        try:
            interfaces = self.get_wifi_interfaces()
            return len(interfaces) > 0 and any(i.get('state', '').lower() == 'connected' for i in interfaces)
        except:
            return False

    def perform_traceroute(self, target_ip: str) -> List[Dict]:
        """Perform traceroute to target IP"""
        hops = []
        
        # Validate IP address to prevent command injection
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(ip_pattern, target_ip):
            self.logger.error(f"Invalid IP address for traceroute: {target_ip}")
            return hops
        
        try:
            output = subprocess.check_output(
                ['tracert', '-d', '-h', '15', '-w', '500', target_ip],
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            hop_num = 0
            for line in output.splitlines():
                if "ms" in line and "over" not in line.lower():
                    hop_num += 1
                    
                    # Parse response times
                    times = re.findall(r'(\d+)\s*ms', line)
                    avg_time = sum(int(t) for t in times) / len(times) if times else 0
                    
                    # Parse IP address
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    ip = ip_match.group(1) if ip_match else "Unknown"
                    
                    hops.append({
                        'hop': hop_num,
                        'ip': ip,
                        'time_ms': avg_time
                    })
        except Exception as e:
            self.logger.error(f"Error performing traceroute: {e}")
            
        return hops
        
    def is_elevated(self) -> bool:
        """Check if the application is running with elevated privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def limit_device_speed(self, ip: str, limit_kbps: int) -> bool:
        """
        Limit device download/upload speed using Windows Firewall and QoS
        
        Args:
            ip: IP address of device to limit
            limit_kbps: Speed limit in Kbps
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_elevated():
            self.logger.error("Admin privileges required to limit device speed")
            return False
            
        try:
            # Convert Kbps to bits per second (bps) for QoS
            limit_bps = limit_kbps * 1000
            
            # Check if there's an existing rule
            check_cmd = subprocess.run(
                [self.netsh_path, "advfirewall", "firewall", "show", "rule", f"name=NetworkMonitor_Limit_{ip}"],
                text=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Delete any existing rule
            if "No rules match the specified criteria" not in check_cmd.stdout:
                subprocess.run(
                    [self.netsh_path, "advfirewall", "firewall", "delete", "rule", f"name=NetworkMonitor_Limit_{ip}"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            # Create a new rule with QoS limitation
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "add", "rule",
                f"name=NetworkMonitor_Limit_{ip}",
                "dir=in",
                "action=allow",
                f"remoteip={ip}",
                "protocol=any",
                f"qoslevel={limit_bps}"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Create outbound rule
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "add", "rule",
                f"name=NetworkMonitor_Limit_{ip}_out",
                "dir=out",
                "action=allow",
                f"remoteip={ip}",
                "protocol=any",
                f"qoslevel={limit_bps}"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.logger.info(f"Speed limit of {limit_kbps} Kbps set for device {ip}")
            return True
        except Exception as e:
            self.logger.error(f"Error limiting device speed: {e}")
            return False
    
    def block_device(self, ip: str) -> bool:
        """
        Block a device on the network using Windows Firewall
        
        Args:
            ip: IP address of device to block
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_elevated():
            self.logger.error("Admin privileges required to block device")
            return False
            
        try:
            # Check if there's an existing rule
            check_cmd = subprocess.run(
                [self.netsh_path, "advfirewall", "firewall", "show", "rule", f"name=NetworkMonitor_Block_{ip}"],
                text=True,
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Delete any existing rule
            if "No rules match the specified criteria" not in check_cmd.stdout:
                subprocess.run(
                    [self.netsh_path, "advfirewall", "firewall", "delete", "rule", f"name=NetworkMonitor_Block_{ip}"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            # Create inbound block rule
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "add", "rule",
                f"name=NetworkMonitor_Block_{ip}",
                "dir=in",
                "action=block",
                f"remoteip={ip}"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Create outbound block rule
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "add", "rule",
                f"name=NetworkMonitor_Block_{ip}_out",
                "dir=out",
                "action=block",
                f"remoteip={ip}"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.logger.info(f"Device {ip} blocked")
            return True
        except Exception as e:
            self.logger.error(f"Error blocking device: {e}")
            return False
    
    def unblock_device(self, ip: str) -> bool:
        """
        Unblock a previously blocked device
        
        Args:
            ip: IP address of device to unblock
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_elevated():
            self.logger.error("Admin privileges required to unblock device")
            return False
            
        try:
            # Remove inbound block rule
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "delete", "rule",
                f"name=NetworkMonitor_Block_{ip}"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Remove outbound block rule
            subprocess.run([
                self.netsh_path, "advfirewall", "firewall", "delete", "rule",
                f"name=NetworkMonitor_Block_{ip}_out"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Also remove any speed limiting rules
            try:
                subprocess.run([
                    self.netsh_path, "advfirewall", "firewall", "delete", "rule",
                    f"name=NetworkMonitor_Limit_{ip}"
                ], creationflags=subprocess.CREATE_NO_WINDOW)
                
                subprocess.run([
                    self.netsh_path, "advfirewall", "firewall", "delete", "rule",
                    f"name=NetworkMonitor_Limit_{ip}_out"
                ], creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass
                
            self.logger.info(f"Device {ip} unblocked")
            return True
        except Exception as e:
            self.logger.error(f"Error unblocking device: {e}")
            return False


