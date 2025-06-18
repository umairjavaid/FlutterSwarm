"""
Isolated test file that doesn't depend on FlutterSwarm imports.
"""

import pytest

def test_basic_math():
    """Test basic mathematical operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5

def test_string_operations():
    """Test string operations."""
    assert "hello".upper() == "HELLO"
    assert "WORLD".lower() == "world"
    assert "hello" + "world" == "helloworld"

def test_list_operations():
    """Test list operations."""
    lst = [1, 2, 3]
    assert len(lst) == 3
    assert lst[0] == 1
    lst.append(4)
    assert len(lst) == 4

def test_dict_operations():
    """Test dictionary operations."""
    d = {"a": 1, "b": 2}
    assert d["a"] == 1
    d["c"] = 3
    assert len(d) == 3

if __name__ == "__main__":
    # Run tests directly
    test_basic_math()
    test_string_operations()
    test_list_operations()
    test_dict_operations()
    print("All isolated tests passed!")
