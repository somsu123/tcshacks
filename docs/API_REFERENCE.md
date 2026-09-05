# FraudShield API Reference

## Overview

FraudShield AI provides a REST API for fraud detection and transaction analysis.

**Base URLs:**
- Development: `http://localhost:8000`
- Production: `https://api.fraudshield.ai` (planned)

**Content Type:** `application/json`

---

## Authentication

*Authentication is planned for future versions.*

Future implementation will use API key authentication:

```
Header: X-API-Key: your_api_key_here
```

---

## Endpoints

### Health Check

Check if the API is running and healthy.

```
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "FraudShield API",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` — Service is healthy

---

### List Transactions

Retrieve a paginated list of transactions.

```
GET /transactions
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |

**Example Request:**

```bash
curl "http://localhost:8000/transactions?page=1&page_size=10"
```

**Response:**

```json
{
  "items": [
    {
      "id": "demo_001",
      "amount": 4200.00,
      "payee": "ABC Holdings Ltd",
      "timestamp": "2026-01-05T03:47:00Z",
      "reference": "Invoice 2847",
      "risk_score": 0.80,
      "risk_level": "high",
      "created_at": "2026-01-05T03:47:15Z"
    }
  ],
  "total": 21,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | List of transactions |
| `total` | integer | Total number of transactions |
| `page` | integer | Current page number |
| `page_size` | integer | Items per page |
| `total_pages` | integer | Total number of pages |

**Transaction Object:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique transaction ID |
| `amount` | number | Transaction amount |
| `payee` | string | Recipient name |
| `timestamp` | string | ISO 8601 timestamp |
| `reference` | string | Payment reference |
| `risk_score` | number | Risk score (0.0 - 1.0) |
| `risk_level` | string | "high", "medium", or "low" |
| `created_at` | string | When transaction was analyzed |

**Status Codes:**
- `200 OK` — Success

---

### Get Transaction Detail

Retrieve a single transaction with full explanation.

```
GET /transactions/{id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Transaction ID |

**Example Request:**

```bash
curl "http://localhost:8000/transactions/demo_001"
```

**Response:**

```json
{
  "id": "demo_001",
  "amount": 4200.00,
  "payee": "ABC Holdings Ltd",
  "timestamp": "2026-01-05T03:47:00Z",
  "reference": "Invoice 2847",
  "risk_score": 0.80,
  "risk_level": "high",
  "created_at": "2026-01-05T03:47:15Z",
  "confidence": 99,
  "explanation": "This transaction triggered 3 fraud indicator(s).",
  "risk_factors": [
    "1. New Payee - First-ever transfer to this payee - no transaction history",
    "2. Unusual Timing - Initiated at 03:47 - outside normal hours (9am-6pm)",
    "3. Amount Spike - Amount (£4200) is 8.1x your average (£520)"
  ],
  "recommended_action": "Verify payee identity before releasing funds."
}
```

**Additional Fields (Detail Only):**

| Field | Type | Description |
|-------|------|-------------|
| `confidence` | integer | Confidence percentage (50-99) |
| `explanation` | string | Human-readable explanation |
| `risk_factors` | array | List of detected risk factors |
| `recommended_action` | string | Suggested action |

**Status Codes:**
- `200 OK` — Success
- `404 Not Found` — Transaction not found

---

### Create Transaction

Submit a new transaction for analysis.

```
POST /transactions
```

**Request Body:**

```json
{
  "amount": 4200.00,
  "payee": "ABC Holdings Ltd",
  "timestamp": "2026-01-05T03:47:00Z",
  "reference": "Invoice 2847",
  "payee_is_new": true
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | number | Yes | Transaction amount (> 0) |
| `payee` | string | Yes | Recipient name |
| `timestamp` | string | Yes | ISO 8601 timestamp |
| `reference` | string | Yes | Payment reference |
| `payee_is_new` | boolean | No | First transaction to this payee (default: false) |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 4200.00,
    "payee": "ABC Holdings Ltd",
    "timestamp": "2026-01-05T03:47:00Z",
    "reference": "Invoice 2847",
    "payee_is_new": true
  }'
```

**Response:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 4200.00,
  "payee": "ABC Holdings Ltd",
  "timestamp": "2026-01-05T03:47:00Z",
  "reference": "Invoice 2847",
  "risk_score": 0.80,
  "risk_level": "high",
  "created_at": "2026-01-09T10:30:00Z",
  "confidence": 99,
  "explanation": "This transaction triggered 3 fraud indicator(s).",
  "risk_factors": [
    "1. New Payee - First-ever transfer to this payee - no transaction history",
    "2. Unusual Timing - Initiated at 03:47 - outside normal hours (9am-6pm)",
    "3. Amount Spike - Amount (£4200) is 8.1x your average (£520)"
  ],
  "recommended_action": "Verify payee identity before releasing funds."
}
```

**Status Codes:**
- `201 Created` — Transaction created and analyzed
- `422 Unprocessable Entity` — Validation error

---

### Root Endpoint

Get API information.

```
GET /
```

**Response:**

```json
{
  "service": "FraudShield API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Error Responses

### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Not Found (404)

```json
{
  "detail": "Transaction not found"
}
```

### Internal Server Error (500)

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

*Rate limiting is planned for production.*

| Endpoint | Limit | Window |
|----------|-------|--------|
| `GET /transactions` | 1000/min | Per IP |
| `POST /transactions` | 100/min | Per IP |
| `GET /transactions/{id}` | 1000/min | Per IP |

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# List transactions
response = requests.get(f"{BASE_URL}/transactions")
transactions = response.json()

# Get transaction detail
response = requests.get(f"{BASE_URL}/transactions/demo_001")
detail = response.json()
print(f"Risk: {detail['risk_level']} ({detail['confidence']}% confidence)")

# Create transaction
new_transaction = {
    "amount": 1500.00,
    "payee": "New Supplier Ltd",
    "timestamp": "2026-01-09T14:30:00Z",
    "reference": "PO-12345",
    "payee_is_new": True
}
response = requests.post(f"{BASE_URL}/transactions", json=new_transaction)
result = response.json()
print(f"Risk: {result['risk_level']}")
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// List transactions
const response = await fetch(`${BASE_URL}/transactions`);
const { items } = await response.json();

// Get transaction detail
const detail = await fetch(`${BASE_URL}/transactions/demo_001`)
  .then(res => res.json());
console.log(`Risk: ${detail.risk_level} (${detail.confidence}% confidence)`);

// Create transaction
const newTransaction = {
  amount: 1500.00,
  payee: "New Supplier Ltd",
  timestamp: "2026-01-09T14:30:00Z",
  reference: "PO-12345",
  payee_is_new: true
};
const result = await fetch(`${BASE_URL}/transactions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(newTransaction)
}).then(res => res.json());
```

### cURL

```bash
# List transactions
curl "http://localhost:8000/transactions?page=1&page_size=10"

# Get transaction detail
curl "http://localhost:8000/transactions/demo_001"

# Create transaction
curl -X POST "http://localhost:8000/transactions" \
  -H "Content-Type: application/json" \
  -d '{"amount":1500,"payee":"Test Co","timestamp":"2026-01-09T14:30:00Z","reference":"Test","payee_is_new":true}'
```

---

## Webhooks (Planned)

Future versions will support webhooks for real-time notifications:

```
POST /webhooks/transaction
```

Contact us if you need webhook integration.
