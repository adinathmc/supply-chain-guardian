#!/bin/bash

# Configuration
# Set these or ensure they are exported in your shell
: "${PROJECT_ID:?Need to set PROJECT_ID}"
: "${REGION:=us-central1}"
: "${DB_PASS:=supplychain123}"

echo "=================================================="
echo "🚀 Creating Infrastructure for Supply Chain Guardian"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "=================================================="

# 1. Enable APIs
echo ""
echo "Enabling APIs..."
gcloud services enable alloydb.googleapis.com \
    servicenetworking.googleapis.com \
    compute.googleapis.com

# 2. Setup AlloyDB
echo ""
echo "Creating AlloyDB Cluster (this takes ~15 mins)..."
gcloud alloydb clusters create supply-chain-cluster \
    --region=$REGION \
    --password=$DB_PASS

echo "Creating AlloyDB Instance..."
gcloud alloydb instances create supply-chain-instance \
    --cluster=supply-chain-cluster \
    --region=$REGION \
    --cpu-count=2 \
    --instance-type=PRIMARY

# 3. Deploy Agent
echo ""
echo "Deploying Vertex AI Agent..."
python deploy.py

echo ""
echo "=================================================="
echo "✅ Infrastructure setup complete!"
echo "Now run the following to deploy the UI:"
echo ""
echo "export AGENT_RESOURCE_NAME='Paste_Resource_Name_From_Above'"
echo "gcloud builds submit --tag gcr.io/$PROJECT_ID/supply-chain-ui"
echo "gcloud run deploy supply-chain-ui --image gcr.io/$PROJECT_ID/supply-chain-ui ..."
echo "=================================================="


