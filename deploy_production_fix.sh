#!/bin/bash

# LexLeaks Production Deployment Script with Scheduler Fix
# This script deploys the fixed scheduler to production

echo "🚀 Deploying LexLeaks to Production with Scheduler Fix..."

# Set variables
PROJECT_ID="lexleaks-api"
SERVICE_NAME="lexleaks-api"
REGION="asia-south1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Navigate to backend directory
cd backend-api

echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --concurrency 1000 \
  --max-instances 10 \
  --set-env-vars "K_SERVICE=$SERVICE_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --update-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY,INDIAN_KANOON_API_KEY=$INDIAN_KANOON_API_KEY"

echo "✅ Deployment complete!"
echo "🔍 Testing scheduler status..."

# Wait for deployment to complete
sleep 30

# Test the health endpoint
echo "Testing health endpoint..."
curl -s "https://$SERVICE_NAME-$REGION.run.app/health" | jq '.'

echo "Testing scheduler status..."
curl -s "https://$SERVICE_NAME-$REGION.run.app/api/scheduler/status" | jq '.'

echo "🎉 Production deployment with scheduler fix complete!"
echo "📊 Monitor logs with: gcloud logs tail --follow --project=$PROJECT_ID"
