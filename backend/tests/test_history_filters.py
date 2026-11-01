"""
tests/test_history_filters.py
==============================
Pytest test suite for GET /api/v1/history dynamic filtering.

Test cases
----------
1. filter by drug_a          – exact match returns only matching rows
2. filter by severity_label  – exact match on a label
3. filter by risk_score__gte – numeric range lower bound
4. filter by created_at range – date range using __gte and __lte
5. invalid field             – unknown field name → 400
6. invalid operator          – unrecognised __xyz operator → 400
7. pagination                – page/limit slicing and metadata
8. sorting                   – sort_by + order direction respected

The in-memory SQLite DB and FastAPI dependency override are set up
in conftest.py (auto-loaded by pytest). No DB configuration is needed here.
"""

import time
import pytest
import httpx
from httpx import ASGITransport
from app.main import app

TIMEOUT = 30.0


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client: httpx.AsyncClient) -> dict:
    """Register a unique user and return {'headers': ..., 'email': ...}."""
    ts = time.time()
    email = f"testuser_{ts}@clinic.org"
    await client.post("/api/v1/auth/register", json={
        "name": "Test Clinician",
        "email": email,
        "password": "TestPass!99",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": email,
        "password": "TestPass!99",
    })
    token = resp.json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "email": email}


async def _predict(client: httpx.AsyncClient, headers: dict, drug_a: str, drug_b: str, **kwargs) -> dict:
    """Fire a single prediction and return the JSON response."""
    payload = {"drug_a": drug_a, "drug_b": drug_b, **kwargs}
    resp = await client.post("/api/v1/check-interaction", json=payload, headers=headers)
    assert resp.status_code == 200, f"Prediction failed: {resp.text}"
    return resp.json()


# ---------------------------------------------------------------------------
# Test 1 – Filter by drug_a (exact match)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_drug_a():
    """Only predictions where drug_a == 'Warfarin' are returned."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        await _predict(client, h, "Warfarin", "Aspirin")
        await _predict(client, h, "Metformin", "Glipizide")  # should NOT appear

        resp = await client.get("/api/v1/history?drug_a=Warfarin", headers=h)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        for item in body["items"]:
            assert item["drug_a"] == "Warfarin", \
                f"Expected drug_a='Warfarin', got '{item['drug_a']}'"


# ---------------------------------------------------------------------------
# Test 2 – Filter by severity_label (exact match)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_severity_label():
    """Filter returns only records with the requested severity label."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        # Create a prediction; capture the actual severity the ML model returns.
        result = await _predict(client, h, "Warfarin", "Aspirin")
        actual_severity = result["severity_label"]

        resp = await client.get(
            f"/api/v1/history?severity_label={actual_severity}", headers=h
        )
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["severity_label"] == actual_severity


# ---------------------------------------------------------------------------
# Test 3 – Filter by risk_score__gte (numeric lower bound)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_risk_score_gte():
    """risk_score__gte=50 returns only records with risk_score >= 50."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        await _predict(client, h, "Warfarin", "Aspirin")   # likely high risk_score
        await _predict(client, h, "Vitamin C", "Zinc")     # likely low risk_score

        resp = await client.get("/api/v1/history?risk_score__gte=50", headers=h)
        assert resp.status_code == 200
        body = resp.json()
        for item in body["items"]:
            assert item["risk_score"] >= 50, \
                f"Expected risk_score >= 50, got {item['risk_score']}"


# ---------------------------------------------------------------------------
# Test 4 – Filter by created_at range
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_created_at_range():
    """
    created_at__gte + created_at__lte bracket today and return all predictions
    created during this test run.
    """
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        await _predict(client, h, "Aspirin", "Ibuprofen")

        # A date range that definitely includes 'right now'
        resp = await client.get(
            "/api/v1/history?created_at__gte=2020-01-01&created_at__lte=2099-12-31",
            headers=h,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1, "Expected at least one result within the broad date range"


# ---------------------------------------------------------------------------
# Test 5 – Invalid filter field → 400
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_filter_field():
    """Filtering on a disallowed field (e.g., user_id) must return HTTP 400."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        resp = await client.get("/api/v1/history?user_id=999", headers=h)
        assert resp.status_code == 400
        assert "Unknown or disallowed filter field" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Test 6 – Invalid operator → 400
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_operator():
    """An unrecognised operator suffix (e.g., __xyz) must return HTTP 400."""
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        resp = await client.get("/api/v1/history?risk_score__xyz=50", headers=h)
        assert resp.status_code == 400
        assert "Unknown operator" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Test 7 – Pagination
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pagination():
    """
    page=1&limit=1 returns exactly one item; page=2&limit=1 returns the next.
    The 'total', 'pages', 'page', and 'limit' metadata fields are correct.
    """
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        # Create 3 predictions so we have enough rows to paginate
        await _predict(client, h, "DrugA", "DrugB")
        await _predict(client, h, "DrugC", "DrugD")
        await _predict(client, h, "DrugE", "DrugF")

        # Page 1 of 1-item pages
        resp1 = await client.get("/api/v1/history?page=1&limit=1", headers=h)
        assert resp1.status_code == 200
        body1 = resp1.json()
        assert body1["page"] == 1
        assert body1["limit"] == 1
        assert len(body1["items"]) == 1
        assert body1["total"] >= 3
        assert body1["pages"] >= 3

        # Page 2 must contain a different item
        resp2 = await client.get("/api/v1/history?page=2&limit=1", headers=h)
        assert resp2.status_code == 200
        body2 = resp2.json()
        assert body2["page"] == 2
        assert len(body2["items"]) == 1
        assert body2["items"][0]["id"] != body1["items"][0]["id"]


# ---------------------------------------------------------------------------
# Test 8 – Sorting
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sorting():
    """
    sort_by=risk_score&order=asc returns items with risk_score in ascending order.
    sort_by=risk_score&order=desc returns them in descending order.
    """
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", timeout=TIMEOUT
    ) as client:
        auth = await _register_and_login(client)
        h = auth["headers"]

        # Create predictions that will receive different risk_scores from the ML engine
        await _predict(client, h, "Warfarin", "Aspirin")      # high risk_score
        await _predict(client, h, "Vitamin C", "Zinc")        # low risk_score
        await _predict(client, h, "Atorvastatin", "Niacin")   # mid risk_score

        # Ascending
        resp_asc = await client.get(
            "/api/v1/history?sort_by=risk_score&order=asc&limit=50", headers=h
        )
        assert resp_asc.status_code == 200
        items_asc = resp_asc.json()["items"]
        scores_asc = [item["risk_score"] for item in items_asc]
        assert scores_asc == sorted(scores_asc), \
            f"Ascending sort violated: {scores_asc}"

        # Descending
        resp_desc = await client.get(
            "/api/v1/history?sort_by=risk_score&order=desc&limit=50", headers=h
        )
        assert resp_desc.status_code == 200
        items_desc = resp_desc.json()["items"]
        scores_desc = [item["risk_score"] for item in items_desc]
        assert scores_desc == sorted(scores_desc, reverse=True), \
            f"Descending sort violated: {scores_desc}"
