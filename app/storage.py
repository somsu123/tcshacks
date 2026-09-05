"""
FraudShield In-Memory Storage

Thread-safe storage for transactions using a dictionary.
"""

from datetime import datetime
from threading import Lock
from typing import Optional
import uuid


class TransactionStore:
    """Thread-safe in-memory storage for transactions."""

    def __init__(self):
        self._transactions: dict[str, dict] = {}
        self._audit_logs: dict[str, list[dict]] = {}  # transaction_id -> list of audit entries
        self._lock = Lock()

    def add(self, transaction_data: dict) -> str:
        """
        Add a new transaction and return its ID.

        Args:
            transaction_data: Transaction data dict

        Returns:
            str: Generated transaction ID
        """
        transaction_id = str(uuid.uuid4())
        with self._lock:
            self._transactions[transaction_id] = {
                **transaction_data,
                "id": transaction_id,
                "status": "pending",  # Default status
                "created_at": datetime.utcnow(),
            }
            # Log creation
            self._audit_logs[transaction_id] = [
                {
                    "timestamp": datetime.utcnow(),
                    "action": "created",
                    "details": f"Transaction created with amount £{transaction_data.get('amount', 0):.2f}"
                }
            ]
        return transaction_id

    def get(self, transaction_id: str) -> Optional[dict]:
        """
        Retrieve a single transaction by ID.

        Args:
            transaction_id: The transaction UUID

        Returns:
            dict or None: Transaction data if found
        """
        return self._transactions.get(transaction_id)

    def get_audit_trail(self, transaction_id: str) -> list[dict]:
        """
        Retrieve audit trail for a transaction.

        Args:
            transaction_id: The transaction UUID

        Returns:
            list: List of audit log entries
        """
        return self._audit_logs.get(transaction_id, [])

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """
        Retrieve paginated transactions sorted by created_at (newest first).

        Args:
            skip: Number of items to skip
            limit: Maximum items to return

        Returns:
            tuple: (list of transactions, total count)
        """
        with self._lock:
            all_items = list(self._transactions.values())
            total = len(all_items)
            all_items.sort(key=lambda x: x["created_at"], reverse=True)
            return all_items[skip : skip + limit], total

    def update(self, transaction_id: str, updates: dict, audit_action: Optional[str] = None, audit_details: str = "") -> bool:
        """
        Update a transaction with new data.

        Args:
            transaction_id: The transaction UUID
            updates: Dict of fields to update
            audit_action: Optional audit log action name (e.g., "approved", "rejected")
            audit_details: Optional details for audit log

        Returns:
            bool: True if update succeeded
        """
        with self._lock:
            if transaction_id in self._transactions:
                self._transactions[transaction_id].update(updates)
                
                # Log the update if action provided
                if audit_action and transaction_id in self._audit_logs:
                    self._audit_logs[transaction_id].append({
                        "timestamp": datetime.utcnow(),
                        "action": audit_action,
                        "details": audit_details
                    })
                
                return True
            return False

    def load_seed_data(self, seed_data: list[dict]) -> int:
        """
        Load seed data into the store.

        Args:
            seed_data: List of transaction dicts

        Returns:
            int: Number of transactions loaded
        """
        count = 0
        for item in seed_data:
            # Use provided ID if available, otherwise generate one
            if "id" in item:
                transaction_id = item["id"]
                with self._lock:
                    self._transactions[transaction_id] = {
                        **item,
                        "created_at": item.get("created_at", datetime.utcnow()),
                    }
                    # Initialize audit log
                    if transaction_id not in self._audit_logs:
                        self._audit_logs[transaction_id] = [
                            {
                                "timestamp": item.get("created_at", datetime.utcnow()),
                                "action": "created",
                                "details": "Seed transaction"
                            }
                        ]
            else:
                self.add(item)
            count += 1
        return count

    def clear(self) -> None:
        """Clear all transactions (useful for testing)."""
        with self._lock:
            self._transactions.clear()
            self._audit_logs.clear()
