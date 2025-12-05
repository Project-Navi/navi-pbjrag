"""
Compatibility shim for pbjrag.metrics
This file redirects imports from pbjrag.metrics to pbjrag.crown_jewel.metrics
"""

# Import everything from the actual metrics module
from .crown_jewel.metrics import *  # noqa: F403

# Also make the module itself available
