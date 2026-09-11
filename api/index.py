import os
import sys

# Ensure backend directory is first in sys.path so 'app' strictly resolves to backend/app
api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from app.main import app

app = app
