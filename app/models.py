"""
FraudShield Pydantic Models

Defines request/response schemas for the API.
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    """Input model for creating a new transaction."""

    account_id: str = Field(..., min_length=1, description="Account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in GBP")
    payee: str = Field(..., min_length=1, max_length=255, description="Payee name")
    timestamp: datetime = Field(..., description="Transaction timestamp (ISO 8601)")
    reference: str = Field(..., min_length=1, max_length=100, description="Transaction reference")
    payee_is_new: bool = Field(default=False, description="Whether this is a new payee")
    location_country: Optional[str] = Field(None, description="ISO country code")
    location_lat: Optional[float] = Field(None, description="Latitude")
    location_lon: Optional[float] = Field(None, description="Longitude")

    model_config = {
        "json_schema_extra": {
            "example": {
                "account_id": "ACC-123456",
                "amount": 4200.00,
                "payee": "ABC Holdings Ltd",
                "timestamp": "2026-01-05T03:47:00Z",
                "reference": "Invoice 2847",
                "payee_is_new": True,
                "location_country": "GB",
                "location_lat": 51.5074,
                "location_lon": -0.1278
            }
        }
    }


class TransactionResponse(BaseModel):
    """Response model for transaction list view."""

    id: str = Field(..., description="Unique transaction ID")
    account_id: str = Field(..., description="Account identifier")
    amount: float = Field(..., description="Transaction amount in GBP")
    payee: str = Field(..., description="Payee name")
    timestamp: datetime = Field(..., description="Transaction timestamp")
    reference: str = Field(..., description="Transaction reference")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score (0-1)")
    risk_level: Literal["high", "medium", "low"] = Field(..., description="Risk classification")
    created_at: datetime = Field(..., description="When the transaction was recorded")
    location_country: Optional[str] = Field(None)
    status: str = Field(default="pending", description="Transaction status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "account_id": "ACC-123456",
                "amount": 4200.00,
                "payee": "ABC Holdings Ltd",
                "timestamp": "2026-01-05T03:47:00Z",
                "reference": "Invoice 2847",
                "risk_score": 0.80,
                "risk_level": "high",
                "created_at": "2026-01-05T03:47:15Z",
                "location_country": "GB",
                "status": "pending"
            }
        }
    }


class TransactionDetailResponse(TransactionResponse):
    """Response model for transaction detail view with full explanation."""

    confidence: int = Field(..., ge=0, le=99, description="Confidence percentage (50-99)")
    explanation: str = Field(..., description="Summary explanation")
    risk_factors: list[str] = Field(default_factory=list, description="List of risk factors")
    recommended_action: str = Field(..., description="Recommended action to take")
    status: str = Field(default="pending", description="Transaction status (pending, approved, rejected)")
    reviewed_by: Optional[str] = Field(default=None, description="User who reviewed the transaction")
    reviewed_at: Optional[datetime] = Field(default=None, description="When the transaction was reviewed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "account_id": "ACC-123456",
                "amount": 4200.00,
                "payee": "ABC Holdings Ltd",
                "timestamp": "2026-01-05T03:47:00Z",
                "reference": "Invoice 2847",
                "risk_score": 0.80,
                "risk_level": "high",
                "created_at": "2026-01-05T03:47:15Z",
                "location_country": "GB",
                "status": "pending",
                "confidence": 90,
                "explanation": "This transaction triggered 3 fraud indicator(s).",
                "risk_factors": [
                    "1. New Payee - First-ever transfer to this payee - no transaction history",
                    "2. Unusual Timing - Initiated at 03:47 - outside normal hours (9am-6pm)",
                    "3. Amount Spike - Amount (£4200) is 8.1x your average (£520)"
                ],
                "recommended_action": "Verify payee identity before releasing funds."
            }
        }
    }


class PaginatedResponse(BaseModel):
    """Paginated response wrapper for transaction lists."""

    items: list[TransactionResponse] = Field(..., description="List of transactions")
    total: int = Field(..., ge=0, description="Total number of transactions")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    timestamp: datetime = Field(..., description="When the action occurred")
    action: str = Field(..., description="Action taken (created, approved, rejected, viewed)")
    details: dict = Field(default_factory=dict, description="Additional details about the action")


class TransactionAuditResponse(BaseModel):
    """Audit trail for a transaction."""

    transaction_id: str = Field(..., description="Transaction ID")
    audit_trail: list[AuditLogEntry] = Field(..., description="List of audit log entries")

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

class RiskThresholdUpdate(BaseModel):
    high: float = Field(..., ge=0, le=1, description="High risk threshold (0-1)")
    medium: float = Field(..., ge=0, le=1, description="Medium risk threshold (0-1)")

class RiskThresholdResponse(BaseModel):
    high: float
    medium: float
