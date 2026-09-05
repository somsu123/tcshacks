"""Tests for input validation on transaction endpoints."""

import pytest


class TestTransactionValidation:
    """Test cases for TransactionCreate model validation."""

    @pytest.mark.asyncio
    async def test_missing_required_field_amount(self, client):
        """Should reject transaction without amount."""
        data = {"account_id": "TEST-123", "payee": "Test", "timestamp": "2026-01-10T10:00:00Z", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_field_payee(self, client):
        """Should reject transaction without payee."""
        data = {"account_id": "TEST-123", "amount": 100.00, "timestamp": "2026-01-10T10:00:00Z", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_field_timestamp(self, client):
        """Should reject transaction without timestamp."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "Test", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_required_field_reference(self, client):
        """Should reject transaction without reference."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "Test", "timestamp": "2026-01-10T10:00:00Z"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_amount_negative(self, client):
        """Should reject transaction with negative amount."""
        data = {"account_id": "TEST-123", "amount": -100.00, "payee": "Test", "timestamp": "2026-01-10T10:00:00Z", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_timestamp_format(self, client):
        """Should reject transaction with invalid timestamp."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "Test", "timestamp": "not-a-date", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_payee(self, client):
        """Should reject transaction with empty payee."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "", "timestamp": "2026-01-10T10:00:00Z", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_reference(self, client):
        """Should reject transaction with empty reference."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "Test", "timestamp": "2026-01-10T10:00:00Z", "reference": ""}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_page_size_over_limit(self, client):
        """Should reject page_size over 100."""
        response = await client.get("/transactions?page_size=200")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_payee_is_new_defaults_to_false(self, client):
        """payee_is_new should default to False if not provided."""
        data = {"account_id": "TEST-123", "amount": 100.00, "payee": "Test", "timestamp": "2026-01-10T10:00:00Z", "reference": "Test"}
        response = await client.post("/transactions", json=data)
        assert response.status_code == 201
        assert response.json()["risk_score"] == 0.0
