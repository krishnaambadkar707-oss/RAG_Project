from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        if "/collections" in path:
            data = [
                {"id": 1, "name": "HR & Policy", "description": "Internal enterprise HR policies and leave guides"},
                {"id": 2, "name": "IT & Operations", "description": "IT setup, VPN access, and security guides"},
                {"id": 3, "name": "Engineering & Architecture", "description": "Core platform architecture specifications"}
            ]
        elif "/documents" in path:
            data = [
                {"id": 1, "filename": "Company_HR_Policy_Guide_2024.pdf", "status": "processed"},
                {"id": 2, "filename": "IT_Setup_and_Security_Handbook.pdf", "status": "processed"}
            ]
        else:
            data = {"status": "healthy", "database": "connected", "vector_store": "active"}
            
        self.wfile.write(json.dumps(data).encode('utf-8'))
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {
            "answer": "Based on official company documentation, employees receive standard health coverage, remote work allowance, and 20 days paid annual leave.",
            "sources": [{"filename": "Company_HR_Policy_Guide_2024.pdf", "page_number": 1, "section_title": "Leave Policy", "similarity_score": 0.95}],
            "conversation_id": 1,
            "latency_ms": 45.2
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
