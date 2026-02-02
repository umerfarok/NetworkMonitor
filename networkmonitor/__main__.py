#!/usr/bin/env python
"""
NetworkMonitor Entry Point
This module provides the main entry point for the packaged application.
"""
import sys
import os


# Ensure the networkmonitor package is in the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
    # Add the executable directory to path
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))
    parent_path = os.path.dirname(application_path)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)

def main():
    """Main entry point for NetworkMonitor application."""
    try:
        # Import after path setup
        from networkmonitor.launcher import start_server
        from networkmonitor.dependency_check import check_system_requirements
        
        # Check dependencies
        ok, message = check_system_requirements()
        if not ok:
            print(f"Dependency check failed: {message}", file=sys.stderr)
            print("\nPlease ensure all requirements are installed.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("=" * 50)
        print("  NetworkMonitor - Network Monitoring Tool")
        print("=" * 50)
        print("\nStarting server on http://localhost:5000")
        print("Press Ctrl+C to stop the server\n")
        
        # Start the server
        success, controller = start_server(host='0.0.0.0', port=5000)
        
        if not success:
            print("Failed to start server", file=sys.stderr)
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Open browser
        try:
            import webbrowser
            webbrowser.open('http://localhost:5000')
        except Exception:
            pass
        
        # Keep running until interrupted
        try:
            controller.wait_for_shutdown()
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            controller.stop_monitoring()
            print("Server stopped.")
            
    except ImportError as e:
        print(f"Import Error: {e}", file=sys.stderr)
        print("\nThis usually means a required dependency is missing.")
        print("Please run: pip install -r requirements.txt")
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
