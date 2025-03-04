"""
Network Monitor Server Module
Provides Flask web server and API endpoints
"""
import os
import sys
import logging
import platform
import atexit
import socket
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request, render_template_string, abort
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor.log'),  
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_available_interfaces() -> List[Dict[str, str]]:
    """Get list of network interfaces available for binding"""
    interfaces = []
    
    try:
        # Try to get network interfaces
        import ifaddr
        adapters = ifaddr.get_adapters()
        
        # Filter for IPv4 addresses
        for adapter in adapters:
            for ip in adapter.ips:
                if isinstance(ip.ip, str):  # IPv4 address
                    # Skip loopback interfaces for this list
                    if not ip.ip.startswith('127.'):
                        interfaces.append({
                            'name': adapter.nice_name,
                            'ip': ip.ip,
                            'network_prefix': ip.network_prefix
                        })
    except ImportError:
        # Fallback: try socket-based approach
        try:
            # Get hostname and IP
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
            
            interfaces.append({
                'name': hostname,
                'ip': host_ip,
                'network_prefix': 24  # Assume /24 network
            })
        except Exception as e:
            logger.error(f"Failed to get network interfaces: {e}")
            
    # Always include localhost
    interfaces.append({
        'name': 'Localhost',
        'ip': '127.0.0.1',
        'network_prefix': 8
    })
            
    return interfaces

