"""
Test configuration and fixtures for NetworkMonitor
"""
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def temp_dir(tmpdir):
    """Provide a temporary directory for test files"""
    return tmpdir

@pytest.fixture
def mock_admin():
    """Mock admin privileges for testing"""
    import mock
    with mock.patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=1):
        yield