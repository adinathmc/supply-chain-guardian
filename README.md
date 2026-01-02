# 🛡️ Supply Chain Guardian

> An intelligent multi-agent AI system for real-time supply chain management, powered by Google Cloud Vertex AI

⚠️ **INTERNAL PROJECT - TEAM ACCESS ONLY**  
📝 **Status:** Under Active Development - See [KNOWN_ISSUES.md](KNOWN_ISSUES.md)

---

## 🔒 Access & Usage

**This is proprietary software for internal team use only.**
- Not open source - all rights reserved
- Team members only - do not share externally
- See [LICENSE](LICENSE) for full terms

**Getting Started?** Jump to [QUICKSTART.md](QUICKSTART.md) (5 minutes)

---

## ✨ Features

### 🤖 Multi-Agent Architecture
- **Inventory Operations Agent**: Real-time stock monitoring and alerting
- **Strategy Agent**: Delay prediction using weather and external data
- **Market Intelligence Agent**: Trend analysis and product recommendations
- **Orchestrator**: Intelligent query routing between specialized agents

### 📊 Core Capabilities
- ✅ Real-time inventory tracking with automated alerts
- 🌤️ Weather-based delivery delay prediction
- 📈 Market trend analysis for product suggestions
- 🚨 Critical stock alerting system
- 📦 Shipment tracking and risk assessment
- 💪 Supply chain resilience scoring
- 🎯 Intelligent reorder recommendations

### 🔧 Technology Stack
- **AI/ML**: Google Vertex AI, Gemini 2.0 Flash
- **Database**: PostgreSQL/AlloyDB with SQLAlchemy
- **APIs**: OpenWeatherMap, NewsAPI
- **Frontend**: Streamlit
- **Cloud**: Google Cloud Platform

## 🚀 Quick Start

### Prerequisites
1. Python 3.10+
2. Google Cloud Project with billing enabled
3. API Keys (OpenWeatherMap - free tier available)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd supply-chain-guardian

# 2. Create virtual environment
python -m venv virtualenv
source virtualenv/Scripts/activate  # Windows
# source virtualenv/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
python setup_database.py

# 6. Test locally
python main.py
```

### Environment Variables

Create a `.env` file:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
STAGING_BUCKET=gs://your-bucket-name

# Database (SQLite by default, or use PostgreSQL/AlloyDB)
DB_CONNECTION_STRING=sqlite:///supply_chain.db
# DB_CONNECTION_STRING=postgresql://user:pass@host:5432/dbname

# API Keys
WEATHER_API_KEY=your-openweathermap-key
NEWS_API_KEY=your-newsapi-key  # Optional

# Alerting (Optional)
PUBSUB_TOPIC=projects/your-project/topics/alerts
ALERT_EMAIL=alerts@yourcompany.com
```

## 📖 Usage

### Local Testing
```bash
# Test all agents
python main.py

# Run alerting check
python alerting.py

# Launch Streamlit UI
streamlit run ui/app.py
```

### Deploy to Google Cloud
```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export STAGING_BUCKET=gs://your-bucket

# Deploy to Vertex AI
python deploy.py
```

### Query Examples

**Inventory Status**:
```python
agent.query("What is our current inventory status?")
agent.query("Is CHIP-X in stock?")
```

**Delay Prediction**:
```python
agent.query("Predict delays for incoming shipments")
agent.query("What's the weather risk in Mumbai?")
```

**Market Intelligence**:
```python
agent.query("What products should we add based on trends?")
agent.query("Show me supply chain disruptions")
```

