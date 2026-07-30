# Parse & Extract — Document Extraction Engine (Skill 2)

> Rencana implementasi fitur parsing dan extraction dokumen klaim .docx untuk ClariFi DSS.

---

## Tujuan

Menggantikan `mock_assess_claim()` dengan fakta nyata yang di-extract dari dokumen klaim yang diupload user. Sistem akan:
1. Parse file .docx (formulir klaim, kuitansi, hasil penunjang, kronologi, riwayat)
2. Extract fakta klinis terstruktur menggunakan LLM (Snowflake Cortex)
3. Feed fakta tersebut ke Fuzzy AHP engine untuk scoring berbasis data nyata

---

## Dokumen Test (folder `docs/`)

### Skenario 1: Budi Santoso — Test case "suspicious/flag"
| File | Isi Kunci |
|------|-----------|
| `Formulir-Klaim-Dummy-ClariFi.docx` | Gastritis Akut (K29.0), MRI Kepala tanpa indikasi, rawat 3 hari |
| `Kuitansi-Dummy-ClariFi.docx` | Total Rp10.28jt, MRI Rp4.2jt (41% total — questionable) |
| `Hasil-Penunjang-Dummy-ClariFi.docx` | Lab normal, USG mendukung gastritis, MRI normal & tidak berkorelasi |
| `Riwayat-PreExisting-Condition-Dummy-ClariFi.docx` | 3 klaim gastritis dalam 10 bulan, polis < 2 tahun |

**Expected result:** Skor rendah — Medical Necessity turun karena MRI tidak justified, flag pre-existing.

### Skenario 2: Siti Rahmawati — Test case "clean/approve"
| File | Isi Kunci |
|------|-----------|
| `Formulir-Klaim-Siti-Dummy-ClariFi.docx` | Fraktur radius distal (S52.5), kecelakaan, rawat 2 hari |
| `Kronologi-Kecelakaan-Dummy-ClariFi.docx` | Tabrakan motor-mobil, laporan polisi ada, mekanisme konsisten |
| `Hasil-Rontgen-Siti-Dummy-ClariFi.docx` | Fraktur terkonfirmasi, tidak ada pre-existing |
| `Kuitansi-Siti-Dummy-ClariFi.docx` | Total Rp7.425jt, semua item berkorelasi dengan penanganan fraktur |

**Expected result:** Skor tinggi — semua kriteria konsisten, Auto-Approve.

---

## Arsitektur

```
User Upload (.docx)
    │
    ▼
┌─────────────────────┐
│  document_parser.py  │  ← python-docx: extract text + tables
│  (parse .docx)       │
└──────────┬──────────┘
           │ raw text
           ▼
┌─────────────────────────┐
│  extraction_service.py   │  ← Snowflake Cortex COMPLETE (LLM)
│  (structured extraction) │     atau fallback regex/pattern
└──────────┬──────────────┘
           │ JSON facts
           ▼
┌─────────────────────┐
│  EXTRACTED_FACTS     │  ← Snowflake table (VARIANT columns)
│  (database)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│  fuzzy_ahp_service.py    │  ← Replace mock with fact-based assessment
│  (real scoring)          │
└─────────────────────────┘
```

---

## Output Extraction (Target JSON)

```json
{
  "patient_name": "Budi Santoso",
  "diagnosis_primary": {"code": "K29.0", "name": "Gastritis Akut"},
  "diagnosis_secondary": [],
  "procedures": [
    {
      "code": "70551",
      "name": "MRI Brain without contrast",
      "medically_indicated": false,
      "reason": "Permintaan keluarga, tidak ada indikasi neurologis"
    }
  ],
  "length_of_stay_days": 3,
  "total_cost": 10280000,
  "cost_breakdown": [
    {"category": "Kamar", "amount": 2550000},
    {"category": "Jasa Medis", "amount": 1350000},
    {"category": "Penunjang", "amount": 5225000},
    {"category": "Obat & BHP", "amount": 1005000},
    {"category": "Administrasi", "amount": 150000}
  ],
  "clinical_findings": "Lab normal, USG mendukung gastritis, MRI normal tidak berkorelasi",
  "doctor_notes": "MRI diajukan atas permintaan keluarga, tidak ada indikasi klinis",
  "pre_existing_flags": [
    "3 klaim gastritis dalam 10 bulan",
    "Polis < 2 tahun",
    "Deklarasi awal: tidak ada riwayat gangguan lambung"
  ],
  "correlation_issues": [
    "MRI Kepala tidak berkorelasi dengan diagnosis Gastritis Akut"
  ],
  "supporting_documents": ["Formulir Klaim", "Kuitansi", "Hasil Penunjang", "Riwayat Pre-Existing"]
}
```

