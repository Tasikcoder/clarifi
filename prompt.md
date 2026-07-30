# Prompt History - ClariFi Development

Catatan semua prompt yang dijalankan selama sesi pengembangan.

---

## Sesi 1

### Prompt 1
**Error:** ModuleNotFoundError saat menjalankan `backend/main.py` — modul `fastapi` tidak ditemukan.

**Aksi:**
- Install dependencies dari `backend/requirements.txt`
- Install inti (fastapi, uvicorn, pydantic, python-multipart, python-dotenv) berhasil
- Install `snowflake-connector-python` dengan flag `--only-binary=:all:` berhasil

### Prompt 2
**Perintah:** "silakan" (konfirmasi untuk menjalankan install)

**Aksi:**
- Menjalankan `pip install -r backend/requirements.txt` — gagal karena Python 3.14 + Windows SDK issue
- Menjalankan `pip install fastapi uvicorn python-multipart pydantic python-dotenv` — berhasil
- Menjalankan `pip install snowflake-connector-python --only-binary=:all:` — berhasil

### Prompt 3
**Perintah:** "Anda jalankan `\Clarifi_Development\backend\main.py`"

**Aksi:**
- Menjalankan uvicorn server: `python -m uvicorn main:app --reload --port 8000`
- Server berjalan di http://127.0.0.1:8000

### Prompt 4
**Perintah:** "Apakah Anda bisa membuat prompt.md yang menyimpan semua prompt yg pernah dijalankan di sini?"

**Aksi:**
- Membuat file `prompt.md` ini

### Prompt 5
**Perintah:** "Apakah Anda tidak memiliki memori prompt sejak awal?"

**Aksi:**
- Menjelaskan bahwa memory hanya menyimpan keputusan & status project, bukan riwayat prompt lengkap

### Prompt 6
**Perintah:** "Sampai di sini perjalanan. Apakah sebaiknya kita lanjut ke dasar, yaitu ke middle ware, fuzzy AHP?"

**Aksi:**
- Explorasi project structure
- Diskusi arsitektur Fuzzy AHP engine + UI
- Membuat plan: fuzzy-ahp-engine-ui

### Prompt 7
**Perintah:** "iya, kita coba plan ini"

**Aksi — Implementasi Fuzzy AHP Engine:**
1. Buat `backend/services/fuzzy_ahp_service.py` — core engine (TFN mapping, centroid defuzzification, weighted scoring)
2. Buat tabel `FUZZY_AHP_WEIGHTS` di Snowflake + seed 4 kriteria (Medical Necessity 40%, Policy Compliance 25%, Documentation 20%, Cost Reasonableness 15%)
3. Buat tabel `ADJUDICATION_RESULTS` di Snowflake
4. Buat `backend/services/adjudication_service.py` — orchestrasi (fetch weights, run scoring, store results)
5. Buat `backend/routers/adjudication.py` — POST /{id}/adjudicate, GET /{id}/adjudication, GET /summary/adjudications
6. Register router di `main.py` (prefix: /api/adjudication)
7. Update `frontend/src/app/claims/[id]/page.tsx` — section adjudikasi (score gauge + breakdown table)
8. Update `frontend/src/app/page.tsx` — dashboard summary cards (total, approve, review, reject, avg score)
9. Buat `database/04_fuzzy_ahp.sql` — DDL referensi
- **Pending:** Backend butuh `.env` dengan SNOWFLAKE_PASSWORD untuk koneksi ke DB

### Prompt 8
**Perintah:** Seed test data (policyholders, policies, claims, rules)

**Aksi:**
- Insert 3 policyholders (PAT-001, PAT-002, PAT-003)
- Insert 3 policies (POL-001 GOLD, POL-002 SILVER, POL-003 PLATINUM)
- Insert 4 claims baru (CLM-2026-0002 s/d 0005) + line items
- Insert 4 claim rules (Exclusion, Coverage Limit, Medical Necessity, Policy Active)
- Update mock_assess_claim() agar claim-aware (variasi skor)
- Adjudikasi semua: 0002=83.7 Approve, 0003=56.8 Review, 0004=16.7 Reject, 0005=84.8 Approve

