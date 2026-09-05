"""Tests for the /health endpoint."""

import pytest


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_response_body(self, client):
        """Health endpoint should return correct JSON structure."""
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "FraudShield API"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Root endpoint should return service information."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "FraudShield API"
        assert data["version"] == "1.0.0"
