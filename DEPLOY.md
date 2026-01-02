# 🚀 Deployment Guide: Supply Chain Guardian

This guide helps you deploy the full system to Google Cloud:
1.  **Database**: AlloyDB for PostgreSQL
2.  **AI Brain**: Vertex AI Agent Engine
3.  **User Interface**: Streamlit on Cloud Run

---

## 🛠️ Prerequisites

Ensure you have your **Project ID** and **Region** ready.
```bash
export PROJECT_ID="your-project-id"  # REPLACE THIS
export REGION="us-central1"
export SERVICE_ACCOUNT="supply-chain-agent@${PROJECT_ID}.iam.gserviceaccount.com"
```

---

## 1️⃣ Set up AlloyDB

AlloyDB is the high-performance PostgreSQL backend.

### A. Enable APIs
```bash
gcloud services enable alloydb.googleapis.com \
    servicenetworking.googleapis.com \
    compute.googleapis.com
```

### B. Create Cluster & Instance
*Note: This creates a primary cluster and instance. It takes ~15-20 minutes.*

```bash
# 1. Create a password for the 'postgres' user
export DB_PASS="supplychain123" 

# 2. Create the Cluster
gcloud alloydb clusters create supply-chain-cluster \
    --region=$REGION \
    --password=$DB_PASS

# 3. Create the Primary Instance
gcloud alloydb instances create supply-chain-instance \
    --cluster=supply-chain-cluster \
    --region=$REGION \
    --cpu-count=2 \
    --instance-type=PRIMARY
```

### C. Create the Database
```bash
# Get the IP address of the instance (Wait for instance to be READY)
export DB_IP=$(gcloud alloydb instances describe supply-chain-instance --cluster=supply-chain-cluster --region=$REGION --format="value(ipAddress)")

# We need a VM or Cloud Shell to connect initially to create the DB tables if not using the script remotely.
# For simplicity, we will let the App create tables if they don't exist, using the 'postgres' default DB.
```

---

## 2️⃣ Deploy the AI Agent ("The Brain")

This deploys the reasoning engine to Vertex AI.

```bash
# 1. Install dependencies locally if needed
pip install -r requirements.txt

# 2. Authenticate
gcloud auth application-default login

# 3. Deploy
python deploy.py
```

**⚠️ IMPORTANT**: After deployment, copy the **Agent Resource Name** (e.g., `projects/123/locations/us-central1/reasoningEngines/456...`).

---

## 3️⃣ Deploy the UI to Cloud Run

### A. Build the Container
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/supply-chain-ui
```

### B. Deploy to Cloud Run
Replace `[AGENT_RESOURCE_NAME]` with the value from Step 2.

```bash
export AGENT_RESOURCE_NAME="projects/..." # REPLACE THIS

gcloud run deploy supply-chain-ui \
    --image gcr.io/$PROJECT_ID/supply-chain-ui \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars="GOOGLE_CLOUD_REGION=$REGION" \
    --set-env-vars="ALLOYDB_PROJECT=$PROJECT_ID" \
    --set-env-vars="ALLOYDB_REGION=$REGION" \
    --set-env-vars="ALLOYDB_CLUSTER=supply-chain-cluster" \
    --set-env-vars="ALLOYDB_INSTANCE=supply-chain-instance" \
    --set-env-vars="DB_USER=postgres" \
    --set-env-vars="DB_PASS=supplychain123" \
    --set-env-vars="AGENT_RESOURCE_NAME=$AGENT_RESOURCE_NAME"
```

---

## 4️⃣ Verify Deployment

1.  Open the **Cloud Run URL** provided in the output.
2.  The app will attempt to connect to AlloyDB on startup.
3.  Ask the agent: *"What is the current stock level of CHIP-X?"*

---

## 🧹 Cleanup (To avoid costs)

```bash
# Delete Cloud Run Service
gcloud run services delete supply-chain-ui --region=$REGION

# Delete AlloyDB Cluster (Deletes all data!)
gcloud alloydb clusters delete supply-chain-cluster --region=$REGION --force

# Delete Vertex AI Reasonin Engine
# (Do this from the Cloud Console)
```
