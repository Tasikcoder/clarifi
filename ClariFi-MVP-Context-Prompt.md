# ClariFi — Build Context untuk AI Coding Tool

> Gunakan dokumen ini sebagai system/context prompt saat memulai sesi dengan Claude Code (atau tool coding lain) untuk membangun MVP ClariFi di Snowflake. Tempel seluruh isi ini di awal sesi, lalu tambahkan instruksi task spesifik (mis. "buatkan skema tabel dulu" atau "implementasikan Skill 2").

## 1. Ringkasan Proyek

ClariFi adalah **Decision Support System (DSS) berbasis AI** untuk adjudikasi klaim asuransi kesehatan. Sistem ini dibangun di atas **Snowflake CoCo CLI**, memanfaatkan **Snowflake Cortex** untuk pemahaman bahasa/dokumen dan **Python UDF** untuk logika matematis. Bedanya dengan AI claim-bot pada umumnya: ClariFi tidak menghasilkan keputusan biner (Approve/Reject) dari black-box model, melainkan menggunakan **Fuzzy Analytic Hierarchy Process (Fuzzy AHP)** untuk menghasilkan skor yang **matematis, dapat ditelusuri (traceable), dan explainable**.

**Tagline:** "Where insurance meets intelligence" — Fuzzy AHP & LLM untuk keputusan klaim yang adil.

## 2. Masalah yang Diselesaikan

1. **Subjektivitas adjudikasi**: adjudikator manual mengevaluasi laporan medis, wording polis, dan pedoman klinis yang ambigu/kontradiktif → keputusan tidak konsisten.
2. **Black-box AI tidak bisa dipercaya**: solusi AI konvensional memberi output "Claim Rejected" tanpa alasan yang bisa dijelaskan ke pemegang polis → sengketa, sorotan regulator, hilangnya kepercayaan.
3. **Adjudikasi klaim adalah masalah Multi-Criteria Decision Making (MCDM)**, bukan klasifikasi biner sederhana — butuh kombinasi cognitive AI + kerangka keputusan yang transparan.

## 3. Alur Kerja Inti (End-to-End)

```
1. Unstructured Claim Input
   → Adjudikator upload Medical Report (PDF) + Hospital Invoice

2. AI Cognitive Extraction (Snowflake Cortex LLM)
   → Ekstrak fakta klinis terstruktur: ICD-10 codes, CPT codes, Length of Stay, diagnosis, treatment

3. Fuzzy AHP Reasoning
   → LLM mengevaluasi fakta vs aturan polis dinamis menggunakan linguistic fuzzy assessment
     (contoh label: "Highly Consistent", "Not Medically Necessary")

4. Mathematical Defuzzification (Python UDF di Snowflake)
   → Linguistic assessment → Triangular Fuzzy Numbers (TFN)
   → TFN × bobot kriteria dinamis
   → Defuzzifikasi → skor akhir objektif (0–100)

5. Explainable Decision Output
   → Skor + breakdown kriteria + alasan bahasa natural
   → Routing: Auto-Approve / Manual Review / Auto-Reject (dengan sitasi klausul)
```

**Contoh output yang harus dihasilkan sistem (format wajib untuk MVP):**
> "Score 35: Auto-Reject. Medical Necessity (weight: 40%) scored 'Not Justified' due to lack of clinical correlation between diagnosis (Gastritis) and treatment (MRI Head)."

## 4. Arsitektur Solusi (4 Skill/Modul Utama)

### Orchestration Layer (Backend Core / Agent Skills)
| Skill | Fungsi |
|---|---|
| **Skill 1 — Criteria Ingestion Engine** | Membaca PDF pedoman medis baru (mis. update dari Perdoksi/IDI), otomatis menstrukturkannya jadi JSON hierarchy untuk matriks Fuzzy AHP. Tanpa intervensi developer. |
| **Skill 2 — Fact Extraction Engine** | Parsing dokumen medis tak terstruktur → memetakan ke fakta klinis terstruktur (ICD-10, CPT codes, Length of Stay). |
| **Skill 3 — Fuzzy Evaluator & Scorer** | Menjalankan logika matematis: linguistic assessment → Triangular Fuzzy Number → bobot → defuzzifikasi → skor final 0–100. |
| **Decision Action Trigger** | Routing otomatis berdasarkan skor: Auto-Approve / Manual Review / Auto-Reject (dengan sitasi klausul). |

### Interaction & Ingestion Layer (Snowflake CoCo CLI)
- Natural language interface (CLI atau dashboard sederhana), contoh perintah: `Process claim ID: CLM-2024-001`
- Dokumen tak terstruktur disimpan di **Snowflake internal stages**
- Real-time streaming output: proses ekstraksi → fuzzy scoring → surat keputusan explainable

### AI & Data Services Stack (Snowflake Cortex & Data Cloud)
- **Snowflake Cortex (LLM Services)**: document parsing, pemahaman konteks klinis, menghasilkan linguistic fuzzy evaluation
- **Python UDF**: eksekusi kalkulasi Fuzzy AHP langsung di dalam Snowflake Data Cloud (bukan di luar sistem)
- **Structured Data Tables**:
  - `POLICIES` — batas cakupan, pengecualian (exclusions)
  - `CLAIMS_HISTORY` — untuk cross-check kondisi pre-existing / pola berulang
  - `FUZZY_AHP_WEIGHTS` — hierarki kriteria dinamis (bisa berubah otomatis via Skill 1)