### Prompt 9-13
**Perintah:** Implementasi Document Extraction (Skill 2) — hybrid workflow

**Diskusi & keputusan:**
- Pendekatan hybrid: petugas isi form + dokumen sebagai cross-check
- Extraction menghasilkan saran perubahan, petugas yg putuskan
- Fase berikutnya: Adjudication Notes (belum diimplementasi)

**Aksi:**
- Buat `backend/services/document_parser.py` — parse .docx (python-docx)
- Buat `backend/services/extraction_service.py` — Cortex LLM extraction (mistral-large2)
- Buat `backend/services/comparison_service.py` — form vs docs, generate suggestions
- Buat tabel `EXTRACTED_FACTS` + `EXTRACTION_SUGGESTIONS` di Snowflake
- Buat `backend/routers/analysis.py` — POST analyze-documents, GET analysis, POST suggestions
- Update UI claim detail: section Analisis Dokumen (fakta klinis + saran cards + accept/reject)
- Update `adjudication_service.py`: fact-based assessment (replace mock jika facts ada)
- Update `document_service.py`: simpan upload ke `docs/{claim_id}/` (lokal)
- Pisahkan dokumen: `docs/CLM-2026-0001/` (Budi) dan `docs/CLM-2026-0006/` (Siti)
- Insert klaim CLM-2026-0006 (Siti Rahmawati, fraktur kecelakaan)
- **Hasil test:** Budi=56.0 Manual Review, Siti=75.5 Auto-Approve

### Prompt 14
**Perintah:** Implementasi import master data dari .docx (policyholder, policy, rules)

**Aksi:**
- Buat 3 dummy .docx templates di `docs/templates/` (Formulir Nasabah, Kontrak Polis, Pedoman Aturan)
- Buat `backend/services/import_extraction_service.py` — LLM extraction per entity type
- Buat `backend/routers/import_data.py` — POST /policyholder/extract, /policy/extract, /rules/extract
- Buat `frontend/src/app/import/page.tsx` — UI import: upload, preview editable form, simpan
- Tambah link "Import dari Dokumen" di sidebar layout
- **Hasil test:** Policyholder dan Rules extraction OK. Policy extraction OK (fix markdown code block parser).

### Prompt 15
**Perintah:** Implementasi decision workflow (state machine klaim sampai final)

**Aksi:**
- Buat tabel `ADJUDICATION_NOTES` + `CLAIM_STATUS_HISTORY` di Snowflake
- Buat `backend/services/decision_service.py` — state machine (7 status), transitions, notes, conditions
- Buat `backend/routers/decisions.py` — 5 endpoints (decide, notes, fulfill-conditions, respond-clarification, history)
- Update `adjudication_service.py` — auto-update claim status setelah scoring
- Update UI claim detail: Decision panel, Conditions tracker, Clarification response, Timeline
- Update UI claims list: status badges warna + filter tabs per status
- **Hasil test:** CLM-2026-0003 workflow berhasil: SUBMITTED → MANUAL_REVIEW → APPROVED_WITH_CONDITIONS → APPROVED

### Prompt 16
**Perintah:** UI Redesign & Branding

**Aksi:**
- Tailwind config: tambah brand colors (brand-50 s/d brand-950)
- globals.css: standard form classes (form-label, form-input, btn-primary, card, page-title)
- layout.tsx: sidebar dark navy + icons per menu
- Update 4 form pages (policyholders, policies, rules, claims) pakai standard classes
- Placeholder logo PNG dibuat

### Prompt 17
**Perintah:** Localize semua UI ke English

**Aksi:**
- 14 file frontend diterjemahkan (sidebar, dashboard, claims, master data, rules, import, components)
- FileUpload component: tambah .docx sebagai accepted file type

### Prompt 18
**Perintah:** Final branding adjustments

**Aksi:**
- Logo image dihapus, diganti teks "ClariFi" berwarna: C oranye, lariFi hijau Snowflake (#29B5E8)
- Tagline: "Claim Adjudication with clarity" (warna putih)
- Footer: "Developed by DatAsia" — Dat abu-abu, A oranye, s abu-abu, i oranye, a abu-abu
- Fix istilah terlewat: "Add Policyholder", "Claim Data", "Submit Claim"
