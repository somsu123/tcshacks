"""Reset the database - clear all transactions and re-run migrations."""
import os
import sys

# Set working dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.db_models import Transaction, AuditLog, User

db = SessionLocal()
try:
    deleted_tx = db.query(Transaction).delete()
    deleted_audit = db.query(AuditLog).delete()
    db.commit()
    print(f"Cleared {deleted_tx} transactions, {deleted_audit} audit logs")
except Exception as e:
    print(f"Error clearing: {e}")
    db.rollback()
finally:
    db.close()
