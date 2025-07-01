# Backend API Deployment Guide - Google Cloud Run

This guide explains how to deploy the updated backend API with the new `verification_status` field and other enhancements.

## Prerequisites

1. Google Cloud SDK (`gcloud`) installed and configured
2. Docker installed (for local testing)
3. Access to the Google Cloud project

## Steps to Deploy

### 1. Ensure You're in the Backend Directory

```bash
cd backend-api
```

### 2. Set Google Cloud Project (if not already set)

```bash
gcloud config set project YOUR_PROJECT_ID
```

### 3. Build and Deploy to Cloud Run

Option A: Deploy directly from source (recommended):

```bash
gcloud run deploy lexleaks-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",SECRET_KEY="${SECRET_KEY}",ADMIN_USERNAME="${ADMIN_USERNAME}",ADMIN_PASSWORD="${ADMIN_PASSWORD}"
```

Option B: Build and push Docker image manually:

```bash
# Build the Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lexleaks-api

# Deploy to Cloud Run
gcloud run deploy lexleaks-api \
  --image gcr.io/YOUR_PROJECT_ID/lexleaks-api \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="${DATABASE_URL}",SECRET_KEY="${SECRET_KEY}",ADMIN_USERNAME="${ADMIN_USERNAME}",ADMIN_PASSWORD="${ADMIN_PASSWORD}"
```

### 4. Run Database Migrations

After deployment, you need to run the Alembic migrations to add the new `verification_status` column:

```bash
# Option 1: Connect to Cloud SQL proxy and run migrations locally
# First, set up Cloud SQL proxy if needed

# Option 2: Run migrations using a one-off container
gcloud run jobs create run-migrations \
  --image gcr.io/YOUR_PROJECT_ID/lexleaks-api \
  --region asia-south1 \
  --set-env-vars DATABASE_URL="${DATABASE_URL}" \
  --command alembic \
  --args "upgrade,head"

# Execute the job
gcloud run jobs execute run-migrations --region asia-south1
```

### 5. Verify Deployment

Test the updated API:

```bash
# Check health
curl https://lexleaks-api-563011146464.asia-south1.run.app/health

# Test the new filtering parameters
curl "https://lexleaks-api-563011146464.asia-south1.run.app/api/posts/?verification_status=verified"
```

## Environment Variables Required

Make sure these are set in Cloud Run:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key for authentication
- `ADMIN_USERNAME` - Admin username
- `ADMIN_PASSWORD` - Admin password

## What's New in This Deployment

1. **New Database Field**: `verification_status` column added to posts table
2. **Enhanced Filtering**:
   - Filter by verification status (verified/unverified/disputed)
   - Filter by author username
   - Filter by impact level (high/medium/low)
   - Sort by impact count
3. **Impact Counting**: Posts now include `impact_count` in API responses
4. **New Endpoints**: Impact tracking endpoints at `/api/impacts/`

## Rollback Plan

If needed, you can rollback to the previous version:

```bash
gcloud run services update-traffic lexleaks-api --to-revisions=PREVIOUS_REVISION_ID=100 --region asia-south1
```

## Notes

- The frontend expects the API to return `verification_status` and `impact_count` fields
- Make sure to update the frontend deployment after the backend is successfully deployed
- The migration adds a default value of 'unverified' to existing posts 