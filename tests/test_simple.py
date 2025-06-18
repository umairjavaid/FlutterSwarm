"""
Simple test to verify pytest setup.
"""

import pytest

def test_simple_addition():
    """Test basic arithmetic to verify pytest is working."""
    assert 2 + 2 == 4

def test_simple_string():
    """Test string operations."""
    assert "hello" + " world" == "hello world"

@pytest.mark.unit
def test_with_marker():
    """Test with unit marker."""
    assert True

if __name__ == "__main__":
    print("Tests defined successfully")