**Strategic Planning**:
```python
agent.query("What's our supply chain resilience score?")
agent.query("Which products need reordering?")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│     Supply Chain Guardian (Orchestrator)    │
│         Intelligent Query Routing           │
└────────┬──────────────┬──────────────┬──────┘
         │              │              │
   ┌─────▼────┐   ┌────▼─────┐  ┌────▼────┐
   │   Ops    │   │ Strategy │  │ Market  │
   │  Agent   │   │  Agent   │  │  Agent  │
   └─────┬────┘   └────┬─────┘  └────┬────┘
         │             │             │
   ┌─────▼─────────────▼─────────────▼──────┐
   │        Data Layer & Services            │
   │  • Database (AlloyDB/PostgreSQL)       │
   │  • Weather API (OpenWeatherMap)        │
   │  • News API (Trends & Events)          │
   │  • Alerting (Pub/Sub)                  │
   └────────────────────────────────────────┘
```

## 📁 Project Structure

```
supply-chain-guardian/
├── main.py                  # Orchestrator & main entry point
├── deploy.py               # Google Cloud deployment script
├── setup_database.py       # Database initialization
├── database.py             # Database models & operations
├── external_services.py    # Weather & news API integration
├── alerting.py            # Alerting system
├── requirements.txt       # Python dependencies
├── SETUP.md              # Detailed setup instructions
├── agents/
│   ├── ops_agent.py      # Inventory operations agent
│   ├── strat_agent.py    # Strategy & delay prediction
│   └── market_agent.py   # Market intelligence
└── ui/
    └── app.py            # Streamlit dashboard

## 🔧 Configuration

### Google Cloud Setup

See [SETUP.md](SETUP.md) for detailed instructions on:
- Enabling required APIs
- Creating storage buckets
- Setting up AlloyDB/Cloud SQL
- Configuring service accounts
- Managing secrets

### API Keys

**OpenWeatherMap** (Required for weather features):
1. Sign up at https://openweathermap.org/api
2. Get free API key (60 calls/minute)
3. Add to `.env` as `WEATHER_API_KEY`

**NewsAPI** (Optional for trend analysis):
1. Sign up at https://newsapi.org/
2. Get free API key (100 requests/day)
3. Add to `.env` as `NEWS_API_KEY`

## 🚨 Alerting

The system automatically checks for:
- Critical stock levels (out of stock)
- Low stock warnings (below threshold)
- Delayed shipments (>3 days)

Alerts can be sent via:
- Google Pub/Sub (configured via `PUBSUB_TOPIC`)
- Console logging (default)
- Email (future enhancement)

## 📊 Dashboard Features

The Streamlit UI provides:
- 💬 **Chat Interface**: Natural language queries to AI
- 📦 **Inventory Dashboard**: Real-time stock levels
- 📊 **Analytics**: Charts and metrics
- 🚨 **Alert Center**: Active warnings
- 🌍 **Risk Monitor**: Weather and news events

## 🧪 Testing

```bash
# Run main test suite
python main.py

# Test individual agents
python -c "from agents.ops_agent import InventoryOpsAgent; agent = InventoryOpsAgent('test', 'us-central1'); print(agent.query('check inventory'))"

# Test alerting
python alerting.py
```

## 📚 Documentation

- [SETUP.md](SETUP.md) - Detailed setup and deployment guide
- [API Documentation](https://cloud.google.com/vertex-ai/docs)
- [Agent Development Guide](docs/agents.md) - Coming soon

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🆘 Support

**For Team Members:**
- Check [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for current bugs
- Review [SETUP.md](SETUP.md) for configuration help
- Contact project owner for access or major issues
- Use team chat for quick questions

## 🎯 Roadmap

- [ ] Email alerting integration
- [ ] Advanced ML forecasting models
- [ ] Multi-warehouse optimization
- [ ] Mobile app
- [ ] Integration with ERP systems
- [ ] Real-time dashboard updates
- [ ] Custom report generation

## 🙏 Acknowledgments

**Project Team:**
- Internal development team
- Project owner/lead

**Technology:**
- Google Cloud Vertex AI team
- OpenWeatherMap API
- Streamlit community

---

**Status:** Under Active Development | **License:** Proprietary | **Access:** Team Only

Built with ❤️ using Google Cloud Vertex AI
```