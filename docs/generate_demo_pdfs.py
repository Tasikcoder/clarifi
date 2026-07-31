"""Generate demo PDFs for ClariFi import feature testing."""
from fpdf import FPDF
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "demo_imports"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_pdf(filename: str, title: str, lines: list[str]):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    w = pdf.w - pdf.l_margin - pdf.r_margin
    for line in lines:
        if line.startswith("##"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(w, 6, line.replace("## ", ""), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
        elif line == "---":
            pdf.ln(2)
            y = pdf.get_y()
            pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
            pdf.ln(2)
        elif line == "":
            pdf.ln(3)
        else:
            pdf.multi_cell(w, 5, line)
    pdf.output(str(OUTPUT_DIR / filename))
    print(f"Created: {OUTPUT_DIR / filename}")


# 1. POLICYHOLDER DOCUMENT
create_pdf("data_nasabah_kartini.pdf", "FORMULIR DATA NASABAH", [
    "PT Asuransi Sehat Sejahtera",
    "Formulir Pendaftaran Nasabah Baru",
    "---",
    "## Data Pribadi",
    "Nama Lengkap: Kartini Widodo",
    "No. KTP (NIK): 3374015503880001",
    "Tanggal Lahir: 15 Maret 1988",
    "Jenis Kelamin: Perempuan",
    "Alamat: Jl. Pahlawan No. 72, Kelurahan Serengan, Kecamatan Serengan, Solo, Jawa Tengah 57155",
    "No. Telepon: 081298765432",
    "Email: kartini.widodo@gmail.com",
    "---",
    "## Informasi Tambahan",
    "Pekerjaan: Dosen Universitas Sebelas Maret",
    "Status: Menikah",
    "Tanggal Pendaftaran: 1 Agustus 2026",
    "---",
    "Dokumen ini adalah formulir resmi pendaftaran nasabah baru.",
    "Diverifikasi oleh: Admin Cabang Solo",
    "Tanggal Verifikasi: 1 Agustus 2026",
])

# 2. POLICY DOCUMENT
create_pdf("kontrak_polis_kartini.pdf", "KONTRAK POLIS ASURANSI KESEHATAN", [
    "PT Asuransi Sehat Sejahtera",
    "Polis Asuransi Kesehatan - Sertifikat",
    "---",
    "## Data Pemegang Polis",
    "Nama Tertanggung: Kartini Widodo",
    "No. Polis: POL-006",
    "---",
    "## Detail Polis",
    "Tipe Plan: GOLD",
    "Limit Pertanggungan: Rp 100.000.000 (seratus juta rupiah)",
    "Tanggal Efektif: 1 Agustus 2026",
    "Tanggal Berakhir: 31 Juli 2027",
    "Premi Bulanan: Rp 850.000",
    "---",
    "## Manfaat",
    "- Rawat Inap: Ditanggung penuh hingga limit",
    "- Rawat Jalan: Ditanggung hingga Rp 5.000.000 per kunjungan",
    "- ICU: Ditanggung hingga 10 hari",
    "- Pembedahan: Ditanggung sesuai jadwal operasi",
    "---",
    "## Exclusions (Pengecualian)",
    "1. Prosedur kosmetik (cosmetic surgery)",
    "2. Perawatan gigi rutin (routine dental)",
    "3. Pengobatan infertilitas",
    "4. Percobaan bunuh diri atau menyakiti diri sendiri",
    "---",
    "## Masa Tunggu",
    "- Penyakit umum: 30 hari",
    "- Penyakit khusus (jantung, kanker): 12 bulan",
    "- Kecelakaan: Tidak ada masa tunggu",
    "---",
    "Diterbitkan di Jakarta, 1 Agustus 2026",
    "PT Asuransi Sehat Sejahtera",
    "Direktur Utama",
])

# 3. CLAIM RULES DOCUMENT
create_pdf("pedoman_aturan_klaim.pdf", "PEDOMAN ATURAN ADJUDIKASI KLAIM", [
    "PT Asuransi Sehat Sejahtera",
    "Standard Operating Procedure - Adjudikasi Klaim",
    "Revisi: Juli 2026",
    "---",
    "## Aturan 1: Pengecekan Kelayakan Polis",
    "Nama Aturan: Cek Status Polis Aktif",
    "Kategori: ELIGIBILITY",
    "Kondisi: Status polis harus ACTIVE pada tanggal kejadian",
    "Aksi: REJECT jika polis tidak aktif atau sudah expired",
    "Prioritas: 1",
    "Deskripsi: Klaim hanya dapat diproses jika polis dalam keadaan aktif pada saat kejadian medis terjadi.",
    "---",
    "## Aturan 2: Batas Pertanggungan",
    "Nama Aturan: Validasi Limit Coverage",
    "Kategori: COVERAGE_LIMIT",
    "Kondisi: Total klaim tidak boleh melebihi sisa limit pertanggungan",
    "Aksi: FLAG untuk review manual jika melebihi 80% limit",
    "Prioritas: 2",
    "Deskripsi: Klaim yang mendekati atau melebihi batas pertanggungan memerlukan persetujuan supervisor.",
    "---",
    "## Aturan 3: Exclusion Prosedur Kosmetik",
    "Nama Aturan: Tolak Otomatis Prosedur Kosmetik",
    "Kategori: EXCLUSION",
    "Kondisi: Jenis layanan mengandung kata 'cosmetic', 'kecantikan', atau 'estetika'",
    "Aksi: REJECT otomatis",
    "Prioritas: 1",
    "Deskripsi: Prosedur yang bersifat kosmetik tidak ditanggung sesuai ketentuan polis.",
    "---",
    "## Aturan 4: Masa Tunggu Penyakit Khusus",
    "Nama Aturan: Cek Waiting Period",
    "Kategori: WAITING_PERIOD",
    "Kondisi: Tanggal kejadian harus lebih dari 12 bulan setelah tanggal efektif polis untuk penyakit khusus",
    "Aksi: REJECT jika masih dalam masa tunggu",
    "Prioritas: 2",
    "Deskripsi: Penyakit khusus (jantung, kanker, stroke) memiliki masa tunggu 12 bulan sejak polis aktif.",
    "---",
    "## Aturan 5: Kelengkapan Dokumen",
    "Nama Aturan: Validasi Dokumen Pendukung",
    "Kategori: DOCUMENTATION",
    "Kondisi: Klaim harus disertai minimal formulir klaim, kuitansi asli, dan resume medis",
    "Aksi: FLAG untuk klarifikasi jika dokumen tidak lengkap",
    "Prioritas: 3",
    "Deskripsi: Dokumen pendukung wajib dilampirkan untuk proses verifikasi klaim.",
])

# 4. CLAIM SUBMISSION (for document upload to existing claim)
create_pdf("formulir_klaim_kartini.pdf", "FORMULIR PENGAJUAN KLAIM ASURANSI", [
    "PT Asuransi Sehat Sejahtera",
    "Formulir Klaim Rawat Jalan",
    "---",
    "## Data Tertanggung",
    "Nama: Kartini Widodo",
    "No. Polis: POL-006",
    "No. KTP: 3374015503880001",
    "---",
    "## Data Kejadian",
    "Tanggal Kejadian: 28 Juli 2026",
    "Tanggal Pengajuan: 30 Juli 2026",
    "---",
    "## Informasi Medis",
    "Diagnosis: Gastritis Acute",
    "Jenis Layanan: Rawat Jalan (Outpatient)",
    "Nama Provider: RS Bethesda Yogyakarta",
    "Dokter yang Merawat: dr. Hendra Wijaya, Sp.PD",
    "---",
    "## Rincian Biaya",
    "1. Konsultasi Dokter Spesialis Penyakit Dalam: Rp 350.000",
    "2. Endoskopi Diagnostik: Rp 5.500.000",
    "3. Obat-obatan (Omeprazole, Sucralfate, Domperidone): Rp 650.000",
    "4. Pemeriksaan H. Pylori: Rp 500.000",
    "Total Biaya: Rp 7.000.000",
    "---",
    "## Keluhan Pasien",
    "Pasien datang dengan keluhan nyeri ulu hati yang memburuk sejak 3 hari. ",
    "Mual, muntah, dan tidak bisa makan. Riwayat gastritis sebelumnya (+).",
    "Pemeriksaan endoskopi menunjukkan erosi mukosa lambung.",
    "---",
    "Tanda tangan pasien: Kartini Widodo",
    "Tanggal: 30 Juli 2026",
])

# 5. MEDICAL RESULT (claim supporting document)
create_pdf("hasil_lab_kartini.pdf", "HASIL PEMERIKSAAN LABORATORIUM", [
    "RS Bethesda Yogyakarta",
    "Laboratorium Patologi Klinik",
    "---",
    "## Data Pasien",
    "Nama: Kartini Widodo",
    "Umur: 38 tahun / Perempuan",
    "No. RM: 2026-BTS-4521",
    "Dokter Pengirim: dr. Hendra Wijaya, Sp.PD",
    "Tanggal Pemeriksaan: 28 Juli 2026",
    "---",
    "## Hasil Pemeriksaan Darah Lengkap",
    "Hemoglobin: 11.8 g/dL (Normal: 12.0-16.0) -- RENDAH",
    "Leukosit: 9.200 /uL (Normal: 4.000-11.000)",
    "Trombosit: 285.000 /uL (Normal: 150.000-400.000)",
    "Hematokrit: 35% (Normal: 36-44%)",
    "---",
    "## Pemeriksaan H. Pylori",
    "H. Pylori IgG: POSITIF",
    "H. Pylori Antigen (Stool): POSITIF",
    "---",
    "## Kimia Darah",
    "SGOT: 28 U/L (Normal: <35)",
    "SGPT: 32 U/L (Normal: <40)",
    "Ureum: 25 mg/dL (Normal: 15-40)",
    "Kreatinin: 0.8 mg/dL (Normal: 0.6-1.2)",
    "---",
    "## Kesimpulan",
    "Infeksi H. Pylori positif. Anemia ringan (Hb 11.8).",
    "Disarankan terapi eradikasi H. Pylori dan evaluasi ulang dalam 4 minggu.",
    "---",
    "Divalidasi oleh: dr. Sari Mulyani, Sp.PK",
    "Tanggal: 28 Juli 2026",
])

# 6. RECEIPT/KUITANSI (claim supporting document)
create_pdf("kuitansi_kartini.pdf", "KUITANSI PEMBAYARAN", [
    "RS Bethesda Yogyakarta",
    "Jl. Jenderal Sudirman No. 70, Yogyakarta",
    "Telp: (0274) 555-1234",
    "---",
    "No. Kuitansi: KWT/2026/07/4521",
    "Tanggal: 28 Juli 2026",
    "---",
    "## Diterima dari",
    "Nama Pasien: Kartini Widodo",
    "No. Rekam Medis: 2026-BTS-4521",
    "---",
    "## Rincian Pembayaran",
    "1. Konsultasi Dokter Sp.PD: Rp 350.000",
    "2. Tindakan Endoskopi: Rp 5.500.000",
    "3. Pemeriksaan Lab (H. Pylori + DL): Rp 500.000",
    "4. Obat-obatan: Rp 650.000",
    "---",
    "TOTAL: Rp 7.000.000 (Tujuh Juta Rupiah)",
    "---",
    "Metode Pembayaran: Jaminan Asuransi (Pending)",
    "No. Polis Asuransi: POL-006",
    "---",
    "Kasir: Rina Handayani",
    "RS Bethesda Yogyakarta",
])

# 7. IRRELEVANT DOCUMENT (should be REJECTED by screening)
create_pdf("brosur_wisata_bali.pdf", "PAKET WISATA BALI 2026", [
    "PROMO SPESIAL LIBURAN AKHIR TAHUN!",
    "---",
    "## Paket Honeymoon Bali 4D3N",
    "Harga: Rp 5.500.000 / couple",
    "",
    "Termasuk:",
    "- Tiket pesawat PP Jakarta-Bali",
    "- Hotel bintang 4 (3 malam)",
    "- Private pool villa upgrade (tambah Rp 1jt)",
    "- Breakfast daily",
    "- Airport transfer",
    "---",
    "## Itinerary",
    "Hari 1: Tiba di Bali, check-in hotel, free time",
    "Hari 2: Ubud tour - Monkey Forest, Tegallalang Rice Terrace, Tirta Empul",
    "Hari 3: Watersport di Tanjung Benoa, Uluwatu sunset, dinner Jimbaran",
    "Hari 4: Check-out, oleh-oleh di Krisna, airport transfer",
    "---",
    "## Syarat & Ketentuan",
    "- Berlaku untuk keberangkatan Oktober - Desember 2026",
    "- Minimal booking 2 minggu sebelum keberangkatan",
    "- Harga tidak berlaku untuk peak season (25 Des - 2 Jan)",
    "- DP 50% saat booking, pelunasan H-7",
    "---",
    "BOOKING SEKARANG!",
    "WA: 081234567890",
    "IG: @bali_dream_tour",
    "Website: www.balidreamtour.co.id",
    "---",
    "Bali Dream Tour - Your Trusted Travel Partner Since 2015",
])

# 8. ANOTHER IRRELEVANT - personal/random content
create_pdf("catatan_resep_masakan.pdf", "KUMPULAN RESEP MASAKAN NUSANTARA", [
    "Catatan Pribadi - Dapur Ibu",
    "---",
    "## Resep 1: Rendang Padang",
    "Bahan-bahan:",
    "- 1 kg daging sapi has dalam, potong dadu",
    "- 1 liter santan kental dari 2 butir kelapa",
    "- 10 buah cabai merah keriting",
    "- 5 siung bawang merah",
    "- 3 siung bawang putih",
    "- 2 cm lengkuas, memarkan",
    "- 2 batang serai, memarkan",
    "- 5 lembar daun jeruk",
    "- 2 lembar daun kunyit",
    "---",
    "Cara Masak:",
    "1. Haluskan bumbu: cabai, bawang merah, bawang putih, kunyit, jahe",
    "2. Tumis bumbu halus hingga harum, masukkan serai dan lengkuas",
    "3. Masukkan daging, aduk rata dengan bumbu",
    "4. Tuang santan, masak dengan api kecil 3-4 jam",
    "5. Aduk sesekali agar tidak gosong",
    "6. Masak hingga santan mengering dan daging berwarna coklat kehitaman",
    "---",
    "## Resep 2: Soto Ayam Lamongan",
    "Bahan: ayam kampung, kunyit, kemiri, bawang, koya, sambal",
    "Tips: gunakan ayam kampung untuk kaldu yang lebih gurih",
    "---",
    "Catatan: resep warisan nenek dari Bukittinggi",
])

print("\n=== All demo PDFs created successfully! ===")
print(f"Location: {OUTPUT_DIR}")
