"""
FraudShield Database Service

Encapsulates all database operations for transactions, users, and audit logs.
Replaces in-memory storage with SQLAlchemy-based persistence.
"""

from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db_models import Transaction, AuditLog, User
from app.database import SessionLocal


class DatabaseService:
    """Service for managing database operations."""

    @staticmethod
    def get_db() -> Session:
        """Get a new database session."""
        return SessionLocal()

    @staticmethod
    def create_transaction(
        db: Session,
        amount: float,
        payee: str,
        timestamp: datetime,
        reference: str,
        payee_is_new: bool,
        risk_score: float,
        risk_level: str,
        factors: list,
        confidence: Optional[float] = None,
        explanation: Optional[str] = None,
        risk_factors_detailed: Optional[list] = None,
        recommended_action: Optional[str] = None,
        account_id: str = 'UNKNOWN',
        location_country: Optional[str] = None,
        location_lat: Optional[float] = None,
        location_lon: Optional[float] = None,
    ) -> Transaction:
        """
        Create a new transaction record in the database.

        Args:
            db: Database session
            amount: Transaction amount
            payee: Payee name
            timestamp: Transaction timestamp
            reference: Transaction reference
            payee_is_new: Whether this is a new payee
            risk_score: Calculated risk score
            risk_level: Risk level (high/medium/low)
            factors: List of triggered risk factors
            confidence: Confidence level (optional, generated later)
            explanation: Explanation text (optional, generated later)
            risk_factors_detailed: Detailed factor descriptions (optional)
            recommended_action: Recommended action (optional)
            account_id: Account ID
            location_country: Location country
            location_lat: Location latitude
            location_lon: Location longitude

        Returns:
            Transaction: Created transaction object
        """
        try:
            transaction = Transaction(
                amount=amount,
                payee=payee,
                timestamp=timestamp,
                reference=reference,
                payee_is_new=payee_is_new,
                risk_score=risk_score,
                risk_level=risk_level,
                factors=factors,
                confidence=confidence,
                explanation=explanation,
                risk_factors_detailed=risk_factors_detailed,
                recommended_action=recommended_action,
                status="pending",
                account_id=account_id,
                location_country=location_country,
                location_lat=location_lat,
                location_lon=location_lon,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            # Create audit log entry
            DatabaseService.create_audit_log(
                db,
                transaction_id=transaction.id,
                action="created",
                details={
                    "amount": amount,
                    "payee": payee,
                    "risk_level": risk_level,
                    "account_id": account_id,
                },
            )

            return transaction
        except Exception as e:
            print(f"Warning: Could not create transaction: {e}")
            raise e
            transaction = Transaction(
                id=uuid.uuid4(),
                amount=amount,
                payee=payee,
                timestamp=timestamp,
                reference=reference,
                payee_is_new=payee_is_new,
                risk_score=risk_score,
                risk_level=risk_level,
                factors=factors,
                confidence=confidence,
                explanation=explanation,
                risk_factors_detailed=risk_factors_detailed,
                recommended_action=recommended_action,
                status="pending",
                created_at=datetime.utcnow(),
                account_id=account_id,
                location_country=location_country,
                location_lat=location_lat,
                location_lon=location_lon,
            )
            return transaction

    @staticmethod
    def get_transaction(db: Session, transaction_id: str) -> Optional[Transaction]:
        """Retrieve a transaction by ID."""
        try:
            return db.query(Transaction).filter(Transaction.id == str(transaction_id)).first()
        except Exception as e:
            print(f"Warning: Could not get transaction {transaction_id}: {e}")
            return None

    @staticmethod
    def list_transactions(
        db: Session, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Transaction], int]:
        """
        List all transactions with pagination.

        Args:
            db: Database session
            skip: Number of items to skip
            limit: Maximum items to return

        Returns:
            Tuple of (transactions list, total count)
        """
        try:
            query = db.query(Transaction).order_by(desc(Transaction.created_at))
            total = query.count()
            items = query.offset(skip).limit(limit).all()
            return items, total
        except Exception as e:
            # If database isn't available, return empty list
            print(f"Warning: Could not query transactions: {e}")
            return [], 0

    @staticmethod
    def get_account_history(db: Session, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get recent transactions for an account, ordered by timestamp desc."""
        try:
            return db.query(Transaction).filter(
                Transaction.account_id == account_id
            ).order_by(desc(Transaction.timestamp)).limit(limit).all()
        except Exception as e:
            print(f"Warning: Could not get account history: {e}")
            return []

    @staticmethod
    def list_account_transactions(db: Session, account_id: str, skip: int = 0, limit: int = 50) -> Tuple[List[Transaction], int]:
        """List all transactions for an account with pagination."""
        try:
            query = db.query(Transaction).filter(
                Transaction.account_id == account_id
            ).order_by(Transaction.timestamp)
            total = query.count()
            items = query.offset(skip).limit(limit).all()
            return items, total
        except Exception as e:
            print(f"Warning: Could not list account transactions: {e}")
            return [], 0

    @staticmethod
    def get_config(db: Session, key: str, default: str = '') -> str:
        from app.db_models import Config
        try:
            config = db.query(Config).filter(Config.key == key).first()
            return config.value if config else default
        except Exception:
            return default

    @staticmethod
    def set_config(db: Session, key: str, value: str) -> None:
        from app.db_models import Config
        try:
            config = db.query(Config).filter(Config.key == key).first()
            if config:
                config.value = value
            else:
                config = Config(key=key, value=value)
                db.add(config)
            db.commit()
        except Exception as e:
            print(f"Warning: Could not set config {key}: {e}")

    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: str,
        updates: dict,
        audit_action: Optional[str] = None,
        audit_details: Optional[dict] = None,
    ) -> Optional[Transaction]:
        """
        Update a transaction with new data.

        Args:
            db: Database session
            transaction_id: Transaction UUID
            updates: Dict of fields to update
            audit_action: Optional audit log action name
            audit_details: Optional audit log details

        Returns:
            Updated transaction or None if not found
        """
        transaction = DatabaseService.get_transaction(db, transaction_id)
        
        if not transaction:
            return None

        for key, value in updates.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)

        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)

        # Create audit log entry if action provided
        if audit_action:
            DatabaseService.create_audit_log(
                db,
                transaction_id=transaction.id,
                action=audit_action,
                details=audit_details or {},
            )

        return transaction

    @staticmethod
    def create_audit_log(
        db: Session,
        transaction_id: UUID,
        action: str,
        details: Optional[dict] = None,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            db: Database session
            transaction_id: Transaction UUID
            action: Action type (created, approved, rejected, viewed, etc)
            details: Additional details as JSON
            user_id: User who performed the action (optional)
            ip_address: IP address of the request (optional)
            user_agent: User agent string (optional)

        Returns:
            AuditLog: Created audit log entry
        """
        audit_log = AuditLog(
            transaction_id=transaction_id,
            action=action,
            details=details or {},
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log

    @staticmethod
    def get_audit_trail(db: Session, transaction_id: str) -> List[AuditLog]:
        """
        Get all audit log entries for a transaction.

        Args:
            db: Database session
            transaction_id: Transaction UUID

        Returns:
            List of AuditLog entries
        """
        try:
            uuid_obj = UUID(transaction_id) if isinstance(transaction_id, str) else transaction_id
            return (
                db.query(AuditLog)
                .filter(AuditLog.transaction_id == str(uuid_obj))
                .order_by(AuditLog.created_at)
                .all()
            )
        except (ValueError, TypeError):
            return []

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            email: User email
            hashed_password: Hashed password
            full_name: User's full name (optional)
            is_superuser: Whether user is a superuser

        Returns:
            User: Created user object
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User or None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            User or None
        """
        return db.query(User).filter(User.id == user_id).first()


# Singleton instance for convenience
db_service = DatabaseService()
