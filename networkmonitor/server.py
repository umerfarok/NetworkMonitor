from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from .monitor import NetworkController
import logging
from typing import Dict, Any
import platform
from .dependency_check import DependencyChecker
import os

def create_app():
    # Get the absolute path to the web directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(current_dir, 'web')
    static_dir = os.path.join(web_dir, 'public')
    
    if not os.path.exists(static_dir):
        # If public directory doesn't exist, try parent directory's web/public
        parent_web_dir = os.path.join(os.path.dirname(current_dir), 'web', 'public')
        if os.path.exists(parent_web_dir):
            static_dir = parent_web_dir

    app = Flask(__name__, 
                static_folder=static_dir,
                static_url_path='')
    CORS(app)

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
    
    monitor = NetworkController()
    
    try:
        if is_ready:  # Only start monitoring if all dependencies are met
            monitor.start_monitoring()
            app.logger.info("Network monitoring started")
        else:
            app.logger.warning("Network monitoring not started due to missing dependencies")
    except Exception as e:
        app.logger.error(f"Error starting monitoring: {e}")

    def response(success: bool, data: Any = None, error: str = None) -> Dict:
        return {
            'success': success,
            'data': data,
            'error': error
        }
    
    # HTML template for missing dependencies page
    DEPENDENCY_ERROR_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Monitor - Missing Dependencies</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }
            .error-box {
                background-color: #ffebee;
                border-left: 5px solid #f44336;
                padding: 15px;
                margin-bottom: 20px;
            }
            .warning-box {
                background-color: #fff8e1;
                border-left: 5px solid #ffc107;
                padding: 15px;
                margin-bottom: 20px;
            }
            .instruction-box {
                background-color: #e8f5e9;
                border-left: 5px solid #4caf50;
                padding: 15px;
                margin-bottom: 20px;
            }
            h2 {
                color: #333;
                margin-top: 30px;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .btn {
                display: inline-block;
                background-color: #2196f3;
                color: white;
                padding: 10px 15px;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 20px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Network Monitor - Missing Dependencies</h1>
        
        <div class="error-box">
            <h2>Network Monitor cannot start</h2>
            <p>Some required dependencies are missing from your system. These need to be installed before the application can run correctly.</p>
        </div>
        
        {% if missing_deps %}
        <h2>Missing Dependencies:</h2>
        <ul>
            {% for dep in missing_deps %}
            <li>{{ dep }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        
        {% if warnings %}
        <div class="warning-box">
            <h2>Warnings:</h2>
            <ul>
                {% for warning in warnings %}
                <li>{{ warning }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if instructions %}
        <h2>Installation Instructions:</h2>
        {% for title, instruction in instructions.items() %}
        <div class="instruction-box">
            <h3>{{ title }}</h3>
            <pre>{{ instruction }}</pre>
        </div>
        {% endfor %}
        {% endif %}
        
        <p>
            <button class="btn" onclick="window.location.reload()">Check Again</button>
        </p>
        
        <hr>
        <p><small>Network Monitor v0.1.0 - <a href="https://github.com/yourusername/networkmonitor">Documentation</a></small></p>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        """Serve the web interface or dependency error page"""
        # Check dependencies again in case user installed something
        is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
        
        if not is_ready:
            # Show missing dependencies page
            instructions = dependency_checker.get_installation_instructions()
            return render_template_string(
                DEPENDENCY_ERROR_TEMPLATE, 
                missing_deps=missing_deps,
                warnings=warnings,
                instructions=instructions
            )
        
        # First try to serve index.html from static folder
        try:
            if os.path.exists(os.path.join(static_dir, 'index.html')):
                return app.send_static_file('index.html')
        except Exception as e:
            logging.error(f"Error serving static file: {e}")
        
        # If no frontend is found, show API status
        return jsonify({
            "status": "running",
            "message": "API server is running but frontend is not built. Please build the frontend first.",
            "api_docs": "/api"
        })

    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Get server and monitoring status"""
        try:
            # Check dependencies again
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            
            return jsonify(response(True, {
                'server_status': 'running',
                'monitoring_active': monitor.monitoring_thread and monitor.monitoring_thread.is_alive(),
                'os_type': platform.system(),
                'interface': monitor.get_default_interface(),
                'dependencies_ok': is_ready,
                'missing_dependencies': missing_deps,
                'warnings': warnings
            }))
        except Exception as e:
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/wifi/interfaces', methods=['GET'])
    def get_wifi_interfaces():
        """Get all WiFi interfaces"""
        try:
            interfaces = monitor.get_wifi_interfaces()
            return jsonify(response(True, interfaces))
        except Exception as e:
            logging.error(f"Error getting WiFi interfaces: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

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
            logging.error(f"Error getting devices: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/devices/<ip>', methods=['GET'])
    def get_device_details(ip: str):
        """Get detailed information about a specific device"""
        try:
            details = monitor.get_device_details(ip)
            if details:
                return jsonify(response(True, details))
            return jsonify(response(False, error="Device not found")), 404
        except Exception as e:
            logging.error(f"Error getting device details: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/network/summary', methods=['GET'])
    def get_network_summary():
        """Get summary of network devices and usage"""
        try:
            summary = monitor.get_network_summary()
            return jsonify(response(True, summary))
        except Exception as e:
            logging.error(f"Error getting network summary: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/limit', methods=['POST'])
    def set_device_limit():
        """Set speed limit for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            limit = float(data.get('limit', 0))
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, error="Device not found")), 404
                
            device.speed_limit = limit
            return jsonify(response(True, {
                'ip': ip,
                'speed_limit': limit
            }))
        except Exception as e:
            logging.error(f"Error setting device limit: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/limit/<ip>', methods=['DELETE'])
    def remove_device_limit(ip: str):
        """Remove speed limit from a device"""
        try:
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, error="Device not found")), 404
                
            device.speed_limit = None
            return jsonify(response(True, {'ip': ip}))
        except Exception as e:
            logging.error(f"Error removing device limit: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/block', methods=['POST'])
    def block_device():
        """Block a device"""
        try:
            data = request.json
            ip = data.get('ip')
            if monitor.block_device(ip):
                return jsonify(response(True, {'ip': ip}))
            return jsonify(response(False, error='Failed to block device')), 500
        except Exception as e:
            logging.error(f"Error blocking device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/rename', methods=['POST'])
    def rename_device():
        """Set a custom name for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            name = data.get('name')
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, error="Device not found")), 404
                
            device.hostname = name
            return jsonify(response(True, {
                'ip': ip,
                'hostname': name
            }))
        except Exception as e:
            logging.error(f"Error renaming device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/type', methods=['POST'])
    def set_device_type():
        """Set device type manually"""
        try:
            data = request.json
            ip = data.get('ip')
            device_type = data.get('type')
            
            device = monitor.devices.get(ip)
            if not device:
                return jsonify(response(False, error="Device not found")), 404
                
            device.device_type = device_type
            return jsonify(response(True, {
                'ip': ip,
                'device_type': device_type
            }))
        except Exception as e:
            logging.error(f"Error setting device type: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

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
            logging.error(f"Error getting bandwidth stats: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/monitor/start', methods=['POST'])
    def start_monitoring():
        """Start the device monitoring"""
        try:
            # Check dependencies first
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            if not is_ready:
                return jsonify(response(False, error="Missing dependencies", 
                                        data={"missing": missing_deps})), 400
            
            monitor.start_monitoring()
            return jsonify(response(True, {'status': 'monitoring started'}))
        except Exception as e:
            logging.error(f"Error starting monitoring: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/monitor/stop', methods=['POST'])
    def stop_monitoring():
        """Stop the device monitoring"""
        try:
            monitor.stop_monitoring()
            return jsonify(response(True, {'status': 'monitoring stopped'}))
        except Exception as e:
            logging.error(f"Error stopping monitoring: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(response(False, error='Resource not found')), 404
    
    @app.route('/api/device/protect', methods=['POST'])
    def protect_device():
        """Enable protection for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            
            if monitor.protect_device(ip):
                return jsonify(response(True, {
                    'ip': ip,
                    'status': 'protected'
                }))
            return jsonify(response(False, error='Failed to protect device')), 500
        except Exception as e:
            logging.error(f"Error protecting device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/unprotect', methods=['POST'])
    def unprotect_device():
        """Disable protection for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            
            if monitor.unprotect_device(ip):
                return jsonify(response(True, {
                    'ip': ip,
                    'status': 'unprotected'
                }))
            return jsonify(response(False, error='Failed to unprotect device')), 500
        except Exception as e:
            logging.error(f"Error unprotecting device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/cut', methods=['POST'])
    def cut_device():
        """Cut network access for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            
            if monitor.cut_device(ip):
                return jsonify(response(True, {
                    'ip': ip,
                    'status': 'cutting'
                }))
            return jsonify(response(False, error='Failed to cut device')), 500
        except Exception as e:
            logging.error(f"Error cutting device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/restore', methods=['POST'])
    def restore_device():
        """Restore network access for a device"""
        try:
            data = request.json
            ip = data.get('ip')
            
            if monitor.stop_cut(ip):
                return jsonify(response(True, {
                    'ip': ip,
                    'status': 'restored'
                }))
            return jsonify(response(False, error='Failed to restore device')), 500
        except Exception as e:
            logging.error(f"Error restoring device: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/device/status', methods=['GET'])
    def get_device_status():
        """Get attack/protection status of devices"""
        try:
            statuses = {
                ip: {
                    'is_protected': device.is_protected,
                    'attack_status': device.attack_status
                }
                for ip, device in monitor.devices.items()
            }
            return jsonify(response(True, statuses))
        except Exception as e:
            logging.error(f"Error getting device statuses: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/network/gateway', methods=['GET'])
    def get_gateway_info():
        """Get gateway information"""
        try:
            gateway_ip, gateway_mac = monitor._get_gateway_info()
            return jsonify(response(True, {
                'ip': gateway_ip,
                'mac': gateway_mac
            }))
        except Exception as e:
            logging.error(f"Error getting gateway info: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.route('/api/dependencies/check', methods=['GET'])
    def check_dependencies():
        """Check system dependencies and return status"""
        try:
            is_ready, missing_deps, warnings = dependency_checker.check_all_dependencies()
            instructions = dependency_checker.get_installation_instructions() if missing_deps else {}
            
            return jsonify(response(True, {
                'ready': is_ready,
                'missing_dependencies': missing_deps,
                'warnings': warnings,
                'installation_instructions': instructions
            }))
        except Exception as e:
            logging.error(f"Error checking dependencies: {str(e)}")
            return jsonify(response(False, error=str(e))), 500

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(response(False, error='Internal server error')), 500

    def cleanup():
        # Stop all attacks and monitoring
        for ip in list(monitor.attack_threads.keys()):
            monitor.stop_cut(ip)
        monitor.stop_monitoring()

    import atexit
    atexit.register(cleanup)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)