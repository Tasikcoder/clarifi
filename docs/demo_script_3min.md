# ClariFi — 3-Minute Demo Script (Hackathon Submission Video)

**Duration:** Exactly 3 minutes
**Strategy:** Slide (30s) → Demo 1: Import + Screening (60s) → Demo 2: Adjudication + Similar Claims (70s) → Close (20s)
**Video tip:** Record screen at normal speed, then speed up loading/waiting parts to 2x in CapCut. Add TTS narration.

---

## [0:00 - 0:30] SLIDE: Problem + Solution + Architecture

**Show:** 1-2 PowerPoint slides (problem statement → architecture diagram)

**Narration (TTS):**

> "Health insurance companies process thousands of claims daily. Each takes 15 to 30 minutes of manual review, and 40 percent of decisions are inconsistent across officers."

> "ClariFi is a domain-specific AI copilot for claim adjudication. It combines Fuzzy AHP scoring with Snowflake Cortex AI — enabling faster, consistent, and fully transparent decisions. Built entirely on Snowflake, using seven platform capabilities: Cortex LLM, AI Classify, Cortex Search, SPCS, Streams, Tasks, and Stored Procedures."

**Visual:** Flash architecture diagram showing the 7 Snowflake features connected.

---

## [0:30 - 1:30] DEMO 1: Import PDF + Document Screening

**URL:** https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/import

**Narration:**

> [0:30] "Let's see ClariFi in action. First — importing master data from PDF documents."

**Action:** Select "Policyholder" → Upload `data_nasabah_rina.pdf` → Click "Extract & Preview"

> [0:40] "The system first screens the document using AI Classify — filtering out irrelevant files before sending to the LLM. This saves processing cost."

**Show:** Brief loading, then extracted data appears (name, ID, address, etc.)

> [0:55] "For valid documents, Cortex LLM extracts structured data automatically. Zero manual typing. The officer reviews and saves."

**Action:** Click "Save to Database"

> [1:05] "Now watch what happens with an irrelevant document."

**Action:** Upload a non-medical file → Click "Extract & Preview" → Alert shows "Document rejected"

> [1:15] "Rejected instantly. The AI classified it as irrelevant — no LLM credits wasted. Two-layer validation: text quality check, then AI classification."

**Transition:** Navigate to Claims list

> [1:25] "Now let's look at the adjudication engine."

---

## [1:30 - 2:40] DEMO 2: Claim Adjudication + Similar Claims + Decision

**URL:** https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/claims/CLM-2026-0010

**Narration:**

> [1:30] "Here's an emergency appendicitis claim — 45 million rupiah. Let's run the Fuzzy AHP scoring."

**Action:** Click "Run Adjudikasi" → Score appears

> [1:40] "The system evaluates four criteria: Medical Necessity, Policy Compliance, Documentation Completeness, and Cost Reasonableness. Each receives a fuzzy linguistic label — converted to numeric scores through Triangular Fuzzy Numbers."

**Show:** Score gauge (62.17) + breakdown table

> [1:55] "Score 62 — falls in the manual review range. The system recommends review, but doesn't auto-decide. The human officer retains authority."

> [2:05] "Now here's a powerful feature — Similar Claims, powered by Cortex Search."

**Show:** Scroll to Similar Claims panel

> [2:10] "The system finds historically similar claims using semantic search. Look — a previous appendicitis claim was approved with score 66. Another cholecystitis case scored 68. This gives the officer context for consistent decisions."

> [2:20] "Armed with the score, criteria breakdown, and historical comparisons — the officer makes an informed decision."

**Action:** Select "Approve" → Enter approved amount (Rp 38,000,000 — partial) → Submit

> [2:30] "Partial approval — 84 percent of the claimed amount. A real-world scenario that most systems can't handle. ClariFi supports nuanced decisions."

---

## [2:40 - 3:00] SLIDE: Impact + Closing

**Show:** Final PowerPoint slide

**Narration:**

> [2:40] "ClariFi reduces claim review time from 30 minutes to 2 minutes. Every decision is auditable and explainable. Behind the scenes, Streams and Tasks auto-score new claims within one minute — event-driven, zero manual trigger."

> [2:52] "Snowflake is not just a data warehouse — it's a complete platform for AI-powered applications. ClariFi proves it. From document ingestion to intelligent scoring to real-time automation — all within a single, secure platform."

> [2:58] "ClariFi — Adjudication with Clarity."

---

## PRODUCTION NOTES

### Recording Plan
1. **Slides:** Record PowerPoint with screen capture (or export as images and overlay in CapCut)
2. **Demo 1 (Import):** Record the full flow, speed up loading to 2x
3. **Demo 2 (Adjudication):** Record claim detail interactions, speed up loading to 2x
4. **Closing slide:** Static image, 20 seconds

### Speed Adjustments
| Segment | Real Duration | Playback Speed | Video Duration |
|---------|--------------|----------------|----------------|
| Slides | 30s | 1x | 30s |
| Import: upload + wait | ~15s | 2x | 8s |
| Import: show results | ~10s | 1x | 10s |
| Import: reject demo | ~10s | 1.5x | 7s |
| Adjudication: click + wait | ~15s | 2x | 8s |
| Adjudication: show results | ~30s | 1x | 30s |
| Decision: partial approve | ~10s | 1x | 10s |
| Closing slide | 20s | 1x | 20s |

### TTS Settings (CapCut)
- Voice: English, Male, Professional/Narrator style
- Speed: 1.0x (don't rush — clarity > speed)
- Pause between sections: 0.5s

### Key URLs for Recording
| Scene | URL |
|-------|-----|
| Import Documents | https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/import |
| Claims List | https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/claims |
| Emergency Claim | https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/claims/CLM-2026-0010 |
| Partial Approval Example | https://iqmwy-qicsmic-fi31542.snowflakecomputing.app/claims/CLM-2026-0005 |
