# Supply Chain Guardian - Complete Setup Guide

## 🎯 Overview
A multi-agent AI system that tracks inventory, predicts delivery delays using weather data, and suggests products based on market trends.

## 📋 Prerequisites

### 1. Google Cloud Project Setup
```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export PROJECT_NUMBER="your-project-number"
export REGION="us-central1"

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  storage-api.googleapis.com \
  alloydb.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com \
  pubsub.googleapis.com \
  cloudbuild.googleapis.com
```

### 2. Create Storage Bucket
```bash
export STAGING_BUCKET="gs://${PROJECT_ID}-agent-staging"
gcloud storage buckets create $STAGING_BUCKET --location=$REGION
```

### 3. Set up AlloyDB (or Cloud SQL)

#### Option A: AlloyDB (Recommended for production)
```bash
# Create AlloyDB cluster
gcloud alloydb clusters create supply-chain-cluster \
  --password=YOUR_SECURE_PASSWORD \
  --network=default \
  --region=$REGION

# Create primary instance
gcloud alloydb instances create supply-chain-primary \
  --cluster=supply-chain-cluster \
  --instance-type=PRIMARY \
  --cpu-count=2 \
  --region=$REGION
```

#### Option B: Cloud SQL (Easier for testing)
```bash
gcloud sql instances create supply-chain-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create inventory --instance=supply-chain-db
```

### 4. Create Secrets for API Keys
```bash
# Weather API (OpenWeatherMap or similar)
echo -n "your-weather-api-key" | gcloud secrets create weather-api-key --data-file=-

# Database connection string
echo -n "postgresql://user:pass@host:5432/inventory" | gcloud secrets create db-connection-string --data-file=-

# News/Trends API key (optional)
echo -n "your-news-api-key" | gcloud secrets create news-api-key --data-file=-
```

### 5. Set up IAM Permissions
```bash
# Get your default service account
export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/alloydb.client"
```

## 🔧 Local Development Setup

### 1. Create Environment File
Create `.env` file in project root:
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
STAGING_BUCKET=gs://your-project-id-agent-staging

# Database
DB_CONNECTION_STRING=postgresql://user:pass@localhost:5432/inventory
# Or for AlloyDB:
# DB_CONNECTION_STRING=postgresql://user:pass@10.0.0.3:5432/inventory

# API Keys
WEATHER_API_KEY=your-openweathermap-api-key
NEWS_API_KEY=your-news-api-key

# Alerting
ALERT_EMAIL=alerts@yourcompany.com
PUBSUB_TOPIC=projects/your-project-id/topics/inventory-alerts
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv virtualenv
source virtualenv/Scripts/activate  # Windows
# source virtualenv/bin/activate    # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python setup_database.py
```

## 🚀 Deployment

### 1. Test Locally
```bash
python main.py
```

### 2. Deploy to Vertex AI
```bash
source .env
python deploy.py
```

### 3. Run Streamlit UI
```bash
streamlit run ui/app.py
```

## 📊 API Keys to Obtain

1. **OpenWeatherMap** (Free tier available)
   - Sign up at: https://openweathermap.org/api
   - Get API key for Current Weather Data

2. **NewsAPI** (Optional - for trend analysis)
   - Sign up at: https://newsapi.org/
   - Free tier: 100 requests/day

3. **Google Search API** (Optional)
   - Enable Custom Search API in Google Cloud Console
   - Create API credentials

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Supply Chain Guardian                  │
│                    (Orchestrator)                       │
└────────────┬───────────────┬────────────────┬──────────┘
             │               │                │
   ┌─────────▼─────┐  ┌─────▼──────┐  ┌──────▼──────┐
   │ Inventory Ops │  │  Strategy  │  │   Market    │
   │    Agent      │  │   Agent    │  │   Agent     │
   └───────┬───────┘  └──────┬─────┘  └──────┬──────┘
           │                 │                │
   ┌───────▼─────────────────▼────────────────▼──────┐
   │              Data Sources & Tools               │
   │  • AlloyDB (Inventory)                         │
   │  • Weather API (OpenWeatherMap)                │
   │  • News API (Trends)                           │
   │  • Pub/Sub (Alerts)                            │
   └────────────────────────────────────────────────┘
```

## 📝 Next Steps

1. ✅ Configure Google Cloud project
2. ✅ Set up database and initialize schema
3. ✅ Obtain and configure API keys
4. ✅ Test agents locally
5. ✅ Deploy to Vertex AI
6. ✅ Configure alerting
7. ✅ Launch Streamlit dashboard

## 🔍 Monitoring

Access your deployed agent:
```python
from vertexai.preview import reasoning_engines

# Load deployed agent
agent = reasoning_engines.ReasoningEngine("projects/.../reasoningEngines/...")
response = agent.query(input="What's our inventory status?")
```

## 🐛 Troubleshooting

### Database Connection Issues
- Ensure VPC/firewall rules allow connections
- Verify credentials in Secret Manager
- Use Cloud SQL Proxy for local testing

### API Rate Limits
- Weather API: 60 calls/minute (free tier)
- Implement caching to reduce calls
- Consider upgrading for production

### Agent Deployment Failures
- Check service account permissions
- Verify all dependencies in requirements.txt
- Review Cloud Build logs in GCP Console
