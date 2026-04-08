-- ============================================================
-- SPCS Infrastructure for MTA Dashboard
-- Run as ACCOUNTADMIN
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE DATABASE MTA_DEMO;
USE SCHEMA RAW;

-- 1. Image Repository
CREATE IMAGE REPOSITORY IF NOT EXISTS MTA_DEMO.RAW.IMAGES;

-- 2. Compute Pool
CREATE COMPUTE POOL IF NOT EXISTS MTA_DASHBOARD_POOL
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS;

-- 3. Service spec YAML is provided inline below
-- First, get the image repository URL:
SHOW IMAGE REPOSITORIES IN SCHEMA MTA_DEMO.RAW;

-- After pushing the image, create the service:
-- (Replace <REPO_URL> with the actual repository URL from SHOW IMAGE REPOSITORIES)
/*
CREATE SERVICE IF NOT EXISTS MTA_DEMO.RAW.MTA_DASHBOARD
  IN COMPUTE POOL MTA_DASHBOARD_POOL
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1
  SPEC = $$
spec:
  containers:
    - name: mta-dashboard
      image: <REPO_URL>/mta-dashboard:latest
      env:
        SNOWFLAKE_WAREHOUSE: MTA_WH
      resources:
        requests:
          cpu: 0.5
          memory: 1Gi
        limits:
          cpu: 2
          memory: 4Gi
      readinessProbe:
        port: 8080
        path: /api/v1/kpis
  endpoints:
    - name: dashboard
      port: 8080
      public: true
$$
  EXTERNAL_ACCESS_INTEGRATIONS = ()
  QUERY_WAREHOUSE = MTA_WH;

-- 4. Grant public access
GRANT USAGE ON SERVICE MTA_DEMO.RAW.MTA_DASHBOARD TO ROLE PUBLIC;
*/
