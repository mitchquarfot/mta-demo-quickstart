#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="mta-dashboard"
IMAGE_TAG="latest"
SNOW_CONN="${SNOWFLAKE_CONNECTION_NAME:-my_connection}"

echo "=== MTA Dashboard SPCS Deployment ==="

echo "1. Getting SPCS image repository URL..."
REPO_URL=$(SNOWFLAKE_CONNECTION_NAME="$SNOW_CONN" python3 -c "
import os, snowflake.connector
conn = snowflake.connector.connect(connection_name=os.environ['SNOWFLAKE_CONNECTION_NAME'], database='MTA_DEMO')
cur = conn.cursor()
cur.execute('SHOW IMAGE REPOSITORIES IN SCHEMA MTA_DEMO.RAW')
for row in cur:
    cols = [d[0] for d in cur.description]
    rec = dict(zip(cols, row))
    if rec.get('name') == 'IMAGES':
        print(rec['repository_url'])
        break
conn.close()
")

if [ -z "$REPO_URL" ]; then
    echo "ERROR: Could not find image repository URL. Run deploy/spcs_setup.sql first."
    exit 1
fi

FULL_IMAGE="${REPO_URL}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "   Repository: ${FULL_IMAGE}"

echo "2. Building Docker image..."
cd "$PROJECT_ROOT"
docker build --platform linux/amd64 -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "3. Tagging for SPCS registry..."
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${FULL_IMAGE}"

echo "4. Logging into SPCS registry..."
snow spcs image-registry login -c "$SNOW_CONN"

echo "5. Pushing image to SPCS..."
docker push "${FULL_IMAGE}"

echo "6. Creating/updating SPCS service..."
snow sql -c "$SNOW_CONN" -q "
DROP SERVICE IF EXISTS MTA_DEMO.RAW.MTA_DASHBOARD;
CREATE SERVICE MTA_DEMO.RAW.MTA_DASHBOARD
  IN COMPUTE POOL MTA_DASHBOARD_POOL
  FROM SPECIFICATION \$\$
spec:
  containers:
    - name: mta-dashboard
      image: ${FULL_IMAGE}
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
        path: /healthz
  endpoints:
    - name: dashboard
      port: 8080
      public: true
\$\$
  MIN_INSTANCES = 1
  MAX_INSTANCES = 1
  QUERY_WAREHOUSE = MTA_WH;
"

echo "7. Waiting for service to start..."
sleep 10
snow sql -c "$SNOW_CONN" -q "SELECT SYSTEM\$GET_SERVICE_STATUS('MTA_DEMO.RAW.MTA_DASHBOARD')"

echo ""
echo "8. Getting endpoint URL..."
snow sql -c "$SNOW_CONN" -q "SHOW ENDPOINTS IN SERVICE MTA_DEMO.RAW.MTA_DASHBOARD"

echo ""
echo "=== Deployment complete! ==="
