"""Tests for transaction endpoints."""

import pytest


class TestListTransactions:
    """Test cases for GET /transactions endpoint."""

    @pytest.mark.asyncio
    async def test_list_transactions_empty(self, client):
        """Should return empty list when no transactions exist."""
        response = await client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_transactions_after_create(self, client, valid_transaction_data):
        """Should return created transactions."""
        await client.post("/transactions", json=valid_transaction_data)
        response = await client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["payee"] == valid_transaction_data["payee"]

    @pytest.mark.asyncio
    async def test_list_transactions_pagination(self, client, valid_transaction_data):
        """Should support pagination parameters."""
        for i in range(5):
            tx_data = {**valid_transaction_data, "reference": f"Payment {i}"}
            await client.post("/transactions", json=tx_data)
        response = await client.get("/transactions?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    @pytest.mark.asyncio
    async def test_list_transactions_page_bounds(self, client):
        """Should validate page parameter bounds."""
        response = await client.get("/transactions?page=0")
        assert response.status_code == 422


class TestCreateTransaction:
    """Test cases for POST /transactions endpoint."""

    @pytest.mark.asyncio
    async def test_create_valid_transaction(self, client, valid_transaction_data):
        """Should create transaction and return 201."""
        response = await client.post("/transactions", json=valid_transaction_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["amount"] == valid_transaction_data["amount"]
        assert "risk_score" in data
        assert data["risk_level"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_create_transaction_low_risk(self, client, low_risk_transaction_data):
        """Low risk transaction should have low risk level."""
        response = await client.post("/transactions", json=low_risk_transaction_data)
        assert response.status_code == 201
        data = response.json()
        assert data["risk_level"] == "low"
        assert data["risk_score"] < 0.35

    @pytest.mark.asyncio
    async def test_create_transaction_high_risk(self, client, high_risk_transaction_data):
        """High risk transaction should have high risk level."""
        response = await client.post("/transactions", json=high_risk_transaction_data)
        assert response.status_code == 201
        data = response.json()
        assert data["risk_level"] == "high"
        assert data["risk_score"] >= 0.65

    @pytest.mark.asyncio
    async def test_create_transaction_medium_risk(self, client, medium_risk_transaction_data):
        """Medium risk transaction should have medium risk level."""
        response = await client.post("/transactions", json=medium_risk_transaction_data)
        assert response.status_code == 201
        data = response.json()
        assert data["risk_level"] == "medium"
        assert 0.35 <= data["risk_score"] < 0.65


class TestGetTransaction:
    """Test cases for GET /transactions/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_transaction_success(self, client, valid_transaction_data):
        """Should return transaction details for valid ID."""
        create_response = await client.post("/transactions", json=valid_transaction_data)
        transaction_id = create_response.json()["id"]
        response = await client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
        assert "explanation" in data
        assert "risk_factors" in data
        assert "recommended_action" in data

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, client):
        """Should return 404 for non-existent transaction ID."""
        response = await client.get("/transactions/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_transaction_detail_includes_explanation(self, client, high_risk_transaction_data):
        """Transaction detail should include AI explanation."""
        create_response = await client.post("/transactions", json=high_risk_transaction_data)
        transaction_id = create_response.json()["id"]
        response = await client.get(f"/transactions/{transaction_id}")
        data = response.json()
        assert len(data["risk_factors"]) > 0
        assert data["confidence"] >= 50
        assert data["recommended_action"] != ""