---

## Langkah Implementasi

### 1. `backend/services/document_parser.py`
- Parse .docx dengan python-docx
- Extract paragraf + tabel → plain text
- Detect tipe dokumen dari heading/judul

### 2. `backend/services/extraction_service.py`
- Gabungkan teks semua dokumen per klaim
- Kirim ke Snowflake Cortex: `SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', prompt)`
- Prompt berisi instruksi → output JSON terstruktur
- Fallback: regex extraction jika Cortex unavailable

### 3. Tabel `CLARIFI.CLAIMS.EXTRACTED_FACTS`
- Simpan hasil extraction per klaim
- Kolom VARIANT untuk nested JSON (procedures, flags, etc.)

### 4. API Endpoint: `POST /api/claims/{claim_id}/extract`
- Baca dokumen yang diupload
- Parse → Extract → Simpan
- Return JSON facts

### 5. Connect ke Fuzzy AHP
- Cek EXTRACTED_FACTS sebelum scoring
- Generate linguistic labels berdasarkan fakta:
  - correlation_issues ada → Medical Necessity = "Not Justified" / "Poorly Justified"
  - pre_existing_flags ada → Policy Compliance turun
  - documents lengkap → Documentation = "Justified" / "Highly Consistent"
  - total_cost vs average → Cost Reasonableness

### 6. UI: Section "Fakta Klinis"
- Tampilkan extracted facts di halaman detail klaim
- Highlight flags dan issues
- Tombol "Extract from Documents"

### 7. Testing End-to-End
- Budi: extract → flag MRI + pre-existing → adjudicate → skor rendah
- Siti: extract → clean → adjudicate → skor tinggi

---

## Dependencies

- `python-docx` (sudah terinstall)
- Snowflake Cortex COMPLETE (model: mistral-large2)
- Warehouse COMPUTE_WH harus aktif untuk Cortex calls

---

## Status: SELESAI DIIMPLEMENTASI

Semua langkah sudah dieksekusi dan diverifikasi:
- Budi (CLM-2026-0001): Score 56.0 → Manual Review (MRI tidak justified terdeteksi)
- Siti (CLM-2026-0006): Score 75.5 → Auto-Approve (semua konsisten)

### File yang dibuat/diubah:
- `backend/services/document_parser.py` — parse .docx
- `backend/services/extraction_service.py` — Cortex LLM extraction
- `backend/services/comparison_service.py` — form vs docs comparison
- `backend/services/adjudication_service.py` — updated: fact-based assessment
- `backend/services/document_service.py` — updated: simpan ke docs/{claim_id}/
- `backend/routers/analysis.py` — API endpoints
- `frontend/src/app/claims/[id]/page.tsx` — UI section analisis
- Tabel Snowflake: `EXTRACTED_FACTS`, `EXTRACTION_SUGGESTIONS`

### Struktur folder dokumen:
```
docs/
├── CLM-2026-0001/   (Budi: formulir, kuitansi, penunjang, riwayat)
├── CLM-2026-0006/   (Siti: formulir, kronologi, rontgen, kuitansi)
```

### Fase berikutnya (belum diimplementasi):
- ADJUDICATION_NOTES — catatan petugas per klaim
- Expanded decisions: Approved with Conditions, Pending Clarification