## 5. Kemampuan Diferensiasi yang Wajib Ada di MVP

1. **Dynamic Criteria Ingestion** — sistem bisa update bobot/hierarki Fuzzy AHP otomatis dari PDF pedoman baru, tanpa hardcode ulang.
2. **Transparent Fuzzy Reasoning** — output selalu berupa decision tree/breakdown kontribusi tiap kriteria ke skor akhir, bukan sekadar label Approve/Reject.
3. **Contextual Guideline & History Evolution** — sistem cross-reference `CLAIMS_HISTORY` untuk konsistensi temporal (keputusan hari ini selaras dengan audit sebelumnya & pedoman terbaru).

## 6. Skema Data Awal (starting point, boleh disesuaikan saat implementasi)

```sql
CREATE TABLE POLICIES (
  policy_id STRING,
  coverage_limit NUMBER,
  exclusions VARIANT,       -- JSON list of excluded conditions/procedures
  effective_date DATE
);

CREATE TABLE CLAIMS_HISTORY (
  claim_id STRING,
  policy_id STRING,
  patient_id STRING,
  diagnosis_codes VARIANT,  -- ICD-10 array
  procedure_codes VARIANT,  -- CPT array
  length_of_stay INT,
  decision STRING,          -- Approved / Rejected / Manual Review
  score NUMBER,
  decision_reason STRING,
  created_at TIMESTAMP
);

CREATE TABLE FUZZY_AHP_WEIGHTS (
  criteria_id STRING,
  criteria_name STRING,     -- e.g. "Medical Necessity", "Documentation Completeness"
  weight NUMBER,            -- dynamic, updated by Skill 1
  parent_criteria_id STRING, -- for hierarchy
  last_updated TIMESTAMP,
  source_guideline STRING   -- traceability ke dokumen PDF asal
);
```

## 7. Metodologi Fuzzy AHP (yang harus diimplementasikan di Skill 3)

1. LLM menghasilkan penilaian linguistik per kriteria (contoh skala: Very Poor, Poor, Fair, Good, Very Good / atau Not Consistent → Highly Consistent).
2. Setiap label linguistik dipetakan ke **Triangular Fuzzy Number (l, m, u)** — perlu tabel mapping standar, contoh:
   - "Not Justified" → (0, 0, 25)
   - "Partially Justified" → (25, 40, 60)
   - "Justified" → (50, 65, 80)
   - "Highly Consistent" → (75, 90, 100)
3. TFN dikombinasikan dengan bobot kriteria dari `FUZZY_AHP_WEIGHTS` (bobot ini sendiri idealnya dihitung via pairwise comparison AHP standar, lalu di-fuzzifikasi).
4. Defuzzifikasi (mis. metode centroid / Center of Area) menghasilkan skor akhir 0–100.
5. Threshold routing (contoh, boleh disesuaikan): `<40` = Auto-Reject, `40–70` = Manual Review, `>70` = Auto-Approve.

## 8. Cakupan MVP (prioritas untuk demo hackathon)

**Harus ada (must-have):**
- Upload 1 medical report (PDF) + invoice → ekstraksi fakta klinis via Cortex
- Minimal 1 set kriteria Fuzzy AHP dengan bobot (boleh hardcode dulu, tapi arsitektur harus siap untuk dynamic ingestion)
- Kalkulasi Fuzzy AHP end-to-end sampai skor 0–100 (Python UDF)
- Output keputusan dalam format explainable seperti contoh di Section 3
- Minimal 1 query CLI via Snowflake CoCo CLI yang men-trigger seluruh pipeline

**Nice-to-have (kalau waktu cukup):**
- Skill 1 (Dynamic Criteria Ingestion) berfungsi penuh dari upload PDF pedoman baru
- Dashboard sederhana (bukan cuma CLI) untuk visualisasi decision tree
- Cross-check ke `CLAIMS_HISTORY` untuk deteksi pola berulang

**Di luar scope MVP (jangan habiskan waktu di sini):**
- Autentikasi/role-based access penuh
- Integrasi sistem klaim asuransi eksternal nyata
- UI produksi yang polished — fokus ke fungsi dan defensibilitas angka

## 9. Kriteria Sukses Demo

- Sistem bisa memproses 1 klaim contoh dari upload dokumen sampai keluar skor + alasan dalam < beberapa menit.
- Output keputusan harus bisa "dibela" secara matematis — tunjukkan breakdown kriteria, bobot, dan TFN yang dipakai, bukan cuma skor akhir.
- Tunjukkan minimal 1 contoh dynamic update (mis. ubah bobot kriteria atau upload pedoman baru) yang mengubah hasil skor tanpa mengubah kode.

---

**Instruksi untuk AI coding tool:** Bangun MVP ini secara bertahap sesuai urutan di Section 8 (must-have dulu). Gunakan Python UDF Snowflake untuk semua kalkulasi Fuzzy AHP (jangan lakukan defuzzifikasi di luar Snowflake). Pastikan setiap keputusan yang dihasilkan menyertakan breakdown kriteria yang bisa ditelusuri balik ke tabel `FUZZY_AHP_WEIGHTS` dan hasil ekstraksi LLM — ini adalah nilai jual utama produk, jangan disederhanakan menjadi output biner.
