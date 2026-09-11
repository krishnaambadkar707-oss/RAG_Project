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

import_error = None
try:
    from app.main import app as real_app
    app = real_app
except Exception as e:
    import_error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    print(f"[VERCEL IMPORT ERROR] {import_error}")
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    fallback_app = FastAPI()
    
    @fallback_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
    def catch_all_error(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to import FastAPI main app on Vercel",
                "error": import_error
            }
        )
    
    app = fallback_app
