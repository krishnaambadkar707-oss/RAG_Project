import os
import sys
import traceback

api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from app.main import app
    app = app
except Exception as e:
    tb_str = traceback.format_exc()
    print(f"[Vercel Index Error] Failed to import app.main: {e}\n{tb_str}")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def error_fallback(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Vercel Python Import Exception",
                "exception": str(e),
                "type": type(e).__name__,
                "traceback": tb_str
            }
        )

