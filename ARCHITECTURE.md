# FraudShield AI - System Architecture

## Overview

FraudShield AI is a fraud detection system designed for SMBs (Small and Medium Businesses). It combines rule-based anomaly detection with AI-powered explanations to provide actionable fraud alerts.

## Design Principles

1. **Provider Agnostic** — Swap AI providers without code changes
2. **Development First** — Works offline with mock providers
3. **Explainable** — Every alert includes plain-English reasoning
4. **Confidence Aware** — Alerts include confidence scores

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRAUDSHIELD AI                                  │
│                           System Architecture                                │
└─────────────────────────────────────────────────────────────────────────────┘

                                    USERS
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                  │
│                             (Next.js 14)                                     │
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│   │  Dashboard  │    │ Detail View │    │  Settings   │                    │
│   │             │    │             │    │             │                    │
│   │ • Stats     │    │ • Risk Badge│    │ • Theme     │                    │
│   │ • Table     │    │ • Factors   │    │ • Providers │                    │
│   │ • Filters   │    │ • Actions   │    │             │                    │
│   └─────────────┘    └─────────────┘    └─────────────┘                    │
│                                                                              │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTP/REST
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               API LAYER                                      │
│                            (FastAPI/Python)                                  │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                          REST Endpoints                              │   │
│   │                                                                      │   │
│   │  GET  /health              — Service health                         │   │
│   │  GET  /transactions        — List transactions                      │   │
│   │  POST /transactions        — Create transaction                     │   │
│   │  GET  /transactions/{id}   — Get detail with explanation            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICE LAYER                                     │
│                                                                              │
│   ┌───────────────────┐              ┌───────────────────┐                  │
│   │  Detection Engine │              │ Explanation Gen   │                  │
│   │                   │              │                   │                  │
│   │  • Rule scoring   │───────────▶ │  • Build context  │                  │
│   │  • Factor detect  │              │  • Call LLM       │                  │
│   │  • Risk classify  │              │  • Format output  │                  │
│   └─────────┬─────────┘              └─────────┬─────────┘                  │
│             │                                  │                             │
└─────────────┼──────────────────────────────────┼─────────────────────────────┘
              │                                  │
              ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROVIDER ABSTRACTION LAYER                             │
│                                                                              │
│   ┌─────────────────────────────┐    ┌─────────────────────────────┐       │
│   │     PatternMatcher          │    │       LLMProvider           │       │
│   │       (Interface)           │    │        (Interface)          │       │
│   └──────────────┬──────────────┘    └──────────────┬──────────────┘       │
│                  │                                   │                       │
│       ┌──────────┼──────────┐             ┌─────────┼─────────┐             │
│       ▼          ▼          ▼             ▼         ▼         ▼             │
│   ┌───────┐  ┌───────┐  ┌───────┐   ┌───────┐  ┌───────┐  ┌───────┐       │
│   │ Azure │  │ Local │  │ Mock  │   │ Azure │  │OpenAI │  │ Mock  │       │
│   │Search │  │ JSON  │  │       │   │OpenAI │  │  API  │  │       │       │
│   └───────┘  └───────┘  └───────┘   └───────┘  └───────┘  └───────┘       │
│                                                                              │
│   Config: PATTERN_PROVIDER=...       Config: LLM_PROVIDER=...               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Provider Abstraction

The provider layer decouples the application from specific AI services. This enables:

- **Development without API keys** using mock providers
- **Cost control** by switching to cheaper providers
- **Vendor flexibility** to change providers without code changes
- **Testing** with deterministic mock responses

### LLM Providers

```python
class LLMProvider(ABC):
    async def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse
    async def parse_email(self, from_addr: str, subject: str, body: str) -> EmailParseResult
    def health_check(self) -> bool
```

| Provider | Config Value | Use Case |
|----------|--------------|----------|
| Azure OpenAI | `azure_openai` | Production (competition requirement) |
| OpenAI API | `openai` | Development, alternative to Azure |
| Ollama | `ollama` | Local development, offline use |
| Mock | `mock` | Testing, CI/CD, demos |

### Pattern Providers

```python
class PatternMatcher(ABC):
    async def find_matching_patterns(self, risk_factors: list, context: dict) -> list[PatternMatch]
    def health_check(self) -> bool
```

| Provider | Config Value | Use Case |
|----------|--------------|----------|
| Azure AI Search | `azure_search` | Production (semantic matching) |
| Local JSON | `local_json` | Development (keyword matching) |
| Mock | `mock` | Testing (no matches) |

---

## Data Flow

