import os
import sys

# Add project root and frontend directories to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(root_dir, "frontend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

from frontend.api.index import app
