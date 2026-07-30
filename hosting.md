# ClariFi — Panduan Hosting ke Snowflake (SPCS)

ClariFi di-deploy ke **Snowpark Container Services (SPCS)** — container Docker berjalan langsung di dalam Snowflake. Tidak perlu cloud hosting terpisah.

## Arsitektur Deployment

```
Internet
    │
    ▼
[SPCS Public Endpoint - port 8080]
    │
    ▼
[Nginx reverse proxy]
    ├── /api/*  → FastAPI backend (port 8000)
    └── /*      → Next.js frontend (port 3000)
```

Semua berjalan dalam satu container Docker, dikelola oleh `supervisord`:
- **nginx** — reverse proxy, expose port 8080
- **gunicorn + uvicorn** — backend FastAPI (port 8000)
- **node server.js** — frontend Next.js standalone (port 3000)

---

## Informasi Production

| Item | Value |
|------|-------|
| URL | https://iraiy-yhnomry-uw19292.snowflakecomputing.app |
| Compute Pool | SYSTEM_COMPUTE_POOL_CPU |
| Image Registry | yhnomry-uw19292.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo |
| Service Name | CLARIFI.CLAIMS.CLARIFI_APP |
| Auth | SPCS token auth (/snowflake/session/token) |

---

## Prasyarat

1. **Docker Desktop** terinstal dan running
2. **Snowflake CLI** (`snow`) terinstal, atau akses ke Snowsight
3. Akun Snowflake dengan privilege untuk SPCS

---

## Langkah-Langkah Deploy

### 1. Login ke Snowflake Image Registry

```bash
docker login yhnomry-uw19292.registry.snowflakecomputing.com \
  -u slametsantoso
# Masukkan password Snowflake saat diminta
```

### 2. Build Docker Image

Dari root folder project (`d:\Codes\Clarifi_Development`):

```bash
docker build -t clarifi:latest -f deploy/Dockerfile .
```

Dockerfile menggunakan multi-stage build:
- Stage 1: Build frontend Next.js (node:20-alpine)
- Stage 2: Production image (python:3.11-slim + Node.js + nginx + supervisor)

### 3. Tag Image untuk Registry

```bash
docker tag clarifi:latest \
  yhnomry-uw19292.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
```

### 4. Push Image ke Registry

```bash
docker push \
  yhnomry-uw19292.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
```

### 5. Buat/Update Service di Snowflake

Jalankan di Snowsight atau via `snow sql`:

```sql
-- Buat service (pertama kali)
CREATE SERVICE IF NOT EXISTS CLARIFI.CLAIMS.CLARIFI_APP
  IN COMPUTE POOL SYSTEM_COMPUTE_POOL_CPU
  FROM SPECIFICATION $$
spec:
  containers:
  - name: clarifi
    image: /clarifi/claims/clarifi_repo/clarifi:latest
    resources:
      requests:
        cpu: 0.5
        memory: 1Gi
      limits:
        cpu: 2
        memory: 4Gi
    ports:
    - name: http
      port: 8080
      protocol: TCP
  endpoints:
  - name: app
    port: 8080
    public: true
  $$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1;
```

### 6. Cek Status Service

```sql
-- Lihat status
SELECT SYSTEM$GET_SERVICE_STATUS('CLARIFI.CLAIMS.CLARIFI_APP');

-- Lihat endpoint URL
SHOW ENDPOINTS IN SERVICE CLARIFI.CLAIMS.CLARIFI_APP;
```

---

## Update Setelah Perubahan Kode

Setiap kali ada perubahan kode, jalankan:

```bash
# 1. Build ulang
docker build -t clarifi:latest -f deploy/Dockerfile .

# 2. Tag
docker tag clarifi:latest \
  yhnomry-uw19292.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest

# 3. Push
docker push \
  yhnomry-uw19292.registry.snowflakecomputing.com/clarifi/claims/clarifi_repo/clarifi:latest
```

Lalu di Snowflake:

```sql
-- 4. Restart service agar ambil image baru
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;
```

---

## Operasional

### Suspend (hemat credit)
```sql
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
```

### Resume
```sql
ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;
```

### Hapus service
```sql
DROP SERVICE CLARIFI.CLAIMS.CLARIFI_APP;
```

### Lihat logs
```sql
SELECT SYSTEM$GET_SERVICE_LOGS('CLARIFI.CLAIMS.CLARIFI_APP', 0, 'clarifi', 100);
```

---

## File-File Deploy

| File | Fungsi |
|------|--------|
| `deploy/Dockerfile` | Multi-stage build (frontend + backend + nginx) |
| `deploy/nginx.conf` | Reverse proxy: /api/ → backend, /* → frontend |
| `deploy/supervisord.conf` | Process manager: nginx + backend + frontend |
| `deploy/spcs_deploy.sql` | SQL script untuk create/manage service |

---

## Catatan Penting

- **Auth di production:** Backend menggunakan SPCS token auth (`/snowflake/session/token`), bukan password. Tidak perlu `.env` file di production.
- **Next.js standalone mode:** Frontend di-build dengan output `standalone` agar bisa dijalankan dengan `node server.js` tanpa `npm start`.
- **File upload limit:** nginx dikonfigurasi `client_max_body_size 50M`.
- **Auto-suspend:** Compute pool auto-suspend setelah 300 detik idle — hemat biaya.
