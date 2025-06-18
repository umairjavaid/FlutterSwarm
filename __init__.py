"""
FlutterSwarm package initialization.
"""

# Use lazy imports to avoid import issues during testing
def _get_flutter_swarm():
    from .flutter_swarm import FlutterSwarm
    return FlutterSwarm

def _get_run_flutter_swarm():
    from .flutter_swarm import run_flutter_swarm
    return run_flutter_swarm

def _get_shared_state():
    from .shared.state import shared_state
    return shared_state

# Only import these when accessed
__version__ = "1.0.0"
__author__ = "FlutterSwarm Team"

__all__ = [
    "FlutterSwarm",
    "run_flutter_swarm", 
    "shared_state"
]

# Lazy attribute access
def __getattr__(name):
    if name == "FlutterSwarm":
        return _get_flutter_swarm()
    elif name == "run_flutter_swarm":
        return _get_run_flutter_swarm()
    elif name == "shared_state":
        return _get_shared_state()
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
