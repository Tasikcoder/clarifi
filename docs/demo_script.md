# Skrip Demo ClariFi — Decision Support System for Health Insurance Claim Adjudication

**Durasi:** 10-15 menit
**Base URL:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app
**Presenter:** [Nama]

---

## PEMBUKAAN (1-2 menit)

> "Selamat [pagi/siang], perkenalkan ClariFi — sebuah Decision Support System untuk adjudikasi klaim asuransi kesehatan. ClariFi menggabungkan metode Fuzzy AHP (Analytical Hierarchy Process) dengan Snowflake Cortex AI untuk membantu petugas klaim membuat keputusan yang lebih cepat, konsisten, dan transparan."

> "Yang membuat ClariFi berbeda: sistem ini bukan black-box. Setiap keputusan bisa di-trace — dari dokumen asli, hingga skor per kriteria, sampai keputusan akhir. Dan semua berjalan di atas platform Snowflake."

---

## BAGIAN 1: DASHBOARD OVERVIEW (1 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/

> "Di dashboard, kita bisa melihat ringkasan adjudikasi: berapa klaim yang auto-approved, manual review, dan auto-rejected. Sistem sudah memproses [X] klaim secara otomatis."

**Yang ditunjukkan:**
- Total Adjudications, Auto-Approve, Manual Review, Auto-Reject
- Average Score gauge

---

## BAGIAN 2: DAFTAR KLAIM (1 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims

> "Di halaman Claims, kita lihat semua klaim dengan berbagai status — warna hijau untuk Approved, kuning untuk Manual Review, merah untuk Rejected, oranye untuk Pending Clarification. Perhatikan bahwa sistem sudah otomatis mengklasifikasikan setiap klaim berdasarkan skornya."

**Yang ditunjukkan:**
- Badge warna-warni per status
- Variasi klaim: ISPA Rp 3.5jt (simple), Appendicitis Rp 45jt (kompleks), Cosmetic Rhinoplasty (rejected)
- Klaim dengan Partial Approval: Ahmad Fauzi (Rp 85jt klaim, Rp 65jt disetujui)

---

## BAGIAN 3: IMPORT DATA VIA PDF (2-3 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/import

> "Sebelum memproses klaim, kita perlu data master. ClariFi bisa mengekstrak data langsung dari dokumen PDF menggunakan Snowflake Cortex AI. Saya akan demo import data nasabah baru."

**Aksi:**
1. Pilih tipe "Policyholder"
2. Upload file `data_nasabah_rina.pdf`
3. Klik "Extract & Preview"

> "Perhatikan — sistem membaca PDF, lalu Cortex LLM mengekstrak data terstruktur: nama, NIK, tanggal lahir, alamat, semuanya otomatis. Petugas tinggal review dan klik Save."

4. Review data yang ter-extract
5. Klik "Save to Database"

> "Sekarang mari kita import juga polis asuransinya dan aturan klaim."

6. Ulangi untuk Policy (`kontrak_polis_rina.pdf`) dan Claim Rules (`aturan_adjudikasi.pdf`)

**Key message:** "Dari dokumen tidak terstruktur menjadi data terstruktur — tanpa ketik manual."

**Verifikasi:**
- Cek data nasabah: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policyholders
- Cek data polis: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/policies
- Cek aturan klaim: https://asaiy-yhnomry-uw19292.snowflakecomputing.app/rules

---

## BAGIAN 3b: DOCUMENT SCREENING — REJECT DOKUMEN SAMPAH (1 menit)

**Tetap di:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/import

> "Tapi bagaimana jika seseorang upload dokumen yang tidak relevan — misalnya brosur, foto pribadi, atau file kosong? Sistem ClariFi punya fitur pre-screening."

**Aksi:**
1. Pilih tipe "Policyholder"
2. Upload file yang **bukan** dokumen asuransi (misal: file teks random, brosur, atau PDF kosong)
3. Klik "Extract & Preview"

> "Perhatikan — sistem menolak dokumen ini SEBELUM mengirim ke LLM. Muncul pesan: 'Document rejected — not relevant to insurance claims'. Ini penting untuk efisiensi biaya: kita tidak membuang credit Cortex AI untuk memproses dokumen sampah."

**Key message:** "Pre-screening menggunakan AI_CLASSIFY dari Snowflake Cortex — hemat biaya, filter noise sejak awal."

