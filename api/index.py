import os
import sys
import json
import traceback
from http.server import BaseHTTPRequestHandler

api_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(api_dir)
backend_dir = os.path.join(root_dir, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            from app.main import app
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            path = self.path
            res = client.get(path)
            
            # If path was not found under /api prefix, try without /api or vice versa
            if res.status_code == 404:
                alt_path = path[4:] if path.startswith("/api") else "/api" + path
                res_alt = client.get(alt_path)
                if res_alt.status_code != 404:
                    res = res_alt

            self.send_response(res.status_code)
            self.send_header('Content-type', res.headers.get('content-type', 'application/json'))
            self.end_headers()
            self.wfile.write(res.content)
        except Exception as e:
            tb = traceback.format_exc()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            err_data = {
                "error": "Vercel Python Invocation Exception",
                "exception": str(e),
                "type": type(e).__name__,
                "traceback": tb
            }
            self.wfile.write(json.dumps(err_data, indent=2).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b''
            
            from app.main import app
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            path = self.path
            headers = {"Content-Type": self.headers.get("Content-Type", "application/json")}
            res = client.post(path, content=body_bytes, headers=headers)
            
            if res.status_code == 404:
                alt_path = path[4:] if path.startswith("/api") else "/api" + path
                res_alt = client.post(alt_path, content=body_bytes, headers=headers)
                if res_alt.status_code != 404:
                    res = res_alt

            self.send_response(res.status_code)
            self.send_header('Content-type', res.headers.get('content-type', 'application/json'))
            self.end_headers()
            self.wfile.write(res.content)
        except Exception as e:
            tb = traceback.format_exc()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            err_data = {
                "error": "Vercel Python Invocation Exception",
                "exception": str(e),
                "type": type(e).__name__,
                "traceback": tb
            }
            self.wfile.write(json.dumps(err_data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
