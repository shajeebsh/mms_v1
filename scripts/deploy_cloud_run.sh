#!/bin/bash

# Configuration - Replace these or pass as environment variables
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="mms-v1"
REGION="us-central1" # Or your preferred region
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Ensure we are in the project root
cd "$(dirname "$0")/.."

echo "🚀 Starting deployment for ${SERVICE_NAME} in project ${PROJECT_ID}..."

# 1. Build the image using Cloud Build
echo "📦 Building container image..."
gcloud builds submit --tag "${IMAGE_TAG}"

# 2. Deploy to Cloud Run
# Note: You will need to manually update environment variables like DATABASE_URL 
# and DJANGO_SECRET_KEY in the Cloud console or via --set-env-vars
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --memory 512Mi

echo "✅ Deployment requested. Check the URL above once finished."
echo "💡 Reminder: You MUST configure your environment variables in the Cloud Console:"
echo "   1. DATABASE_URL"
echo "   2. DJANGO_SECRET_KEY"
echo "   3. CLOUD_SQL_INSTANCES (Add your connection name here)"
echo "   4. CSRF_TRUSTED_ORIGINS (Set to the URL provided above)"
