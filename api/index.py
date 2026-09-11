import os
import sys

# Add api directory, root directory, and backend directory to sys.path
api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

for d in [api_dir, root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from app.main import app
except ImportError:
    from backend.app.main import app

handler = app

