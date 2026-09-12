import requests
import json

response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'email': 'test@company.com', 'password': 'testpass123'},
    timeout=10
)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test retrieval by checking the query response structure
print('=== Full Query Response ===')
result = requests.post(
    'http://localhost:8000/api/query',
    json={'question': 'vacation', 'collection_id': 1, 'top_k': 10},
    headers=headers,
    timeout=30
).json()

print(json.dumps(result, indent=2))