> "Dua layer validasi: pertama cek apakah dokumen punya teks yang cukup (reject file blank/corrupt). Kedua, AI mengklasifikasi apakah dokumen relevan — medical report, invoice, formulir klaim — atau irrelevant seperti spam atau foto pribadi."

---

## BAGIAN 4: SUBMIT KLAIM BARU (2 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/new

> "Sekarang kita simulasikan pengajuan klaim baru. Nasabah Rina Wulandari datang dengan diagnosis Gastritis Acute, rawat jalan di RS Bethesda."

**Aksi:** Isi form:
- Policy ID: POL-006 (atau sesuai yang baru dibuat)
- Patient: Rina Wulandari
- Diagnosis: Gastritis Acute
- Service Type: Outpatient
- Provider: RS Bethesda Yogyakarta
- Line items: Konsultasi (Rp 300.000), Endoskopi (Rp 5.000.000), Obat (Rp 800.000)
- Upload dokumen PDF pendukung

> "Perhatikan saat upload, sistem langsung mem-parse dokumen dan mendeteksi tipe-nya — kuitansi, hasil lab, formulir klaim. Ini fitur auto-parse yang berjalan real-time."

Klik "Submit Claim"

---

## BAGIAN 5: AUTO-PIPELINE (1 menit)

**Tetap di:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims

> "Di balik layar, Snowflake Stream mendeteksi klaim baru masuk. Dalam 1 menit, Task terjadwal akan otomatis menjalankan initial scoring. Kita tidak perlu klik apapun."

**Aksi:** Tunggu sebentar, lalu refresh halaman Claims

> "Lihat — klaim yang tadi SUBMITTED sekarang sudah berubah statusnya menjadi [Manual Review/Approved]. Ini dilakukan oleh auto-pipeline tanpa intervensi manual."

**Key message:** "Event-driven architecture — Stream detects, Task processes."

---

## BAGIAN 6: DETAIL KLAIM & ADJUDIKASI (3-4 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0009

(Klaim Budi Santoso, ISPA, Rp 3.5jt — status MANUAL_REVIEW)

> "Mari kita lihat detail klaim. Di sini petugas bisa melihat semua informasi: data pasien, prosedur yang diklaim, dokumen pendukung beserta status parsing-nya."

### 6a. Document Analysis

> "Langkah pertama petugas: analisis dokumen. Sistem menggunakan Cortex LLM untuk mengekstrak fakta klinis dari dokumen — diagnosis, prosedur, biaya, temuan laboratorium."

**Aksi:** Klik "Document Analysis" (jika dokumen memiliki parsed text)

### 6b. Fuzzy AHP Adjudication

**Aksi:** Klik "Run Adjudikasi"

> "Sekarang kita jalankan scoring Fuzzy AHP. Sistem mengevaluasi 4 kriteria:"
> - "Medical Necessity — apakah prosedur secara medis diperlukan?"
> - "Policy Compliance — apakah sesuai ketentuan polis?"
> - "Documentation Completeness — apakah dokumen lengkap?"
> - "Cost Reasonableness — apakah biaya wajar?"

> "Setiap kriteria diberi label linguistik fuzzy — 'Justified', 'Highly Consistent', 'Partially Justified' — lalu dikonversi ke angka melalui Triangular Fuzzy Number dan defuzzifikasi centroid."

**Yang ditunjukkan:**
- Score gauge (misal: 60.33)
- Tabel breakdown: kriteria, bobot, label, TFN, defuzzified, kontribusi, alasan
- Decision: "Manual Review"

> "Score 60.33 berada di rentang 40-70, artinya butuh review manual oleh petugas. Sistem tidak auto-approve atau auto-reject — memberikan rekomendasi, bukan keputusan final."

### 6c. Similar Claims (Cortex Search)

> "Fitur yang sangat powerful: Similar Claims. Menggunakan Cortex Search, sistem mencari klaim historis yang mirip berdasarkan diagnosis dan prosedur."

**Yang ditunjukkan:**
- Panel "Similar Claims" dengan klaim-klaim serupa
- Score dan keputusan klaim serupa
- "Klaim serupa dari Budi Santoso (Appendicitis) di-approve dengan score 66"

> "Ini membantu petugas: klaim serupa di masa lalu bagaimana keputusannya? Apakah di-approve? Berapa score-nya? Consistency check."

