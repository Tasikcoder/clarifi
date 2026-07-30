# ClariFi — Decision Support System for Health Insurance Claim Adjudication

A domain-specific AI copilot that helps insurance claim officers make faster, consistent, and transparent adjudication decisions. Built entirely on **Snowflake**.

**Live App:** [https://asaiy-yhnomry-uw19292.snowflakecomputing.app](https://asaiy-yhnomry-uw19292.snowflakecomputing.app)

---

## Problem

Health insurance claim adjudication is:
- **Slow** — 15-30 minutes per claim for manual document review
- **Inconsistent** — 40% decision variance across officers
- **Opaque** — no structured framework, no audit trail

## Solution

ClariFi combines **Fuzzy AHP** (multi-criteria decision analysis) with **Snowflake Cortex AI** to provide:
- AI-extracted clinical facts from medical documents (PDF/DOCX)
- 4-criteria scoring with full transparency (Medical Necessity, Policy Compliance, Documentation, Cost)
- Similar claims retrieval via semantic search
- Partial approval, conditional approval, and clarification workflows
- Event-driven auto-scoring pipeline

## Snowflake Features Used (8)

| # | Feature | Usage |
|---|---------|-------|
| 1 | Cortex LLM (COMPLETE) | Extract clinical facts from medical documents |
| 2 | Cortex AI_CLASSIFY | Pre-screen documents, reject irrelevant before LLM |
| 3 | Cortex Search Service | Find similar historical claims (semantic search) |
| 4 | SPCS (Container Services) | Full-stack production deployment |
| 5 | Streams | Detect new claims in real-time |
| 6 | Tasks | Auto-score new claims every 1 minute |
| 7 | Stored Procedures | Business logic at database layer |
| 8 | Git Repository Integration | Source code connected to Snowflake |

## Architecture

```
Document Upload → AI_CLASSIFY (screen) → Cortex LLM (extract facts)
                                                    ↓
Claim Form → Snowflake Tables ← Extracted Facts → Fuzzy AHP Scoring
                                                    ↓
                              Cortex Search (similar claims) → Officer Decision
                                                    ↓
                              Status History + Audit Trail

Auto-Pipeline: Stream → Task (1 min) → Auto-score + status update
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 + Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | Snowflake |
| AI/LLM | Snowflake Cortex (mistral-large2) |
| Deployment | SPCS (nginx + gunicorn + supervisord) |
| Search | Cortex Search Service |

## Project Structure

```
clarifi/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Snowflake connection (SPCS OAuth + local .env)
│   ├── models/                 # Pydantic request/response models
│   ├── routers/                # API endpoints
│   │   ├── claims.py           # CRUD claims
│   │   ├── adjudication.py     # Fuzzy AHP scoring + similar claims
│   │   ├── analysis.py         # Document analysis (LLM extraction)
│   │   ├── decisions.py        # Workflow state machine
│   │   ├── documents.py        # File upload + auto-parse
│   │   └── import_data.py      # Import from PDF/DOCX
│   └── services/
│       ├── fuzzy_ahp_service.py          # Fuzzy AHP engine (TFN, defuzzification)
│       ├── adjudication_service.py       # Scoring orchestration + Cortex Search
│       ├── document_parser.py            # PDF (PyMuPDF) + DOCX parser
│       ├── document_screening_service.py # AI_CLASSIFY pre-screening
│       ├── extraction_service.py         # Cortex LLM fact extraction
│       └── decision_service.py           # State machine + audit trail
├── frontend/
│   └── src/app/
│       ├── page.tsx            # Dashboard
│       ├── claims/             # Claims list + detail + new claim
│       ├── import/             # Import documents (PDF/DOCX → data)
│       ├── policyholders/      # Policyholder management
│       ├── policies/           # Policy management
│       └── rules/              # Claim rules management
├── database/
│   └── schema.sql             # Full database schema (12 tables)
├── deploy/
│   ├── Dockerfile             # Multi-stage build
│   ├── nginx.conf             # Reverse proxy config
│   ├── supervisord.conf       # Process manager
│   └── spcs_deploy.sql        # SPCS service creation
└── docs/
    ├── sample_imports/         # Sample PDF files for import testing
    └── demo_script_3min.md    # Demo narration script
```

## Setup (Reproduce from Scratch)

### 1. Database
```sql
-- Run in Snowflake
-- Creates all tables, views, stream, and seed data
SOURCE @CLARIFI.CLAIMS.CLARIFI_GIT_REPO/branches/main/database/schema.sql;
```

### 2. Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
# Create .env with SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### 3. Deploy to SPCS
```powershell
# Build
docker build -f deploy/Dockerfile -t clarifi:latest .

# Tag + Push
docker tag clarifi:latest <account>.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
docker push <account>.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest

# Create/restart service (see deploy/spcs_deploy.sql)
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;
```

## Fuzzy AHP Methodology

Four criteria evaluated per claim:

| Criteria | Weight | What it measures |
|----------|--------|-----------------|
| Medical Necessity | 40% | Are procedures medically indicated for the diagnosis? |
| Policy Compliance | 25% | Does it comply with policy terms and exclusions? |
| Documentation | 20% | Are supporting documents complete? |
| Cost Reasonableness | 15% | Are costs within acceptable market range? |

Linguistic labels (Triangular Fuzzy Numbers):
- Not Justified (0, 0, 25)
- Poorly Justified (10, 25, 40)
- Partially Justified (25, 40, 60)
- Justified (50, 65, 80)
- Highly Consistent (75, 90, 100)

Decision thresholds: Score > 70 = Auto-Approve | 40-70 = Manual Review | < 40 = Auto-Reject

## License

MIT

---

*Built with Snowflake Cortex Code for the CoCo CLI Hackathon 2026*
