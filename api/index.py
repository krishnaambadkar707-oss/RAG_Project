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
    from mangum import Mangum
    from app.main import app
    
    handler = Mangum(app, lifespan="off")
    app = handler
except Exception as e:
    tb_str = traceback.format_exc()
    print(f"[Vercel Index Error] Failed to initialize Mangum/FastAPI app: {e}\n{tb_str}")
    def handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": f'{{"error": "Handler Init Failed", "details": "{str(e)}"}}'
        }
    app = handler


