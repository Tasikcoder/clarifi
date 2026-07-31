# Update Production — ClariFi SPCS Deployment

## Production URL

**https://iqmwy-qicsmic-fi31542.snowflakecomputing.app**

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
