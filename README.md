# Snowflake Multi-Touch Attribution (MTA) Demo

A full-stack multi-touch attribution platform built entirely on Snowflake, featuring 6 attribution models, media mix modeling, propensity scoring, and an interactive React dashboard deployed via Snowpark Container Services (SPCS).

## Overview

This project demonstrates how to build an end-to-end marketing analytics solution on Snowflake using:

- **4.4M impressions** across **8 channels** (search, social, display, CTV, OLV, native, audio, DOOH)
- **50,000 synthetic users** with **34,609 resolved identities** via identity resolution
- **6 attribution models**: last-touch, first-touch, linear, time-decay, position-based, Shapley
- **Media Mix Modeling (MMM)** with Bayesian ridge regression
- **Propensity scoring** with gradient-boosted classification
- **Channel forecasting** with Snowflake Cortex ML
- **Budget optimization** with scipy constrained optimization
- **Cortex Agent** for natural language analytics queries

## Architecture

```
Raw Data (Snowflake)
  → dbt transformations (staging + analytics)
    → Python analytics (attribution, MMM, propensity, forecasting)
      → React dashboard (Vite + TailwindCSS)
        → FastAPI backend
          → Deployed on SPCS
```

## Project Structure

```
├── app/
│   ├── backend/          # FastAPI API server
│   └── frontend/         # React + Vite + TailwindCSS dashboard
├── dbt_mta/              # dbt project for data transformations
├── deploy/               # SPCS deployment scripts
├── notebooks/            # Snowflake notebooks for analytics
├── streamlit_app/        # Streamlit companion app
├── Dockerfile            # Multi-stage build (frontend + backend)
└── README.md
```

## Prerequisites

- Snowflake account with ACCOUNTADMIN access
- Docker (for building the SPCS image)
- Node.js 18+ and Python 3.11+
- dbt-core with dbt-snowflake adapter

## Quick Start

1. **Set up Snowflake objects**: Run `deploy/spcs_setup.sql` to create the database, schemas, warehouse, compute pool, and image repository.

2. **Configure connections**: Set environment variables:
   ```bash
   export SNOWFLAKE_CONNECTION_NAME=my_connection
   export SNOWFLAKE_WAREHOUSE=MTA_WH
   ```

3. **Run dbt models**: 
   ```bash
   cd dbt_mta
   dbt run --profiles-dir profiles
   ```

4. **Run analytics notebooks** in Snowflake to populate attribution results, MMM coefficients, propensity scores, and forecasts.

5. **Build and deploy the dashboard**:
   ```bash
   bash deploy/deploy.sh
   ```

## License

Apache 2.0
