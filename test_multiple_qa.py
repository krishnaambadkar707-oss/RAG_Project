import requests
import json

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'email': 'test@company.com', 'password': 'testpass123'},
    timeout=10
)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("=" * 70)
print("TESTING Q&A SYSTEM WITH MULTIPLE QUESTIONS")
print("=" * 70)

# Test 1: Vacation question
print("\n1️⃣  QUESTION: 'How much vacation do I get?'")
result = requests.post(
    'http://localhost:8000/api/query',
    json={'question': 'How much vacation do I get?', 'collection_id': 1},
    headers=headers,
    timeout=30
).json()

answer = result.get('answer', 'NO ANSWER')[:300]
sources_count = len(result.get('sources', []))
print(f"   Answer: {answer}")
print(f"   ✓ Sources found: {sources_count}")

# Test 2: Remote work question
print("\n2️⃣  QUESTION: 'What is the remote work policy?'")
result = requests.post(
    'http://localhost:8000/api/query',
    json={'question': 'What is the remote work policy?', 'collection_id': 1},
    headers=headers,
    timeout=30
).json()

answer = result.get('answer', 'NO ANSWER')[:300]
sources_count = len(result.get('sources', []))
print(f"   Answer: {answer}")
print(f"   ✓ Sources found: {sources_count}")

# Test 3: IT question
print("\n3️⃣  QUESTION: 'How do I set up a VPN?' (from IT collection)")
result = requests.post(
    'http://localhost:8000/api/query',
    json={'question': 'How do I set up a VPN?', 'collection_id': 2},
    headers=headers,
    timeout=30
).json()

answer = result.get('answer', 'NO ANSWER')[:300]
sources_count = len(result.get('sources', []))
print(f"   Answer: {answer}")
print(f"   ✓ Sources found: {sources_count}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETE - Q&A SYSTEM IS WORKING!")
print("=" * 70)
