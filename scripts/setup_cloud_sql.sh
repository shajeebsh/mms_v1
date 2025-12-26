#!/bin/bash

# Configuration
INSTANCE_NAME="mms-db"
DB_NAME="mms_prod"
DB_USER="mms_admin"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID not found. Run 'gcloud config set project [PROJECT_ID]'"
    exit 1
fi

echo "🚀 Setting up Cloud SQL Instance: ${INSTANCE_NAME} in project ${PROJECT_ID}..."

# 1. Create Instance
echo "🏗️ Creating instance (this may take 5-10 minutes)..."
gcloud sql instances create ${INSTANCE_NAME} \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=${REGION}

# 2. Create Database
echo "📁 Creating database ${DB_NAME}..."
gcloud sql databases create ${DB_NAME} --instance=${INSTANCE_NAME}

# 3. Create User
echo "👤 Creating user ${DB_USER}..."
DB_PASSWORD=$(openssl rand -base64 12)
gcloud sql users create ${DB_USER} \
    --instance=${INSTANCE_NAME} \
    --password=${DB_PASSWORD}

# 4. Get Connection Name
CONNECTION_NAME=$(gcloud sql instances describe ${INSTANCE_NAME} --format='value(connectionName)')

echo "✅ Setup Complete!"
echo "--------------------------------------------------"
echo "Database Details (SAVE THESE!):"
echo "  Instance: ${INSTANCE_NAME}"
echo "  Database: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo "  Password: ${DB_PASSWORD}"
echo "  Connection Name: ${CONNECTION_NAME}"
echo ""
echo "DATABASE_URL for Cloud Run:"
echo "  postgres://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"
echo "--------------------------------------------------"
