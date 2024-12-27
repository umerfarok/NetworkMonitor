# server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from .monitor import NetworkMonitor
import logging
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

monitor = NetworkMonitor()
monitor.start_monitoring()  # Start background monitoring

def response(success: bool, data: Any = None, error: str = None) -> Dict:
    return {
        'success': success,
        'data': data,
        'error': error
    }

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

# server.py (continued)

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
    """Block a device from the network"""
    try:
        data = request.json
        ip = data.get('ip')
        
        if ip not in monitor.devices:
            return jsonify(response(False, error="Device not found")), 404
            
        # Implementation depends on your network setup
        # This is a placeholder for actual blocking logic
        success = True  # Replace with actual blocking implementation
        
        if success:
            monitor.devices[ip].status = "blocked"
            return jsonify(response(True, {'ip': ip, 'status': 'blocked'}))
        return jsonify(response(False, error="Failed to block device")), 500
    except Exception as e:
        logging.error(f"Error blocking device: {str(e)}")
        return jsonify(response(False, error=str(e))), 500

@app.route('/api/device/unblock', methods=['POST'])
def unblock_device():
    """Unblock a device from the network"""
    try:
        data = request.json
        ip = data.get('ip')
        
        if ip not in monitor.devices:
            return jsonify(response(False, error="Device not found")), 404
            
        # Implementation depends on your network setup
        # This is a placeholder for actual unblocking logic
        success = True  # Replace with actual unblocking implementation
        
        if success:
            monitor.devices[ip].status = "active"
            return jsonify(response(True, {'ip': ip, 'status': 'active'}))
        return jsonify(response(False, error="Failed to unblock device")), 500
    except Exception as e:
        logging.error(f"Error unblocking device: {str(e)}")
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

@app.errorhandler(500)
def server_error(e):
    return jsonify(response(False, error='Internal server error')), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)