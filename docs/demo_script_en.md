# ClariFi Demo Script — Decision Support System for Health Insurance Claim Adjudication

**Duration:** 10-15 minutes
**Base URL:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app
**Presenter:** [Name]

---

## OPENING (1-2 minutes)

> "Good [morning/afternoon], let me introduce ClariFi — a Decision Support System for health insurance claim adjudication. ClariFi combines Fuzzy AHP (Analytical Hierarchy Process) with Snowflake Cortex AI to help claim officers make faster, more consistent, and transparent decisions."

> "What makes ClariFi different: it's not a black box. Every decision is fully traceable — from the original document, through per-criteria scoring, to the final decision. And everything runs entirely on the Snowflake platform."

---

## PART 1: DASHBOARD OVERVIEW (1 minute)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/

> "On the dashboard, we can see the adjudication summary at a glance: how many claims were auto-approved, sent to manual review, or auto-rejected. The system has already processed claims automatically through our pipeline."

**Show:**
- Total Adjudications, Auto-Approve, Manual Review, Auto-Reject metric cards
- Average Score gauge

---

## PART 2: CLAIMS LIST (1 minute)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims

> "On the Claims page, we see all claims with their current status — green for Approved, yellow for Manual Review, red for Rejected, orange for Pending Clarification. Notice how the system has already automatically classified each claim based on its score."

**Highlight:**
- Color-coded status badges
- Variety: ISPA Rp 3.5M (simple), Appendicitis Rp 45M (complex), Cosmetic Rhinoplasty (rejected)
- Partial Approval: Ahmad Fauzi (claimed Rp 85M, approved Rp 65M — 76.5%)

---

## PART 3: IMPORT DATA VIA PDF (2-3 minutes)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/import

> "Before processing claims, we need master data. ClariFi can extract structured data directly from PDF documents using Snowflake Cortex AI. Let me demonstrate importing a new policyholder."

**Actions:**
1. Select type "Policyholder"
2. Upload `data_nasabah_rina.pdf`
3. Click "Extract & Preview"

> "Watch — the system reads the PDF, then Cortex LLM extracts structured data: name, national ID, date of birth, address — all automatically. The officer just reviews and clicks Save."

4. Review extracted data
5. Click "Save to Database"

> "Now let's import the insurance policy and claim rules as well."

6. Repeat for Policy (`kontrak_polis_rina.pdf`) and Claim Rules (`aturan_adjudikasi.pdf`)

**Key message:** "From unstructured documents to structured data — zero manual typing."

**Verify imported data:**
- Policyholders: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policyholders
- Policies: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policies
- Claim Rules: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/rules

---

## PART 3b: DOCUMENT SCREENING — REJECTING GARBAGE (1 minute)

**Stay on:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/import

> "But what if someone uploads an irrelevant document — a brochure, a personal photo, or a blank file? ClariFi has a pre-screening layer."

**Actions:**
1. Select type "Policyholder"
2. Upload a file that is NOT an insurance document (e.g., random text, advertisement, or blank PDF)
3. Click "Extract & Preview"

> "Notice — the system rejects this document BEFORE sending it to the LLM. The message says: 'Document rejected — not relevant to insurance claims'. This is critical for cost efficiency: we don't waste Cortex AI credits processing garbage."

**Key message:** "Pre-screening uses AI_CLASSIFY from Snowflake Cortex — saves cost, filters noise at the gate."

> "Two validation layers: first, check if the document has meaningful text content (reject blank or corrupt files). Second, AI classifies whether the document is relevant — medical report, invoice, claim form — or irrelevant like spam or personal photos."

---

## PART 4: SUBMIT A NEW CLAIM (2 minutes)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/new

> "Now let's simulate a new claim submission. Patient Rina Wulandari presents with Acute Gastritis, outpatient visit at RS Bethesda."

**Actions:** Fill the form:
- Policy ID: POL-006 (or the newly created one)
- Patient: Rina Wulandari
- Diagnosis: Gastritis Acute
- Service Type: Outpatient
- Provider: RS Bethesda Yogyakarta
- Line items: Consultation (Rp 300,000), Endoscopy (Rp 5,000,000), Medication (Rp 800,000)
- Upload supporting PDF documents