def create_app(host: str = '127.0.0.1', port: int = 5000):
    """Create and configure the Flask application"""
    
    # Import NetworkController here to avoid circular imports
    try:
        # Try relative import first
        from .monitor import NetworkController
        from .dependency_check import DependencyChecker
    except ImportError:
        # Try absolute import if relative fails
        from networkmonitor.monitor import NetworkController
        from networkmonitor.dependency_check import DependencyChecker
    except Exception as e:
        logger.error(f"Failed to import required modules: {e}")
        # Create dummy classes for graceful degradation
        class DummyNetworkController:
            def __init__(self):
                self.devices = {}
                self.monitoring_thread = None
            def start_monitoring(self): pass
            def stop_monitoring(self): pass
            def get_connected_devices(self): return []
            def get_network_summary(self): return {"devices": 0, "active": 0}
            def get_default_interface(self): return None
            def get_wifi_interfaces(self): return []
        
        class DummyDependencyChecker:
            def check_all_dependencies(self): 
                return False, ["Required modules could not be imported"], [str(e)]
        
        NetworkController = DummyNetworkController
        DependencyChecker = DummyDependencyChecker

    # Initialize Flask app
    app = Flask(__name__)
    
    # Enable CORS for all domains (for development)
    CORS(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('networkmonitor.log'),  
            logging.StreamHandler()
        ]
    )

    # Check dependencies before starting
    dependency_checker = DependencyChecker()
    is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
    
    # Log warnings and missing dependencies
    for warning in warnings:
        app.logger.warning(warning)
    
    for dep in missing_deps:
        app.logger.error(f"Missing dependency: {dep}")
    
    # Initialize network monitor
    try:
        monitor = NetworkController()
        
        if is_ready:  # Only start monitoring if all dependencies are met
            monitor.start_monitoring()
            app.logger.info("Network monitoring started")
        else:
            app.logger.warning("Network monitoring not started due to missing dependencies")
    except Exception as e:
        app.logger.error(f"Error starting monitoring: {e}")
        monitor = NetworkController()  # Create an instance but don't start monitoring

    def response(success: bool, data: Any = None, error: str = None) -> Dict:
        """Standard response format for API endpoints"""
        return {
            'success': success,
            'data': data,
            'error': error
        }

    @app.route('/')
    def index():
        """API root endpoint showing server status"""
        # Check if we have any HTML template for the interface
        if hasattr(app, 'send_static_file'):
            try:
                return app.send_static_file('index.html')
            except:
                pass
                
        # Otherwise, return JSON info
        return jsonify({
            "status": "running",
            "version": "0.1.0",
            "api_docs": "/api/docs",
            "endpoints": [
                "/api/status",
                "/api/devices",
                "/api/wifi/interfaces",
                "/api/network/gateway",
                "/api/network/summary",
                "/api/stats/bandwidth"
            ],
            "bind_address": f"{host}:{port}",
            "available_interfaces": get_available_interfaces()
        })

    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Get server and monitoring status"""
        try:
            # Check dependencies again
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            
            return jsonify(response(True, {
                'server_status': 'running',
                'monitoring_active': hasattr(monitor, 'monitoring_thread') and monitor.monitoring_thread and monitor.monitoring_thread.is_alive(),
                'os_type': platform.system(),
                'interface': monitor.get_default_interface(),
                'dependencies_ok': is_ready,
                'missing_dependencies': missing_deps,
                'warnings': warnings,
                'available_interfaces': get_available_interfaces()
            }))
        except Exception as e:
            app.logger.error(f"Error getting status: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/wifi/interfaces', methods=['GET'])
    def get_wifi_interfaces():
        """Get all WiFi interfaces"""
        try:
            interfaces = monitor.get_wifi_interfaces()
            return jsonify(response(True, interfaces))
        except Exception as e:
            app.logger.error(f"Error getting WiFi interfaces: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/devices', methods=['GET'])
    def get_devices():
        """Get all connected devices"""
        try:
            interface = request.args.get('interface')
            devices = monitor.get_connected_devices(interface)
            
            return jsonify(response(True, [
                {
                    'ip': d.ip,
                    'mac': d.mac,
                    'hostname': d.hostname,
                    'vendor': d.vendor,
                    'device_type': d.device_type,
                    'signal_strength': d.signal_strength,
                    'connection_type': d.connection_type,
                    'status': d.status,
                    'current_speed': d.current_speed,
                    'speed_limit': d.speed_limit,
                    'last_seen': d.last_seen.isoformat() if d.last_seen else None
                }
                for d in devices
            ]))
        except Exception as e:
            app.logger.error(f"Error getting devices: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/devices/<ip>', methods=['GET'])
    def get_device_details(ip: str):
        """Get detailed information about a specific device"""
        try:
            details = monitor.get_device_details(ip)
            if details:
                return jsonify(response(True, details))
            return jsonify(response(False, None, "Device not found")), 404
        except Exception as e:
            app.logger.error(f"Error getting device details: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/network/summary', methods=['GET'])
    def get_network_summary():
        """Get summary of network devices and usage"""
        try:
            summary = monitor.get_network_summary()
            return jsonify(response(True, summary))
        except Exception as e:
            app.logger.error(f"Error getting network summary: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/limit', methods=['POST'])
    def set_device_limit():
        """Set speed limit for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            limit = float(data.get('limit', 0))
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, None, "Device not found")), 404
                
            device.speed_limit = limit
            return jsonify(response(True, {
                'ip': ip,
                'speed_limit': limit
            }))
        except Exception as e:
            app.logger.error(f"Error setting device limit: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/limit/<ip>', methods=['DELETE'])
    def remove_device_limit(ip: str):
        """Remove speed limit from a device"""
        try:
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, None, "Device not found")), 404
                
            device.speed_limit = None
            return jsonify(response(True, {'ip': ip}))
        except Exception as e:
            app.logger.error(f"Error removing device limit: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/block', methods=['POST'])
    def block_device():
        """Block a device"""
        try:
            data = request.json
            ip = data.get('ip')
            if monitor.block_device(ip):
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, None, "Failed to block device")), 500
        except Exception as e:
            app.logger.error(f"Error blocking device: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/rename', methods=['POST'])
    def rename_device():
        """Set a custom name for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            name = data.get('name')
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, None, "Device not found")), 404
                
            device.hostname = name
            return jsonify(response(True, {
                'ip': ip,
                'hostname': name
            }))
        except Exception as e:
            app.logger.error(f"Error renaming device: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/type', methods=['POST'])
    def set_device_type():
        """Set device type manually"""
        try:
            data = request.json
            ip = data.get('ip')
            device_type = data.get('type')
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, None, "Device not found")), 404
                
            device.device_type = device_type
            return jsonify(response(True, {
                'ip': ip,
                'device_type': device_type
            }))
        except Exception as e:
            app.logger.error(f"Error setting device type: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/stats/bandwidth', methods=['GET'])
    def get_bandwidth_stats():
        """Get bandwidth statistics for all devices"""
        try:
            stats = {
                ip: {
                    'current_speed': device.current_speed,
                    'speed_limit': device.speed_limit,
                    'status': device.status
                }
                for ip, device in monitor.devices.items()
                if device.status == 'active'
            }
            return jsonify(response(True, stats))
        except Exception as e:
            app.logger.error(f"Error getting bandwidth stats: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/monitor/start', methods=['POST'])
    def start_monitoring():
        """Start the device monitoring"""
        try:
            # Check dependencies first
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            if not is_ready:
                return jsonify(response(False, None, f"Missing dependencies: {', '.join(missing_deps)}")), 500
                
            if hasattr(monitor, 'monitoring_thread') and monitor.monitoring_thread and monitor.monitoring_thread.is_alive():
                return jsonify(response(True, {"status": "already_running"}))
                
            monitor.start_monitoring()
            return jsonify(response(True, {"status": "started"}))
        except Exception as e:
            app.logger.error(f"Error starting monitoring: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/monitor/stop', methods=['POST'])
    def stop_monitoring():
        """Stop the device monitoring"""
        try:
            monitor.stop_monitoring()
            return jsonify(response(True, {"status": "stopped"}))
        except Exception as e:
            app.logger.error(f"Error stopping monitoring: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/protect', methods=['POST'])
    def protect_device():
        """Enable protection for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            result = getattr(monitor, 'protect_device', lambda x: False)(ip)
            if result:
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, None, "Failed to protect device")), 500
        except Exception as e:
            app.logger.error(f"Error protecting device: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/unprotect', methods=['POST'])
    def unprotect_device():
        """Disable protection for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            result = getattr(monitor, 'unprotect_device', lambda x: False)(ip)
            if result:
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, None, "Failed to unprotect device")), 500
        except Exception as e:
            app.logger.error(f"Error unprotecting device: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/cut', methods=['POST'])
    def cut_device():
        """Cut network access for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            result = getattr(monitor, 'cut_device', lambda x: False)(ip)
            if result:
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, None, "Failed to cut device connection")), 500
        except Exception as e:
            app.logger.error(f"Error cutting device connection: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/restore', methods=['POST'])
    def restore_device():
        """Restore network access for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            result = getattr(monitor, 'restore_device', lambda x: False)(ip)
            if result:
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, None, "Failed to restore device connection")), 500
        except Exception as e:
            app.logger.error(f"Error restoring device connection: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/device/status', methods=['GET'])
    def get_device_status():
        """Get attack/protection status of devices"""
        try:
            status = getattr(monitor, 'get_protection_status', lambda: {})(request.args.get('ip'))
            return jsonify(response(True, status))
        except Exception as e:
            app.logger.error(f"Error getting device status: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/network/gateway', methods=['GET'])
    def get_gateway_info():
        """Get gateway information"""
        try:
            gateway_info = getattr(monitor, '_get_gateway_info', lambda: (None, None))()
            if gateway_info and len(gateway_info) == 2:
                gateway_ip, gateway_mac = gateway_info
                return jsonify(response(True, {
                    'ip': gateway_ip,
                    'mac': gateway_mac
                }))
            return jsonify(response(False, None, "Could not get gateway information")), 404
        except Exception as e:
            app.logger.error(f"Error getting gateway info: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/dependencies/check', methods=['GET'])
    def check_dependencies():
        """Check system dependencies and return status"""
        try:
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            return jsonify(response(True, {
                'dependencies_ok': is_ready,
                'missing_dependencies': missing_deps,
                'warnings': warnings
            }))
        except Exception as e:
            app.logger.error(f"Error checking dependencies: {e}")
            return jsonify(response(False, None, str(e))), 500

    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """Show API documentation"""
        docs_html = """  
        <!DOCTYPE html>
        <html>
        <head>
            <title>Network Monitor API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                h1 { color: #333; }
                h2 { color: #444; margin-top: 30px; }
                .endpoint { background: #f4f4f4; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
                .method { font-weight: bold; display: inline-block; width: 80px; }
                .path { font-family: monospace; }
                .description { margin-top: 10px; } 
                .parameters { margin-top: 10px; }
                .parameter { margin-left: 20px; }
                .param-name { font-weight: bold; }
                .example { background: #e9e9e9; padding: 10px; border-radius: 3px; overflow-x: auto; }
                code { font-family: monospace; }
            </style>
        </head>
        <body>
            <h1>Network Monitor API Documentation</h1>
            
            <h2>Status Endpoints</h2>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/status</span></div>
                <div class="description">Get server and monitoring status</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/dependencies/check</span></div>
                <div class="description">Check system dependencies and return status</div>
            </div>
            
            <h2>Device Endpoints</h2>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/devices</span></div>
                <div class="description">Get all connected devices</div>
                <div class="parameters">
                    <div>Optional parameters:</div>
                    <div class="parameter"><span class="param-name">interface</span> - Filter by network interface</div>
                </div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/devices/:ip</span></div>
                <div class="description">Get details about a specific device</div>
            </div>

            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/rename</span></div>
                <div class="description">Rename a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100", "name": "New Device Name" }</code></div>
            </div>

            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/type</span></div>
                <div class="description">Set device type</div>
                <div class="example"><code>{ "ip": "192.168.1.100", "type": "computer" }</code></div>
            </div>
            
            <h2>Network Control Endpoints</h2>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/block</span></div>
                <div class="description">Block a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100" }</code></div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/limit</span></div>
                <div class="description">Set speed limit for a device (in Kbps)</div>
                <div class="example"><code>{ "ip": "192.168.1.100", "limit": 1024 }</code></div>
            </div>

            <div class="endpoint">
                <div><span class="method">DELETE</span> <span class="path">/api/device/limit/:ip</span></div>
                <div class="description">Remove speed limit from a device</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/protect</span></div>
                <div class="description">Enable protection for a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100" }</code></div>
            </div>

            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/unprotect</span></div>
                <div class="description">Disable protection for a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100" }</code></div>
            </div>

            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/cut</span></div>
                <div class="description">Cut network access for a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100" }</code></div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/device/restore</span></div>
                <div class="description">Restore network access for a device</div>
                <div class="example"><code>{ "ip": "192.168.1.100" }</code></div>
            </div>
            
            <h2>Network Information Endpoints</h2>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/wifi/interfaces</span></div>
                <div class="description">Get all WiFi interfaces</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/network/gateway</span></div>
                <div class="description">Get gateway information</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/network/summary</span></div>
                <div class="description">Get summary of network devices and usage</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <span class="path">/api/stats/bandwidth</span></div>
                <div class="description">Get bandwidth statistics for all devices</div>
            </div>
            
            <h2>Monitoring Control</h2>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/monitor/start</span></div>
                <div class="description">Start the device monitoring</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">POST</span> <span class="path">/api/monitor/stop</span></div>
                <div class="description">Stop the device monitoring</div>
            </div>
        </body>
        </html>
        """
        return render_template_string(docs_html)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(response(False, None, "Endpoint not found")), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify(response(False, None, f"Internal server error: {str(e)}")), 500

    def cleanup():
        # Stop all attacks and monitoring
        if hasattr(monitor, 'attack_threads'):
            for ip in list(monitor.attack_threads.keys()):
                if hasattr(monitor, 'stop_cut'):
                    try:
                        monitor.stop_cut(ip)
                    except:
                        pass
                        
        if hasattr(monitor, 'stop_monitoring'):
            try:
                monitor.stop_monitoring()
            except:
                pass
                
    atexit.register(cleanup)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # If run directly, determine the best host to bind to
    host = '127.0.0.1'  # Default to localhost
    port = 5000
    
    # Check if we should bind to all interfaces
    if '--external' in sys.argv:
        interfaces = get_available_interfaces()
        # Find a non-localhost interface
        for interface in interfaces:
            if not interface['ip'].startswith('127.'):
                host = interface['ip']
                break
        
        # If no suitable interface found, bind to all interfaces
        if host.startswith('127.'):
            host = '0.0.0.0'
    
    # Custom port
    if '--port' in sys.argv and sys.argv.index('--port') + 1 < len(sys.argv):
        try:
            port = int(sys.argv[sys.argv.index('--port') + 1])
        except:
            pass
    
    # Print listening info
    print(f"Starting server on http://{host}:{port}")
    
    # Run the app
    app_instance = create_app(host, port)
    app_instance.run(host=host, port=port, debug=True)