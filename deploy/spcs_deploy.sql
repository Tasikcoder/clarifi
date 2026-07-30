-- ClariFi SPCS Deployment Script
-- Run these commands in order after pushing Docker image

-- 1. Image Repository (already created)
-- CREATE IMAGE REPOSITORY IF NOT EXISTS CLARIFI.CLAIMS.CLARIFI_REPO;

-- 2. Use existing compute pool (or create new one)
-- Account already has SYSTEM_COMPUTE_POOL_CPU. We'll use that.
-- If you prefer a dedicated pool:
-- CREATE COMPUTE POOL CLARIFI_POOL
--   MIN_NODES = 1 MAX_NODES = 1
--   INSTANCE_FAMILY = CPU_X64_XS
--   AUTO_SUSPEND_SECS = 300
--   AUTO_RESUME = TRUE;

-- 3. Create the service
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

-- 4. Check service status
-- SHOW SERVICES IN SCHEMA CLARIFI.CLAIMS;
-- SELECT SYSTEM$GET_SERVICE_STATUS('CLARIFI.CLAIMS.CLARIFI_APP');

-- 5. Get public endpoint URL
-- SHOW ENDPOINTS IN SERVICE CLARIFI.CLAIMS.CLARIFI_APP;

-- 6. To update after code changes:
-- ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;
-- ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP RESUME;

-- 7. To stop (save credits):
-- ALTER SERVICE CLARIFI.CLAIMS.CLARIFI_APP SUSPEND;

-- 8. To remove completely:
-- DROP SERVICE CLARIFI.CLAIMS.CLARIFI_APP;
