import os
import requests

API_URL = "http://127.0.0.1:8000"

def test_api_upload():
    print("=== Testing Upload API Endpoint ===")
    sample_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_documents/HR_Policy.txt"))
    
    if not os.path.exists(sample_file_path):
        print(f"File not found: {sample_file_path}")
        return

    with open(sample_file_path, "rb") as f:
        files = {"file": ("HR_Policy_Test.txt", f, "text/plain")}
        data = {"collection_id": ""}
        res = requests.post(f"{API_URL}/documents/upload", files=files, data=data)
        
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")

if __name__ == "__main__":
    test_api_upload()
