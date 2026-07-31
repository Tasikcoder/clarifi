# Update Production — ClariFi SPCS Deployment

## Production URL

**https://mqmwy-qicsmic-fi31542.snowflakecomputing.app**

---

## Update Kode ke Production

Setelah ada perubahan kode di lokal, jalankan perintah berikut untuk update production:

### 1. Build Docker image baru

```powershell
cd d:\Codes\Clarifi_Development
docker build -f deploy/Dockerfile -t clarifi:latest .
```

### 2. Tag untuk Snowflake registry

```powershell
docker tag clarifi:latest qicsmic-fi31542.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
```

### 3. Login ke registry (jika belum)

```powershell
docker login qicsmic-fi31542.registry.snowflakecomputing.com -u muqenasantoso
```
(masukkan password Snowflake saat diminta)

### 4. Push image baru

```powershell
docker push qicsmic-fi31542.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
```

### 5. Restart service (ambil image terbaru)

Jalankan di Cortex Code atau Snowflake Worksheet:
```sql
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;
```

Tunggu ~1 menit, service akan running dengan kode terbaru.

---

## Manage Service

### Cek status
```sql
SELECT SYSTEM$GET_SERVICE_STATUS('CLARIFI.CLAIMS.CLARIFI_APP');
```

### Lihat logs
```sql
SELECT SYSTEM$GET_SERVICE_LOGS('CLARIFI.CLAIMS.CLARIFI_APP', '0', 'clarifi', 100);
```

### Stop service (hemat credit)
```sql
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
```

### Start ulang
```sql
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;
```

### Hapus service (jika tidak dipakai lagi)
```sql
DROP SERVICE CLARIFI.CLAIMS.CLARIFI_APP;
DROP COMPUTE POOL CLARIFI_POOL;
```

---

## Info Teknis

| Item | Detail |
|------|--------|
| Compute Pool | `CLARIFI_POOL` (CPU_X64_XS, 1 node) |
| Auto-suspend | 300 detik (5 menit idle) |
| Image Registry | `qicsmic-fi31542.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo` |
| Service | `CLARIFI.CLAIMS.CLARIFI_APP` |
| Port | 8080 (nginx reverse proxy) |
| Auth (production) | OAuth token (`/snowflake/session/token`) |
| Auth (lokal) | `.env` file dengan password |

---

## Deployment History

| Tanggal | Commit | Deskripsi |
|---------|--------|-----------|
| 2026-07-31 | `240df05` | Initial commit: full app (backend + frontend + database) |
| 2026-07-31 | `7e29a2f` | Add README and database schema for hackathon submission |
| 2026-07-31 | `ff0f3d4` | Add submission deck content |
| 2026-07-31 | `857ebfb` | Migrate deployment to new account QICSMIC-FI31542 (dari expired trial YHNOMRY-UW19292) |
| 2026-07-31 | `ecdd8e6` | Fix import page state reset + add 8 demo PDFs in docs/demo_imports/ |

---

## Catatan Migrasi (31 Juli 2026)

Aplikasi di-deploy ulang dari akun trial `YHNOMRY-UW19292` (expired) ke akun baru `QICSMIC-FI31542`:

1. Database `CLARIFI.CLAIMS` dibuat dari nol (12 tabel + stream + view)
2. Seed data demo: 5 policyholders, 5 policies, 10 claims (berbagai status), 5 rules, AHP weights
3. Image repository baru: `qicsmic-fi31542.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo`
4. Compute pool dedicated: `CLARIFI_POOL` (CPU_X64_XS) — karena SYSTEM_COMPUTE_POOL_CPU hanya untuk notebook/ML
5. Cortex Search Service: `CLARIFI.CLAIMS.SIMILAR_CLAIMS_SEARCH` aktif
6. Fix bug import page: file input tidak di-reset setelah save/reject

### Demo Files (docs/demo_imports/)

| File | Tipe Import | Hasil |
|------|-------------|-------|
| `data_nasabah_kartini.pdf` | Policyholder | Kartini Widodo, NIK 3374015503880001 |
| `kontrak_polis_kartini.pdf` | Policy | Gold, limit Rp100jt |
| `pedoman_aturan_klaim.pdf` | Claim Rules | 5 aturan adjudikasi |
| `formulir_klaim_kartini.pdf` | Claim document | Gastritis, Rp7jt |
| `hasil_lab_kartini.pdf` | Claim document | H.Pylori positif |
| `kuitansi_kartini.pdf` | Claim document | Kuitansi Rp7jt |
| `brosur_wisata_bali.pdf` | REJECTED | Brosur travel (irrelevant) |
| `catatan_resep_masakan.pdf` | REJECTED | Resep masakan (irrelevant) |