### Transaction Analysis Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TRANSACTION ANALYSIS FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

 USER                    FRONTEND                 API                  PROVIDERS
  │                         │                      │                        │
  │  1. Submit transaction  │                      │                        │
  │────────────────────────▶│                      │                        │
  │                         │  2. POST /transactions                        │
  │                         │─────────────────────▶│                        │
  │                         │                      │  3. Rule-based scoring │
  │                         │                      │───────────────────────▶│
  │                         │                      │  4. Detect factors     │
  │                         │                      │◀───────────────────────│
  │                         │                      │                        │
  │                         │                      │  5. Find patterns      │
  │                         │                      │───────────────────────▶│
  │                         │                      │  6. Matched patterns   │
  │                         │                      │◀───────────────────────│
  │                         │                      │                        │
  │                         │                      │  7. Generate explain   │
  │                         │                      │───────────────────────▶│
  │                         │                      │  8. Explanation        │
  │                         │                      │◀───────────────────────│
  │                         │                      │                        │
  │                         │  9. Transaction + explanation                 │
  │                         │◀─────────────────────│                        │
  │  10. Display result     │                      │                        │
  │◀────────────────────────│                      │                        │
```

### Response Time Budget

| Component | Target | Notes |
|-----------|--------|-------|
| Frontend render | ~100ms | Client-side |
| API processing | ~50ms | Routing, validation |
| Rule scoring | ~10ms | In-memory |
| Pattern matching | ~200ms | Local JSON or AI Search |
| LLM explanation | ~1-1.5s | GPT-4 or mock |
| **Total** | **~1.4-1.9s** | Under 2 seconds |

---

## Component Details

### Frontend (Next.js 14)

```
frontend/
├── app/                      # App Router pages
│   ├── page.tsx             # Dashboard
│   ├── transactions/[id]/   # Detail page
│   └── layout.tsx           # Root layout
├── components/
│   ├── ui/                  # Base components
│   ├── dashboard/           # Dashboard components
│   └── detail/              # Detail page components
├── lib/
│   ├── api.ts              # API client
│   ├── types.ts            # TypeScript types
│   └── utils.ts            # Utilities
└── hooks/
    ├── use-transactions.ts  # List hook
    └── use-transaction.ts   # Detail hook
```

**Key Features:**
- Server components for initial render
- SWR for client-side data fetching
- Framer Motion for animations
- next-themes for dark/light mode

### Backend (FastAPI)

```
app/
├── main.py                  # Application entry
├── config.py               # Configuration
├── models.py               # Pydantic schemas
├── storage.py              # Data storage
├── providers/
│   ├── __init__.py         # Provider factory
│   ├── llm/                # LLM providers
│   └── patterns/           # Pattern providers
├── services/
│   ├── anomaly_detector.py # Detection logic
│   └── explanation_generator.py
└── data/
    ├── demo_transactions.json
    └── fraud_patterns.json
```

**Key Features:**
- Async/await throughout
- Pydantic validation
- Provider abstraction
- In-memory storage (MVP)

---

## Deployment Architecture

### Local Development

```
┌─────────────────────┐     ┌─────────────────────┐
│   Frontend          │     │   Backend           │
│   localhost:3000    │────▶│   localhost:8000    │
│                     │     │                     │
│   npm run dev       │     │   uvicorn app.main  │
└─────────────────────┘     └─────────────────────┘

Providers: mock + local_json (no external services)
```

### Production (Azure)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AZURE CLOUD                              │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Azure Static    │    │ Azure App       │                    │
│  │ Web Apps        │    │ Service         │                    │
│  │                 │    │                 │                    │
│  │ Frontend        │───▶│ Backend API     │                    │
│  │ (Next.js)       │    │ (FastAPI)       │                    │
│  └─────────────────┘    └────────┬────────┘                    │
│                                  │                              │
│         ┌────────────────────────┼────────────────────────┐    │
│         │                        │                        │    │
│         ▼                        ▼                        ▼    │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐│
│  │Azure OpenAI │         │ Azure AI    │         │ Azure       ││
│  │             │         │ Search      │         │ Cosmos DB   ││
│  │ GPT-4       │         │             │         │ (Future)    ││
│  └─────────────┘         └─────────────┘         └─────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

1. **API Keys** — Never committed, stored in environment variables
2. **Input Validation** — All inputs validated via Pydantic
3. **CORS** — Configured for allowed origins only
4. **Rate Limiting** — Planned for production
5. **Data Encryption** — TLS in transit, encryption at rest (production)

See [SECURITY.md](SECURITY.md) for full security documentation.

---

## Future Enhancements

### Version 1.1
- API versioning (`/api/v1/`)
- Batch upload endpoint
- Email parsing endpoint
- Export functionality
- User feedback loop

### Version 2.0
- Persistent storage (Cosmos DB)
- Accounting software integrations
- Real-time webhook processing
- Multi-tenancy

See the full roadmap in the project documentation.
