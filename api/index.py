import os
import sys

# Add root directory and backend directory to sys.path so imports resolve seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")
app_dir = os.path.join(backend_dir, "app")

for d in [root_dir, backend_dir, app_dir]:
    if d not in sys.path and os.path.exists(d):
        sys.path.insert(0, d)

try:
    from backend.app.main import app
except ImportError:
    try:
        from app.main import app
    except ImportError:
        from main import app



