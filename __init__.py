"""
FlutterSwarm package initialization.
"""

from .flutter_swarm import FlutterSwarm, run_flutter_swarm
from .shared.state import shared_state

__version__ = "1.0.0"
__author__ = "FlutterSwarm Team"

__all__ = [
    "FlutterSwarm",
    "run_flutter_swarm", 
    "shared_state"
]
