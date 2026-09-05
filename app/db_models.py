"""
FraudShield Database Models

SQLAlchemy ORM models for database tables.
Database-agnostic — works with both SQLite (local dev) and PostgreSQL (production).
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, JSON
import uuid

from app.database import Base


class Transaction(Base):
    """Transaction model for storing fraud detection records."""
    
    __tablename__ = "transactions"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    payee = Column(String(255), nullable=False, index=True)
    payee_is_new = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    reference = Column(String(100), nullable=False)
    account_id = Column(String(50), nullable=True, index=True)
    location_country = Column(String(2), nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    
    # Risk assessment
    risk_score = Column(Float, nullable=False, index=True)
    risk_level = Column(String(10), nullable=False, index=True)  # high, medium, low
    factors = Column(JSON, default=list)  # List of triggered factor codes
    
    # Explanation (generated lazily, cached here)
    confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    risk_factors_detailed = Column(JSON, nullable=True)  # Formatted factor descriptions
    recommended_action = Column(Text, nullable=True)
    
    # Action tracking — status values: pending, approved, rejected, hold
    status = Column(String(20), default="pending", index=True)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction(id={self.id}, payee={self.payee}, account={self.account_id}, risk_level={self.risk_level})>"


class User(Base):
    """User model for authentication."""
    
    __tablename__ = "fastapi_user"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(email={self.email})>"


class AuditLog(Base):
    """Audit log for tracking user actions."""
    
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    transaction_id = Column(String(36), nullable=True, index=True)
    action = Column(String(50), nullable=False)  # viewed, approved, rejected, hold, created, etc.
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, user_id={self.user_id})>"


class Config(Base):
    """Key-value configuration store for persisting settings like risk thresholds."""
    
    __tablename__ = "config"
    
    key = Column(String(100), primary_key=True)
    value = Column(String(500), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Config(key={self.key}, value={self.value})>"
