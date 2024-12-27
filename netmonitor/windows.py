# netmonitor/windows.py
import wmi
import psutil
import socket
import struct
import subprocess
from typing import List, Dict

class WindowsNetworkMonitor:
    def __init__(self):
        self.wmi = wmi.WMI()
    
    def get_interfaces(self) -> List[Dict]:
        interfaces = []
        try:
            # Get network adapters using WMI
            for adapter in self.wmi.Win32_NetworkAdapter(PhysicalAdapter=True):
                config = adapter.associators("Win32_NetworkAdapterConfiguration")[0]
                if config.IPAddress:
                    interfaces.append({
                        'name': adapter.Name,
                        'ip': config.IPAddress[0],
                        'mac': adapter.MACAddress,
                        'stats': self._get_interface_stats(adapter.Name)
                    })
        except Exception as e:
            print(f"Error getting interfaces: {e}")
        return interfaces
    
    def _get_interface_stats(self, interface_name: str) -> Dict:
        try:
            stats = psutil.net_io_counters(pernic=True)[interface_name]
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv
            }
        except:
            return {}
    
    def _get_arp_table(self) -> List[Dict]:
        devices = []
        try:
            # Run arp -a command
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('Interface'):
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1]
                        if mac != '<incomplete>':
                            devices.append({
                                'ip': ip,
                                'mac': mac
                            })
        except Exception as e:
            print(f"Error getting ARP table: {e}")
        return devices

# Import this class in monitor.py and use it for Windows systems