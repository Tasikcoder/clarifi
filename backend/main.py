from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import claims, documents, policyholders, policies, rules, adjudication, analysis, import_data, decisions

app = FastAPI(
    title="ClariFi API",
    description="Decision Support System for Health Insurance Claim Adjudication",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router, prefix="/api/claims", tags=["Claims"])
app.include_router(documents.router, prefix="/api/claims", tags=["Documents"])
app.include_router(policyholders.router, prefix="/api/policyholders", tags=["Policyholders"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])
app.include_router(adjudication.router, prefix="/api/adjudication", tags=["Adjudication"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Document Analysis"])
app.include_router(import_data.router, prefix="/api/import", tags=["Data Import"])
app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "clarifi-api"}
