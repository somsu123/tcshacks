"""
FraudShield API

FastAPI-based fraud detection service that analyzes transactions
and provides risk assessments with AI-generated explanations.
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.auth_routes import router as auth_router
from app.auth import get_current_user, OptionalAuthBackend
from app.config import RISK_THRESHOLDS
from app.models import (
    HealthResponse,
    PaginatedResponse,
    TransactionCreate,
    TransactionDetailResponse,
    TransactionResponse,
    AuditLogEntry,
    TransactionAuditResponse,
    RiskThresholdUpdate,
    RiskThresholdResponse,
)
from app.services.anomaly_detector import (
    AnomalyDetectorProtocol,
    get_anomaly_detector,
    TransactionValidationError,
)
from app.services.explanation_generator import (
    ExplanationGeneratorProtocol,
    get_explanation_generator,
)
from app.services.database_service import db_service
from app.database import get_db
from app.db_models import User


def get_risk_level(score: float) -> str:
    """Map risk score to risk level."""
    if score >= RISK_THRESHOLDS["high"]:
        return "high"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "medium"
    return "low"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load seed data on startup."""
    seed_file = Path(__file__).parent / "data" / "demo_transactions.json"
    db = None
    
    try:
        db = db_service.get_db()
        
        if seed_file.exists():
            with open(seed_file) as f:
                seed_data = json.load(f)

                detector = get_anomaly_detector()
                generator = get_explanation_generator()
                
                count = 0
                for item in seed_data:
                    # Convert timestamp string to datetime
                    if isinstance(item.get("timestamp"), str):
                        item["timestamp"] = datetime.fromisoformat(
                            item["timestamp"].replace("Z", "+00:00")
                        )

                    item.setdefault('account_id', 'DEMO_ACCT_001')

                    # Skip if transaction already exists
                    existing = db_service.get_transaction(db, item.get("id"))
                    if existing:
                        continue

                    # Calculate risk score and factors
                    risk_score, factors = detector.calculate_risk_score(item)
                    risk_level = get_risk_level(risk_score)
                    
                    # Generate explanation
                    explanation_data = generator.generate_explanation(
                        transaction=item,
                        risk_score=risk_score,
                        factors=factors,
                    )

                    # Create transaction with all data
                    db_service.create_transaction(
                        db,
                        account_id=item.get("account_id", "DEMO_ACCT_001"),
                        amount=item["amount"],
                        payee=item["payee"],
                        timestamp=item["timestamp"],
                        reference=item["reference"],
                        payee_is_new=item.get("payee_is_new", False),
                        location_country=item.get("location_country"),
                        location_lat=item.get("location_lat"),
                        location_lon=item.get("location_lon"),
                        risk_score=risk_score,
                        risk_level=risk_level,
                        factors=factors,
                        confidence=explanation_data.get("confidence"),
                        explanation=explanation_data.get("explanation"),
                        risk_factors_detailed=explanation_data.get("risk_factors"),
                        recommended_action=explanation_data.get("recommended_action"),
                    )
                    count += 1
                
                print(f"FraudShield: Loaded {count} seed transactions into database")
    except Exception as e:
        print(f"FraudShield: Warning - Could not load seed data: {e}")
        print("FraudShield: Running without seed data. Database may not be available.")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass
    
    yield
    print("FraudShield: Shutting down")


