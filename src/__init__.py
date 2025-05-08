"""
Klaviyo Reporting POC Source Package

This package contains all the core functionality for the Klaviyo Reporting POC.
"""

# Version info
__version__ = '0.1.0'

import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))
