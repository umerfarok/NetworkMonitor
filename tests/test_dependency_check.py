"""
Tests for dependency checking functionality
"""
import pytest
from networkmonitor.dependency_check import check_system_requirements

def test_system_requirements():
    """Test that system requirements check returns a tuple"""
    result = check_system_requirements()
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)