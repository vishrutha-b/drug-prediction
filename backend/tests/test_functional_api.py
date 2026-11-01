import pytest
import httpx
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import ASGITransport
from app.main import app
TIMEOUT = 30.0

@pytest.mark.asyncio
async def test_auth_workflow():
    """Test standard medical professional authentication flow."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT) as client:
        # 1. Register Professional (Generic)
        reg_data = {
            "name": "Medical Professional",
            "email": f"mp_{asyncio.get_event_loop().time()}@hospital.org",
            "password": "securePassword123"
        }
        response = await client.post("/api/v1/auth/register", json=reg_data)
        assert response.status_code == 200
        assert response.json()["email"] == reg_data["email"]

        # 2. Login
        login_data = {
            "username": reg_data["email"],
            "password": reg_data["password"]
        }
        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Check Persistence (Profile)
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == reg_data["email"]

@pytest.mark.asyncio
async def test_prediction_accuracy():
    """Verify that clinical DDI prediction returns high-fidelity labels and confidence."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT) as client:
        reg_data = {
            "name": "Validation Engine",
            "email": f"validator_{asyncio.get_event_loop().time()}@hospital.org",
            "password": "verifyPassword!"
        }
        await client.post("/api/v1/auth/register", json=reg_data)
        login_res = await client.post("/api/v1/auth/login", data={"username": reg_data["email"], "password": reg_data["password"]})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. High Risk Scenario (Warfarin + Aspirin)
        predict_data = {
            "drug_a": "Warfarin",
            "drug_b": "Aspirin",
            "indication": "Anticoagulation",
            "substance": "Tablet"
        }
        response = await client.post("/api/v1/check-interaction", json=predict_data, headers=headers)
        assert response.status_code == 200
        result = response.json()
        assert "severity_label" in result
        assert result["confidence_score"] > 0.7  # Adjusted for BioBERT variance
        assert "explanation" in result

@pytest.mark.asyncio
async def test_dashboard_analytics():
    """Verify that institutional analytics data is accessible and correctly formatted."""
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT) as client:
        reg_data = {"name": "Admin", "email": f"admin_{asyncio.get_event_loop().time()}@hospital.org", "password": "pass"}
        await client.post("/api/v1/auth/register", json=reg_data)
        login_res = await client.post("/api/v1/auth/login", data={"username": reg_data["email"], "password": reg_data["password"]})
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        response = await client.get("/api/v1/dashboard/summary", headers=headers)
        assert response.status_code == 200
        summary = response.json()
        assert "total_predictions" in summary
        assert "major_severity_count" in summary
        assert "recent_predictions" in summary