### 6d. Officer Decision

> "Berbekal semua informasi ini — score, breakdown, analisis dokumen, dan klaim serupa — petugas sekarang bisa membuat keputusan yang informed."

**Aksi:** 
- Pilih "Approve (Full)" atau "Approve with Conditions"
- Isi alasan
- (Opsional) Untuk partial approval: isi jumlah yang disetujui
- Submit

---

## BAGIAN 7: PARTIAL APPROVAL (1 menit)

**Buka:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0005

(Klaim Ahmad Fauzi, Acute Myocardial Infarction, Rp 85jt — sudah APPROVED)

> "Contoh partial approval: klaim Ahmad Fauzi untuk serangan jantung sebesar Rp 85 juta. Petugas menyetujui Rp 65 juta — 76.5% — karena biaya kamar VVIP di-downgrade ke VIP sesuai hak polis."

**Yang ditunjukkan:**
- Total Klaim: Rp 85.000.000
- Disetujui: Rp 65.000.000 (76.5%)
- Timeline workflow lengkap

---

## BAGIAN 8: KLAIM LAIN YANG MENARIK (opsional)

Jika ada waktu, tunjukkan juga:

- **Klaim Rejected:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0004
  (Siti Rahayu, Cosmetic Rhinoplasty — auto-rejected score 16.66 karena prosedur kosmetik)

- **Pending Clarification:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0007
  (Dewi Kartika, Vertigo — MRI kepala butuh justifikasi tambahan)

- **Approved with Conditions:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0008
  (Rudi Hermawan, Cholecystitis — perlu lampirkan hasil PA batu empedu)

- **Emergency:** https://asaiy-yhnomry-uw19292.snowflakecomputing.app/claims/CLM-2026-0010
  (Dewi Kartika, Appendicitis Perforata — emergency, biaya signifikan)

---

## BAGIAN 9: ARSITEKTUR SNOWFLAKE (1-2 menit)

> "Di balik layar, ClariFi memanfaatkan 6 fitur utama Snowflake:"

| # | Fitur | Penggunaan |
|---|-------|-----------|
| 1 | **Cortex LLM (COMPLETE)** | Ekstraksi fakta klinis dari dokumen medis |
| 2 | **Cortex AI_CLASSIFY** | Pre-screening dokumen: filter noise sebelum extraction |
| 3 | **Cortex Search** | Semantic similarity search untuk klaim serupa |
| 4 | **SPCS (Container Services)** | Full-stack deployment (Next.js + FastAPI + nginx) |
| 5 | **Streams** | Real-time detection klaim baru |
| 6 | **Tasks** | Auto-scoring pipeline (event-driven) |
| 7 | **Stored Procedures** | Business logic adjudikasi di database layer |

> "Semuanya berjalan di dalam ekosistem Snowflake — tidak ada external dependency. Data tidak pernah keluar dari platform."

---

## PENUTUP (1 menit)

> "ClariFi membuktikan bahwa Snowflake bukan hanya data warehouse — tapi platform lengkap untuk membangun aplikasi AI-powered yang production-ready. Dari ingestion (PDF parsing), processing (Fuzzy AHP + LLM), hingga serving (SPCS) — semua dalam satu platform."

> "Terima kasih. Ada pertanyaan?"

---

## REFERENSI LINK LENGKAP

| Halaman | URL |
|---------|-----|
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

## TIPS DEMO

1. **Jika Document Analysis gagal** (karena seed data tanpa parsed_text): gunakan klaim yang baru di-submit dengan PDF yang di-upload langsung
2. **Untuk menunjukkan auto-pipeline**: submit klaim via UI, tunggu 1-2 menit, refresh halaman
3. **Klaim yang bagus untuk demo detail**: CLM-2026-0005 (partial approval) atau CLM-2026-0010 (emergency appendicitis)
4. **Jika ditanya tentang akurasi**: "Fuzzy AHP memberikan framework terstruktur. LLM memberikan kemampuan membaca dokumen. Kombinasi keduanya lebih baik daripada masing-masing sendiri."
5. **Jika ditanya soal production-readiness**: "Ini MVP. Untuk production, perlu: role-based access control, audit logging lebih detail, integration dengan sistem core insurance, dan fine-tuning model LLM untuk domain spesifik."
