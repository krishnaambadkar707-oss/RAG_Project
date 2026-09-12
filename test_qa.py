import requests

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'email': 'test@company.com', 'password': 'testpass123'},
    timeout=10
)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get documents
print('=== Documents in System ===')
docs = requests.get('http://localhost:8000/api/documents', headers=headers, timeout=10).json()
print(f'Total documents: {len(docs)}')
for d in docs:
    print(f"  {d['filename']} - {d['status']} (chunks: {d['chunk_count']})")

# Get collections
print('\n=== Collections ===')
colls = requests.get('http://localhost:8000/api/collections', headers=headers, timeout=10).json()
for c in colls:
    print(f"  ID {c['id']}: {c['name']} (docs: {c.get('document_count', 0)})")
