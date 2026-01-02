# Known Issues and Limitations

**Status:** Under Active Development ⚠️

This document tracks known issues, bugs, and limitations in the Supply Chain Guardian system.

## 🐛 Current Issues

### High Priority

1. **Google Cloud Authentication**
   - **Issue:** Requires local Google Cloud credentials even for fallback mode
   - **Workaround:** System automatically falls back to simple routing when Vertex AI unavailable
   - **Status:** Working as designed for local development
   - **Impact:** None for local testing

2. **Database Session Management**
   - **Issue:** Some database queries may fail if session closes prematurely
   - **Fix Applied:** Using context managers in strategy agent
   - **Status:** Partially resolved, monitoring for other occurrences
   - **Impact:** Low - mainly affects delay prediction queries

3. **Weather API Mock Data**
   - **Issue:** Uses mock data when WEATHER_API_KEY not set
   - **Status:** By design - allows testing without API key
   - **Impact:** None - real API works when key provided
   - **Note:** Free OpenWeatherMap key recommended

### Medium Priority

4. **Streamlit UI Connection to Deployed Agent**
   - **Issue:** Requires manual resource name entry for deployed agents
   - **Status:** Works as designed
   - **Future:** Could auto-detect from config
   - **Impact:** Low - one-time setup

5. **Alert System**
   - **Issue:** Pub/Sub integration requires Google Cloud setup
   - **Status:** Falls back to console logging
   - **Impact:** None for local development
   - **Note:** Console logging works fine for testing

6. **Import Errors on First Run**
   - **Issue:** May show warnings about missing modules
   - **Fix:** Run `pip install -r requirements.txt`
   - **Status:** Expected behavior
   - **Impact:** Low - one-time setup issue

### Low Priority

7. **Agent Router Fallback**
   - **Issue:** Uses keyword-based routing when Gemini unavailable
   - **Status:** Working fallback mechanism
   - **Impact:** Minimal - fallback routing is functional
   - **Note:** Gemini routing is more accurate but not required

8. **Incomplete Error Messages**
   - **Issue:** Some error messages could be more descriptive
   - **Status:** Ongoing improvement
   - **Impact:** Low - basic debugging possible

## 🚧 Limitations

### Architecture
- **SQLite by default:** Not suitable for production at scale - use PostgreSQL/AlloyDB
- **Mock news data:** NewsAPI key optional but recommended for production
- **Single-threaded:** Streamlit UI doesn't support concurrent users efficiently

### API Dependencies
- **Weather API:** Limited to 60 calls/minute on free tier
- **News API:** Limited to 100 requests/day on free tier
- **Vertex AI:** Requires Google Cloud project with billing

### Data
- **Sample data only:** Includes 5 sample products for testing
- **Mock shipments:** Need real shipment tracking integration
- **No historical data:** Fresh database each time setup runs

### Scalability
- **Not production-ready:** Requires additional testing and hardening
- **No load balancing:** Single instance deployment
- **No caching:** API calls not cached (could improve performance)

## 🔧 Workarounds

### For Local Development
```bash
# If imports fail
pip install -r requirements.txt

# If database errors occur
python setup_database.py

# If Vertex AI errors
# Ignore them - system uses fallback mode automatically

# If weather API errors
# Leave WEATHER_API_KEY empty - uses realistic mock data
```

### For Testing Without API Keys
- Weather: Leave `WEATHER_API_KEY` empty - uses mock data
- News: Leave `NEWS_API_KEY` empty - uses mock trends
- Google Cloud: Not needed for local testing

## 📝 Not Bugs (By Design)

These are intentional behaviors:

- ✅ **Warnings about missing credentials** - Expected in local mode
- ✅ **Fallback to simple routing** - Designed for offline work
- ✅ **Mock data when APIs unavailable** - Allows testing without keys
- ✅ **Console logging for alerts** - Default when Pub/Sub not configured

## 🎯 Planned Improvements

### Short Term
- [ ] Better error messages
- [ ] More comprehensive input validation
- [ ] Additional test coverage
- [ ] Performance optimization

### Medium Term
- [ ] Email alerting integration
- [ ] Advanced caching layer
- [ ] Better multi-user support
- [ ] Real-time dashboard updates

### Long Term
- [ ] Production hardening
- [ ] Load balancing support
- [ ] Advanced ML forecasting
- [ ] Mobile app

## 🆘 Reporting Issues

Found a new issue? Document it with:
- What you were trying to do
- What happened
- Error messages (full text)
- Your environment (OS, Python version)
- Steps to reproduce

**Contact:** Project owner or team lead

## ✅ Recently Fixed

- ✅ Indentation error in ops_agent.py (Jan 2, 2026)
- ✅ Database session management in strat_agent.py (Jan 2, 2026)
- ✅ Missing ShipmentTracking import (Jan 2, 2026)

---

**Last Updated:** January 2, 2026

**Note:** This is a living document. Update as issues are discovered or resolved.
