#!/bin/bash

# Test Production Scheduler Fix
# This script tests if the scheduler is working in production

echo "🔍 Testing Production Scheduler Fix..."

API_URL="https://lexleaks-api-563011146464.asia-south1.run.app"

echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | jq '.'

echo -e "\n2. Testing scheduler status..."
curl -s "$API_URL/api/scheduler/status" | jq '.'

echo -e "\n3. Testing scheduler stats..."
curl -s "$API_URL/api/scheduler/stats" | jq '.'

echo -e "\n4. Testing web scraping..."
curl -s "$API_URL/api/pipeline/scrape-legal-news" | jq '.success, .articles_count'

echo -e "\n5. Testing Gemini topic generation..."
curl -s "$API_URL/api/pipeline/generate-topics" | jq '.success, .topics | length'

echo -e "\n6. Testing manual pipeline run..."
curl -s -X POST "$API_URL/api/scheduler/run-now" \
  -H "Content-Type: application/json" \
  -d '{"mode": "generate"}' | jq '.'

echo -e "\n7. If scheduler is not running, force starting..."
SCHEDULER_STATUS=$(curl -s "$API_URL/api/scheduler/status" | jq -r '.is_running')

if [ "$SCHEDULER_STATUS" = "false" ]; then
    echo "⚠️  Scheduler not running, force starting..."
    curl -s -X POST "$API_URL/api/scheduler/force-start" | jq '.'
    
    echo "Waiting 5 seconds..."
    sleep 5
    
    echo "Re-checking scheduler status..."
    curl -s "$API_URL/api/scheduler/status" | jq '.'
fi

echo -e "\n✅ Production scheduler test complete!"