# Initialize FastAPI app
app = FastAPI(
    title="FraudShield API",
    description="AI-powered fraud detection for financial transactions",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication routes
app.include_router(auth_router)


@app.get("/", tags=["Root"])
async def root():
    """API root - service information."""
    return {
        "service": "FraudShield API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for Azure App Service."""
    return HealthResponse(status="healthy", service="FraudShield API")


@app.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=201,
    tags=["Transactions"],
    summary="Submit a new transaction for fraud analysis",
)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    detector: AnomalyDetectorProtocol = Depends(get_anomaly_detector),
):
    """
    Submit a new transaction for fraud detection analysis.

    The transaction will be analyzed and assigned a risk score between 0 and 1,
    with a corresponding risk level (high, medium, low).
    """
    # Prepare transaction data
    transaction_data = transaction.model_dump()
    
    account_id = transaction_data.get('account_id', 'UNKNOWN')
    location_country = transaction_data.get('location_country')
    location_lat = transaction_data.get('location_lat')
    location_lon = transaction_data.get('location_lon')

    history = db_service.get_account_history(db, account_id)
    history_dicts = [{'amount': h.amount, 'timestamp': h.timestamp, 'location_lat': getattr(h, 'location_lat', None), 'location_lon': getattr(h, 'location_lon', None), 'location_country': getattr(h, 'location_country', None)} for h in history]

    try:
        risk_score, factors = detector.calculate_risk_score(transaction_data, history_dicts)
    except TransactionValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    risk_level = get_risk_level(risk_score)

    # Create transaction in database
    db_transaction = db_service.create_transaction(
        db,
        account_id=account_id,
        amount=transaction_data["amount"],
        payee=transaction_data["payee"],
        timestamp=transaction_data["timestamp"],
        reference=transaction_data["reference"],
        payee_is_new=transaction_data.get("payee_is_new", False),
        location_country=location_country,
        location_lat=location_lat,
        location_lon=location_lon,
        risk_score=risk_score,
        risk_level=risk_level,
        factors=factors,
    )

    return TransactionResponse(
        id=str(db_transaction.id),
        amount=db_transaction.amount,
        payee=db_transaction.payee,
        timestamp=db_transaction.timestamp,
        reference=db_transaction.reference,
        risk_score=db_transaction.risk_score,
        risk_level=db_transaction.risk_level,
        created_at=db_transaction.created_at,
        account_id=str(getattr(db_transaction, 'account_id', 'UNKNOWN')),
        location_country=getattr(db_transaction, 'location_country', None),
        status=getattr(db_transaction, 'status', 'pending')
    )


