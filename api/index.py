import os
import sys

# Add root directory and backend directory to sys.path so imports resolve seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Override sqlite3 with pysqlite3-binary for ChromaDB compatibility on Linux/Vercel serverless
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from backend.app.main import app

