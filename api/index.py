import os
import sys
import traceback

api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

root_dir = os.path.dirname(api_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from app.main import app
    app = app
except Exception as e:
    tb = traceback.format_exc()
    print(f"[Vercel Import Error] {e}\n{tb}")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def catch_all_error(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Vercel Python App Import Failure",
                "exception": str(e),
                "type": type(e).__name__,
                "traceback": tb
            }
        )
