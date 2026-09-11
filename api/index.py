import os
import sys
import traceback

api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

for d in [api_dir, root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from app.main import app
except Exception as e:
    err_msg = f"Failed to load FastAPI app: {e}\n{traceback.format_exc()}"
    print(f"[Vercel Startup Error] {err_msg}")
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/{path:path}")
    def catch_all_error(path: str):
        return {
            "error": "Serverless App Initialization Failed",
            "details": err_msg
        }

app = app
