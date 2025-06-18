import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_simple():
    assert True

def test_import():
    from tools.base_tool import ToolStatus
    assert ToolStatus.SUCCESS.value == "success"
