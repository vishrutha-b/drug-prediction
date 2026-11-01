import requests

url = "http://localhost:8000/api/v1/check-interaction"

# Get token first
login_url = "http://localhost:8000/api/v1/auth/login"
resp = requests.post(login_url, data={"username": "admin@example.com", "password": "password123"})
token = resp.json().get("access_token")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("--- Test 1: Only drug_a and drug_b ---")
payload1 = {
    "drug_a": "Warfarin",
    "drug_b": "Fluconazole"
}
resp1 = requests.post(url, json=payload1, headers=headers)
print(f"Status: {resp1.status_code}")
print(f"Response: {resp1.text}")

print("\n--- Test 2: Full payload ---")
payload2 = {
    "drug_a": "Warfarin",
    "drug_b": "Fluconazole",
    "indication": "N/A",
    "substance": "N/A"
}
resp2 = requests.post(url, json=payload2, headers=headers)
print(f"Status: {resp2.status_code}")
print(f"Response: {resp2.text}")
