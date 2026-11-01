import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("--- Starting API Test Flow ---")
    
    # 1. Register
    reg_data = {
        "name": "Test Student",
        "email": "student@test.com",
        "password": "password123"
    }
    print(f"\n1. Registering user: {reg_data['email']}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        if response.status_code == 200:
            print("Successfully registered!")
        else:
            print(f"Registration status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Login
    login_data = {
        "username": "student@test.com",
        "password": "password123"
    }
    print("\n2. Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Successfully logged in! Token received.")
    else:
        print(f"Login failed: {response.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Predict interaction
    predict_data = {
        "drug_a": "Aspirin",
        "drug_b": "Warfarin",
        "indication": "Pain and Blood thinning",
        "substance": "Tablet"
    }
    print(f"\n3. Predicting interaction between {predict_data['drug_a']} and {predict_data['drug_b']}...")
    response = requests.post(f"{BASE_URL}/predictions/predict", json=predict_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"Prediction Result: {result['severity_label']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Explanation: {result['explanation']}")
    else:
        print(f"Prediction failed: {response.text}")

    # 4. Get Dashboard Summary
    print("\n4. Fetching Dashboard Summary...")
    response = requests.get(f"{BASE_URL}/dashboard/summary", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"Total Predictions: {summary['total_predictions']}")
        print("Severity counts:")
        for key in ["major_severity_count", "moderate_severity_count", "minor_severity_count", "no_interaction_count"]:
            print(f" - {key}: {summary[key]}")
    else:
        print(f"Summary fetch failed: {response.text}")

    print("\n--- Test Flow Completed ---")

if __name__ == "__main__":
    # Wait a moment for server to be ready if needed
    test_flow()
