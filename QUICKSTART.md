# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
python -m venv virtualenv
source virtualenv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your credentials:
# - GOOGLE_CLOUD_PROJECT
# - WEATHER_API_KEY (free from openweathermap.org)
```

### Step 3: Initialize Database
```bash
python setup_database.py
```

### Step 4: Test Locally
```bash
# Test agents
python main.py

# Launch dashboard
streamlit run ui/app.py
```

## 🎯 What Can It Do?

Try these commands in the UI chat:

1. **"What is our current inventory status?"**
   → Shows all products and stock levels

2. **"Predict delays for incoming shipments"**
   → Analyzes weather and provides delay estimates

3. **"What products should we add based on trends?"**
   → Suggests new products using market intelligence

4. **"What's the weather risk in Mumbai?"**
   → Checks real-time weather impact on logistics

5. **"Check supply chain resilience"**
   → Provides health score and vulnerability analysis

## 📊 Dashboard Features

- **Chat**: Natural language queries
- **Inventory**: Real-time stock monitoring
- **Analytics**: Charts and metrics
- **Alerts**: Critical warnings
- **Risks**: Weather and news events

## 🌩️ Deploy to Google Cloud

```bash
# 1. Set up Google Cloud (see SETUP.md)
# 2. Configure environment variables
# 3. Deploy
python deploy.py
```

## ❓ Troubleshooting

**Database errors**: Run `python setup_database.py`

**API errors**: Check `.env` file has correct API keys

**Import errors**: Activate virtualenv: `source virtualenv/Scripts/activate`

**Vertex AI errors**: Ensure GOOGLE_CLOUD_PROJECT is set

## 📚 Next Steps

- Read [SETUP.md](SETUP.md) for production deployment
- Read [README.md](README.md) for full documentation
- Configure alerting with Pub/Sub
- Set up AlloyDB for production database

---

Need help? Check the documentation or create an issue!
