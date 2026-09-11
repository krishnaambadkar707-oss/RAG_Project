import os
import sys
import traceback
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "python_version": sys.version,
        "cwd": os.getcwd()
    }

api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

for d in [api_dir, root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from app.main import app as main_app
    app = main_app
except Exception as e:
    err_str = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    print(f"[Vercel App Load Error] {err_str}")
    
    @app.get("/api/debug_error")
    def get_error():
        return {"error": err_str}