@app.get(
    "/transactions",
    response_model=PaginatedResponse,
    tags=["Transactions"],
    summary="Get all transactions with risk scores",
)
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of all transactions with their risk scores.

    Results are sorted by creation date (newest first).
    """
    skip = (page - 1) * page_size
    items, total = db_service.list_transactions(db, skip=skip, limit=page_size)

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=[
            TransactionResponse(
                id=str(item.id),
                amount=item.amount,
                payee=item.payee,
                timestamp=item.timestamp,
                reference=item.reference,
                risk_score=item.risk_score,
                risk_level=item.risk_level,
                created_at=item.created_at,
                account_id=str(getattr(item, 'account_id', 'UNKNOWN')),
                location_country=getattr(item, 'location_country', None),
                status=getattr(item, 'status', 'pending')
            )
            for item in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get(
    "/transactions/{transaction_id}",
    response_model=TransactionDetailResponse,
    tags=["Transactions"],
    summary="Get transaction details with full explanation",
)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    detector: AnomalyDetectorProtocol = Depends(get_anomaly_detector),
    generator: ExplanationGeneratorProtocol = Depends(get_explanation_generator),
):
    """
    Retrieve a single transaction with its full fraud analysis explanation.

    The response includes the risk assessment explanation, confidence level,
    identified risk factors, and recommended action.
    """
    transaction = db_service.get_transaction(db, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    # Get stored risk data or recalculate
    risk_score = transaction.risk_score
    factors = transaction.factors or []
    
    # Use cached explanation or generate new one
    if transaction.explanation:
        # Use cached explanation data
        explanation_data = {
            "confidence": transaction.confidence,
            "explanation": transaction.explanation,
            "risk_factors": transaction.risk_factors_detailed or [],
            "recommended_action": transaction.recommended_action,
            "risk_level": transaction.risk_level,
        }
    else:
        # Generate explanation and cache it
        transaction_dict = {
            "amount": transaction.amount,
            "payee": transaction.payee,
            "timestamp": transaction.timestamp,
            "reference": transaction.reference,
            "payee_is_new": transaction.payee_is_new,
        }
        
        explanation_data = generator.generate_explanation(
            transaction=transaction_dict,
            risk_score=risk_score,
            factors=factors,
        )
        
        # Cache the explanation
        db_service.update_transaction(
            db,
            transaction_id,
            {
                "confidence": explanation_data.get("confidence"),
                "explanation": explanation_data.get("explanation"),
                "risk_factors_detailed": explanation_data.get("risk_factors", []),
                "recommended_action": explanation_data.get("recommended_action"),
            },
        )

    return TransactionDetailResponse(
        id=str(transaction.id),
        amount=transaction.amount,
        payee=transaction.payee,
        timestamp=transaction.timestamp,
        reference=transaction.reference,
        risk_score=risk_score,
        risk_level=explanation_data["risk_level"],
        created_at=transaction.created_at,
        confidence=explanation_data["confidence"],
        explanation=explanation_data["explanation"],
        risk_factors=explanation_data["risk_factors"],
        recommended_action=explanation_data["recommended_action"],
        status=getattr(transaction, 'status', 'pending'),
        reviewed_by=transaction.reviewed_by,
        reviewed_at=transaction.reviewed_at,
        account_id=str(getattr(transaction, 'account_id', 'UNKNOWN')),
        location_country=getattr(transaction, 'location_country', None)
    )


@app.post(
    "/transactions/{transaction_id}/approve",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Mark transaction as approved/legitimate",
)
async def approve_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """
    Approve a transaction, marking it as legitimate.
    
    Updates the transaction status to 'approved'.
    """
    transaction = db_service.get_transaction(db, transaction_id)
    
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    # Update status
    updated = db_service.update_transaction(
        db,
        transaction_id,
        {
            "status": "approved",
            "reviewed_at": datetime.utcnow(),
        },
        audit_action="approved",
        audit_details={"status_change": f"{transaction.status} -> approved"},
    )
    
    return TransactionResponse(
        id=str(updated.id),
        amount=updated.amount,
        payee=updated.payee,
        timestamp=updated.timestamp,
        reference=updated.reference,
        risk_score=updated.risk_score,
        risk_level=updated.risk_level,
        created_at=updated.created_at,
        account_id=str(getattr(updated, 'account_id', 'UNKNOWN')),
        location_country=getattr(updated, 'location_country', None),
        status=getattr(updated, 'status', 'pending')
    )


@app.post(
    "/transactions/{transaction_id}/reject",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Mark transaction as fraud/rejected",
)
async def reject_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """
    Reject a transaction, marking it as fraud.
    
    Updates the transaction status to 'rejected'.
    """
    transaction = db_service.get_transaction(db, transaction_id)
    
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    # Update status
    updated = db_service.update_transaction(
        db,
        transaction_id,
        {
            "status": "rejected",
            "reviewed_at": datetime.utcnow(),
        },
        audit_action="rejected",
        audit_details={"status_change": f"{transaction.status} -> rejected"},
    )
    
    return TransactionResponse(
        id=str(updated.id),
        amount=updated.amount,
        payee=updated.payee,
        timestamp=updated.timestamp,
        reference=updated.reference,
        risk_score=updated.risk_score,
        risk_level=updated.risk_level,
        created_at=updated.created_at,
        account_id=str(getattr(updated, 'account_id', 'UNKNOWN')),
        location_country=getattr(updated, 'location_country', None),
        status=getattr(updated, 'status', 'pending')
    )


@app.post(
    "/transactions/{transaction_id}/hold",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Hold transaction for further review",
)
async def hold_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db_service.get_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail=f"Transaction with ID {transaction_id} not found")
    updated = db_service.update_transaction(
        db, transaction_id,
        {"status": "hold", "reviewed_at": datetime.utcnow()},
        audit_action="hold",
        audit_details={"status_change": f"{transaction.status} -> hold"},
    )
    return TransactionResponse(
        id=str(updated.id),
        amount=updated.amount,
        payee=updated.payee,
        timestamp=updated.timestamp,
        reference=updated.reference,
        risk_score=updated.risk_score,
        risk_level=updated.risk_level,
        created_at=updated.created_at,
        account_id=str(getattr(updated, 'account_id', 'UNKNOWN')),
        location_country=getattr(updated, 'location_country', None),
        status=getattr(updated, 'status', 'pending')
    )


@app.get("/accounts/{account_id}/transactions", response_model=PaginatedResponse, tags=["Accounts"])
async def get_account_transactions(
    account_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = db_service.list_account_transactions(db, account_id, skip=skip, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        items=[
            TransactionResponse(
                id=str(item.id),
                amount=item.amount,
                payee=item.payee,
                timestamp=item.timestamp,
                reference=item.reference,
                risk_score=item.risk_score,
                risk_level=item.risk_level,
                created_at=item.created_at,
                account_id=str(getattr(item, 'account_id', 'UNKNOWN')),
                location_country=getattr(item, 'location_country', None),
                status=getattr(item, 'status', 'pending')
            )
            for item in items
        ],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@app.get("/config/risk-thresholds", response_model=RiskThresholdResponse, tags=["Config"])
async def get_risk_thresholds(db: Session = Depends(get_db)):
    high = float(db_service.get_config(db, 'risk_threshold_high', str(RISK_THRESHOLDS['high'])))
    medium = float(db_service.get_config(db, 'risk_threshold_medium', str(RISK_THRESHOLDS['medium'])))
    return RiskThresholdResponse(high=high, medium=medium)


@app.put("/config/risk-thresholds", response_model=RiskThresholdResponse, tags=["Config"])
async def update_risk_thresholds(thresholds: RiskThresholdUpdate, db: Session = Depends(get_db)):
    db_service.set_config(db, 'risk_threshold_high', str(thresholds.high))
    db_service.set_config(db, 'risk_threshold_medium', str(thresholds.medium))
    RISK_THRESHOLDS['high'] = thresholds.high
    RISK_THRESHOLDS['medium'] = thresholds.medium
    return RiskThresholdResponse(high=thresholds.high, medium=thresholds.medium)


@app.post("/transactions/load-sample", tags=["Transactions"])
async def load_sample_data(db: Session = Depends(get_db)):
    """Reload the demo seed transactions (clears existing and re-seeds)."""
    seed_file = Path(__file__).parent / "data" / "demo_transactions.json"
    try:
        if not seed_file.exists():
            raise HTTPException(status_code=404, detail="Demo data file not found")

        with open(seed_file) as f:
            seed_data = json.load(f)

        detector = get_anomaly_detector()
        generator = get_explanation_generator()
        count = 0

        for item in seed_data:
            if isinstance(item.get("timestamp"), str):
                item["timestamp"] = datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                )
            item.setdefault("account_id", "DEMO_ACCT_001")

            # Always insert fresh (skip if UUID already present)
            existing = db_service.get_transaction(db, item.get("id", ""))
            if existing:
                continue

            risk_score, factors = detector.calculate_risk_score(item)
            risk_level = get_risk_level(risk_score)
            explanation_data = generator.generate_explanation(
                transaction=item,
                risk_score=risk_score,
                factors=factors,
            )

            db_service.create_transaction(
                db,
                account_id=item.get("account_id", "DEMO_ACCT_001"),
                amount=item["amount"],
                payee=item["payee"],
                timestamp=item["timestamp"],
                reference=item["reference"],
                payee_is_new=item.get("payee_is_new", False),
                location_country=item.get("location_country"),
                location_lat=item.get("location_lat"),
                location_lon=item.get("location_lon"),
                risk_score=risk_score,
                risk_level=risk_level,
                factors=factors,
                confidence=explanation_data.get("confidence"),
                explanation=explanation_data.get("explanation"),
                risk_factors_detailed=explanation_data.get("risk_factors"),
                recommended_action=explanation_data.get("recommended_action"),
            )
            count += 1

        return {"message": f"Loaded {count} sample transactions", "count": count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample data: {str(e)}")


@app.get(
    "/transactions/{transaction_id}/audit",
    response_model=TransactionAuditResponse,
    tags=["Transactions"],
    summary="Get audit trail for a transaction",
)
async def get_audit_trail(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve the complete audit trail for a transaction.
    
    Shows all actions taken on the transaction (creation, approvals, rejections, etc).
    
    NOTE: Audit trail data is included in the transaction detail response (status, reviewed_by, reviewed_at fields).
    This endpoint returns a simple empty trail as a placeholder until database migrations are fully applied.
    """
    try:
        transaction = db_service.get_transaction(db, transaction_id)
        
        if transaction is None:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found",
            )
        
        # For now, return an empty audit trail
        # TODO: Once audit_logs table is properly migrated, populate this with actual audit entries
        audit_entries = []
        
        # Add a synthetic "created" entry based on the transaction
        if transaction:
            audit_entries.append(
                AuditLogEntry(
                    timestamp=transaction.created_at,
                    action="created",
                    details={
                        "amount": float(transaction.amount),
                        "payee": transaction.payee,
                        "risk_level": transaction.risk_level,
                    }
                )
            )
            
            # Add approval/rejection entry if transaction has been reviewed
            if getattr(transaction, 'status', 'pending') != "pending" and transaction.reviewed_at:
                audit_entries.append(
                    AuditLogEntry(
                        timestamp=transaction.reviewed_at,
                        action=transaction.status,
                        details={
                            "reviewed_by": transaction.reviewed_by,
                            "status": transaction.status,
                        }
                    )
                )
        
        return TransactionAuditResponse(
            transaction_id=transaction_id,
            audit_trail=audit_entries
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_audit_trail: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