> "Notice during upload — the system immediately parses each document and detects its type: invoice, lab result, claim form. This auto-parse runs in real-time."

Click "Submit Claim"

---

## PART 5: AUTO-PIPELINE (1 minute)

**Stay on:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims

> "Behind the scenes, a Snowflake Stream detects the new claim. Within one minute, a scheduled Task automatically runs initial scoring. No manual action required."

**Action:** Wait briefly, then refresh the Claims page

> "Look — the claim that was just SUBMITTED has now changed status to [Manual Review/Approved]. This was done by the auto-pipeline with zero human intervention."

**Key message:** "Event-driven architecture — Stream detects, Task processes, automatically."

---

## PART 6: CLAIM DETAIL & ADJUDICATION (3-4 minutes)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0009

(Budi Santoso, ISPA / Upper Respiratory Infection, Rp 3.5M — status MANUAL_REVIEW)

> "Let's look at a claim in detail. Here the officer can see everything: patient data, claimed procedures, supporting documents with their parsing status."

### 6a. Document Analysis

> "First step: document analysis. The system uses Cortex LLM to extract clinical facts from documents — diagnosis, procedures, costs, lab findings, and potential red flags."

**Action:** Click "Document Analysis"

### 6b. Fuzzy AHP Adjudication

**Action:** Click "Run Adjudikasi"

> "Now we run the Fuzzy AHP scoring. The system evaluates 4 criteria:"
> - "Medical Necessity — is the procedure medically required for this diagnosis?"
> - "Policy Compliance — does it comply with the patient's policy terms?"
> - "Documentation Completeness — are all required documents present?"
> - "Cost Reasonableness — are the costs within acceptable range?"

> "Each criterion receives a fuzzy linguistic label — 'Justified', 'Highly Consistent', 'Partially Justified' — which is then converted to a numeric score through Triangular Fuzzy Numbers and centroid defuzzification."

**Show:**
- Score gauge (e.g., 60.33)
- Breakdown table: criteria, weight, label, TFN, defuzzified value, contribution, reason
- Decision: "Manual Review"

> "A score of 60.33 falls in the 40-70 range, meaning it requires manual review. The system doesn't auto-approve or auto-reject — it provides a recommendation, not the final decision. The human officer retains full authority."

### 6c. Similar Claims (Cortex Search)

> "Here's a powerful feature: Similar Claims. Using Cortex Search, the system finds historically similar claims based on diagnosis, procedures, and provider."

**Show:**
- "Similar Claims" panel with matching historical claims
- Their scores and decisions
- "A similar claim from Budi Santoso (Appendicitis) was approved with score 66"

> "This helps the officer make consistent decisions: how were similar claims decided in the past? Were they approved? What was their score? It's a consistency check powered by semantic search."

### 6d. Officer Decision

> "Armed with all this information — the score, the breakdown, document analysis, and similar claims — the officer can now make a well-informed decision."

**Actions:**
- Select "Approve (Full)" or "Approve with Conditions"
- Enter reason
- (Optional) For partial approval: enter approved amount
- Submit

---

## PART 7: PARTIAL APPROVAL (1 minute)

**Open:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0005

(Ahmad Fauzi, Acute Myocardial Infarction, Rp 85M — status APPROVED)

> "Here's an example of partial approval: Ahmad Fauzi's claim for a heart attack totaling Rp 85 million. The officer approved Rp 65 million — 76.5% — because the VVIP room charge was downgraded to VIP rate per policy entitlement."

**Show:**
- Total Claim: Rp 85,000,000
- Approved: Rp 65,000,000 (76.5%)
- Complete workflow timeline

> "This is a common real-world scenario that most systems can't handle — all-or-nothing approval. ClariFi supports nuanced decisions."

---

## PART 8: OTHER INTERESTING CLAIMS (optional)

If time permits, show additional cases:

- **Rejected Claim:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0004
  (Siti Rahayu, Cosmetic Rhinoplasty — auto-rejected score 16.66, cosmetic procedure)

- **Pending Clarification:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0007
  (Dewi Kartika, Vertigo — MRI needs additional justification)

- **Approved with Conditions:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0008
  (Rudi Hermawan, Cholecystitis — must submit pathology report within 14 days)

- **Emergency Case:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0010
  (Dewi Kartika, Perforated Appendicitis — emergency, significant cost)

---

## PART 9: SNOWFLAKE ARCHITECTURE (1-2 minutes)

> "Under the hood, ClariFi leverages 6 core Snowflake capabilities:"

| # | Feature | Usage |
|---|---------|-------|
| 1 | **Cortex LLM (COMPLETE)** | Extract clinical facts from medical documents |
| 2 | **Cortex AI_CLASSIFY** | Pre-screen documents: filter noise before expensive extraction |
| 3 | **Cortex Search** | Semantic similarity search for comparable claims |
| 4 | **SPCS (Container Services)** | Full-stack deployment (Next.js + FastAPI + nginx) |
| 5 | **Streams** | Real-time detection of new claims |
| 6 | **Tasks** | Auto-scoring pipeline (event-driven) |
| 7 | **Stored Procedures** | Business logic at the database layer |

> "Everything runs within the Snowflake ecosystem — no external dependencies. Data never leaves the platform. This is critical for healthcare data which is subject to strict privacy regulations."

---

## CLOSING (1 minute)

> "ClariFi demonstrates that Snowflake is not just a data warehouse — it's a complete platform for building AI-powered, production-ready applications. From ingestion (PDF parsing with Cortex), to processing (Fuzzy AHP + LLM scoring), to real-time automation (Streams + Tasks), to serving (SPCS) — all within a single, secure platform."

> "The Fuzzy AHP methodology provides mathematical rigor and transparency. The Cortex AI provides intelligence and automation. Together, they enable what we call 'Adjudication with Clarity' — which is exactly what ClariFi means."

> "Thank you. I'm happy to take questions."

---

## FULL LINK REFERENCE

| Page | URL |
|------|-----|
| Dashboard | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/ |
| Claims List | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims |
| New Claim | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/new |
| Import Documents | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/import |
| Policyholders | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policyholders |
| Policies | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policies |
| Claim Rules | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/rules |
| Detail: ISPA (manual review) | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0009 |
| Detail: Partial Approval | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0005 |
| Detail: Rejected (cosmetic) | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0004 |
| Detail: Pending Clarification | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0007 |
| Detail: Approved w/ Conditions | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0008 |
| Detail: Emergency | https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0010 |

---

## Q&A PREPARATION

**Q: How accurate is the scoring?**
> "Fuzzy AHP provides a structured mathematical framework — it's deterministic and auditable. The LLM provides document understanding. The combination is more reliable than either alone. In production, the model would be calibrated against historical adjudication decisions."

**Q: Can it handle different languages/document formats?**
> "Currently it processes Indonesian medical documents in PDF and DOCX format. Cortex LLM supports multiple languages, so extending to English or other languages requires only prompt adjustment, not architectural changes."

**Q: What about production readiness?**
> "This is an MVP. For production deployment, we'd add: role-based access control, detailed audit logging, integration with core insurance systems, SLA-based escalation, and fine-tuning the LLM for domain-specific accuracy."

**Q: How does the auto-pipeline handle errors?**
> "The Stream + Task pipeline includes fallback logic. If scoring fails, the claim stays in SUBMITTED status for manual processing. The system favors safety — it never auto-rejects without clear evidence."

**Q: Why Fuzzy AHP instead of pure ML/AI?**
> "Transparency and explainability. In regulated industries like insurance, you need to explain WHY a claim was rejected. Fuzzy AHP gives you per-criteria scores with human-readable labels. A pure neural network would be a black box that regulators won't accept."

---

## DEMO TIPS

1. **If Document Analysis fails** (seed data without parsed text): use a freshly submitted claim with uploaded PDF
2. **To show auto-pipeline**: submit a claim via UI, wait 1-2 minutes, refresh the page
3. **Best claims for detailed demo**: CLM-2026-0005 (partial approval) or CLM-2026-0010 (emergency appendicitis)
4. **Keep energy high** during the Extract & Preview step — there's a 5-10 second wait for LLM processing
5. **Emphasize the "why"**: every decision has a traceable reason chain
