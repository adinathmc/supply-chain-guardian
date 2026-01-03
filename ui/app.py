"""Streamlit UI for Supply Chain Guardian - Enhanced Real-time Dashboard"""
import streamlit as st
import time
import pandas as pd
import sys
import os
import json
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_manager
from alerting import get_alerting_service
from external_services import get_weather_service

# Try to import deployed agent
try:
    from vertexai.preview import reasoning_engines
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# Try to import local agent
try:
    from main import get_supply_chain_guardian
    LOCAL_AGENT_AVAILABLE = True
except ImportError:
    LOCAL_AGENT_AVAILABLE = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Supply Chain Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    /* Force alert text to render in black for readability */
    .alert-high, .alert-medium {
        color: #000000;
    }
    /* Sidebar alert summary: make metric text white only inside sidebar */
    [data-testid="stSidebar"] [data-testid="stMetricLabel"],
    [data-testid="stSidebar"] [data-testid="stMetricValue"],
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }
    .alert-high {
        background-color: #ffebee;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #fff8e1;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #ff9800;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SERVICES ---
@st.cache_resource
def init_services():
    """Initialize database and services with timeout."""
    import threading
    
    result = {"db": None, "alerting": None, "weather": None, "error": None}
    
    def _init():
        try:
            result["db"] = get_db_manager()
            result["alerting"] = get_alerting_service()
            result["weather"] = get_weather_service()
        except Exception as e:
            result["error"] = str(e)
    
    # Run initialization in a thread with timeout
    thread = threading.Thread(target=_init, daemon=True)
    thread.start()
    thread.join(timeout=3)  # 3 second timeout
    
    if thread.is_alive():
        # Initialization timed out, return None gracefully
        return None, None, None
    
    if result["error"]:
        return None, None, None
    
    return result["db"], result["alerting"], result["weather"]

db, alerting, weather = init_services()

# --- SIDEBAR: MONITORING & CONFIG ---
with st.sidebar:
    st.title("🛡️ Guardian Control Center")
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    if db:
        st.success("🟢 Database: Connected")
    else:
        st.error("🔴 Database: Offline")
    
    if LOCAL_AGENT_AVAILABLE:
        st.success("🟢 Local Agent: Ready")
    else:
        st.warning("🟡 Local Agent: Not Available")
    
    st.markdown("---")
    
    # Real-time Stats
    if db and db.connection_established:
        st.subheader("Live Inventory")
        try:
            products = db.get_all_products()
            if products:
                df_inventory = pd.DataFrame([
                    {
                        "Product": p.id,
                        "Stock": p.stock_level,
                        "Status": "🚨" if p.status == "Critical" else "⚠️" if p.status == "Low" else "✅"
                    }
                    for p in products
                ])
                st.dataframe(df_inventory, use_container_width=True, hide_index=True)
            else:
                st.info("No products found in database")
        except Exception as e:
            st.warning(f"⚠️ Could not load inventory: {str(e)[:50]}...")
    elif db:
        st.subheader("Live Inventory")
        st.info("💾 Database not connected. Using API for queries.")
    else:
        st.subheader("Live Inventory")
        st.warning("⚠️ No database connection available")
    
    st.markdown("---")
    
    # Alert Summary
    if alerting:
        st.subheader("Alert Summary")
        try:
            summary = alerting.get_alert_summary()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total", summary['total_alerts'])
                st.metric("🔴 High", summary['high_severity'])
            with col2:
                st.metric("🟡 Medium", summary['medium_severity'])
                st.metric("🟢 Low", summary['low_severity'])
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
    
    st.markdown("---")
    
    # Deployment Config
    with st.expander("⚙️ Deployment Settings"):
        agent_resource_name = st.text_input(
            "Agent Resource Name",
            placeholder="projects/.../reasoningEngines/...",
            help="Paste the resource name from deploy.py output"
        )
        # Persist the latest agent resource name for chat usage
        if agent_resource_name:
            st.session_state["agent_resource_name"] = agent_resource_name.strip()
        if st.button("Connect to Deployed Agent"):
            if agent_resource_name and AGENT_AVAILABLE:
                try:
                    st.session_state['deployed_agent'] = reasoning_engines.ReasoningEngine(agent_resource_name)
                    st.success("✅ Connected to deployed agent!")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
            else:
                st.warning("Enter valid resource name")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

# --- MAIN INTERFACE ---
st.title("Supply Chain Guardian AI")
st.caption("Intelligent monitoring of global inventory, risks, and market trends")

# Latest agent id from sidebar (if provided)
agent_id = st.session_state.get("agent_resource_name")

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat", "📦 Inventory", "📊 Analytics", "🚨 Alerts", "🌍 External Risks"
])

# TAB 1: CHAT INTERFACE
with tab1:
    st.header("Ask Guardian AI")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about inventory, delays, trends..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Guardian is thinking..."):
                try:
                    # Prefer backend API if configured
                    backend_api = os.getenv("BACKEND_API_URL")
                    if backend_api:
                        try:
                            resp = requests.post(
                                backend_api.rstrip("/") + "/query",
                                json={"input": prompt},
                                timeout=30,
                            )
                            resp.raise_for_status()
                            response = resp.json().get("response", "")
                        except Exception as api_err:
                            response = f"⚠️ Backend API error: {api_err}"
                    # Try deployed agent directly
                    elif 'deployed_agent' in st.session_state:
                        response = st.session_state['deployed_agent'].query(input=prompt)
                    # Fallback to local agent
                    elif LOCAL_AGENT_AVAILABLE:
                        agent = get_supply_chain_guardian()
                        response = agent.query(prompt)
                    else:
                        response = "⚠️ No agent available. Please deploy or configure local agent."
                    
                    # Try to parse as JSON and display nicely
                    try:
                        response_json = json.loads(response)
                        # If it's a list of dicts, show as table and JSON
                        if isinstance(response_json, list) and response_json and isinstance(response_json[0], dict):
                            st.dataframe(response_json, use_container_width=True)
                        # Always show the structured JSON view too
                        st.json(response_json)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except (json.JSONDecodeError, ValueError):
                        # Not JSON, display as markdown
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")

# TAB 2: INVENTORY DASHBOARD
with tab2:
    st.header("📦 Inventory Dashboard")
    
    if db:
        try:
            products = db.get_all_products()
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Products", len(products))
            with col2:
                critical = len([p for p in products if p.status == "Critical"])
                st.metric("Critical Stock", critical, delta=None, delta_color="inverse")
            with col3:
                low = len([p for p in products if p.status == "Low"])
                st.metric("Low Stock", low, delta=None, delta_color="inverse")
            with col4:
                ok = len([p for p in products if p.status == "OK"])
                st.metric("Healthy Stock", ok)
            
            st.markdown("---")
            
            # Detailed table
            df = pd.DataFrame([
                {
                    "Product ID": p.id,
                    "Name": p.name,
                    "Stock": p.stock_level,
                    "Status": p.status,
                    "Warehouse": p.warehouse_location,
                    "Supplier": p.supplier_location,
                    "Lead Time": f"{p.lead_time_days} days"
                }
                for p in products
            ])
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Stock": st.column_config.NumberColumn(format="%d units"),
                    "Status": st.column_config.TextColumn()
                }
            )
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
    else:
        st.warning("Database not connected")

# TAB 3: ANALYTICS
with tab3:
    st.header("📊 Supply Chain Analytics")
    
    if db:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Stock Distribution")
            products = db.get_all_products()
            status_counts = {"Critical": 0, "Low": 0, "OK": 0}
            for p in products:
                if p.status in status_counts:
                    status_counts[p.status] += 1
            
            st.bar_chart(status_counts)
        
        with col2:
            st.subheader("Shipment Status")
            try:
                in_transit = len(db.get_shipments_by_status("in_transit"))
                delayed = len(db.get_shipments_by_status("delayed"))
                delivered = len(db.get_shipments_by_status("delivered"))
                
                shipment_data = {
                    "In Transit": in_transit,
                    "Delayed": delayed,
                    "Delivered": delivered
                }
                st.bar_chart(shipment_data)
            except:
                st.info("No shipment data available")

# TAB 4: ALERTS
with tab4:
    st.header("🚨 Active Alerts")
    
    if alerting:
        # Run alert check
        if st.button("🔍 Check for New Alerts"):
            with st.spinner("Scanning inventory..."):
                new_alerts = alerting.check_and_alert()
                if new_alerts:
                    st.success(f"Created {len(new_alerts)} new alerts")
                else:
                    st.info("No new critical conditions detected")
        
        st.markdown("---")
        
        # Display alerts
        summary = alerting.get_alert_summary()
        
        if summary['total_alerts'] > 0:
            # High priority
            if summary['high_severity'] > 0:
                st.subheader("🔴 High Priority")
                for alert in summary['alerts_by_severity']['High']:
                    st.markdown(f"""
                    <div class="alert-high">
                        <strong>{alert['product_id']}</strong> - {alert['alert_type']}<br>
                        {alert['message']}<br>
                        <small>{alert['created_at']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Medium priority
            if summary['medium_severity'] > 0:
                st.subheader("🟡 Medium Priority")
                for alert in summary['alerts_by_severity']['Medium']:
                    st.markdown(f"""
                    <div class="alert-medium">
                        <strong>{alert['product_id']}</strong> - {alert['alert_type']}<br>
                        {alert['message']}<br>
                        <small>{alert['created_at']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ No active alerts. Supply chain is healthy!")

# TAB 5: EXTERNAL RISKS
with tab5:
    st.header("🌍 External Risk Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weather Risks")
        if weather and db:
            try:
                products = db.get_all_products()
                locations = list(set([p.supplier_location for p in products]))
                
                for location in locations[:5]:  # Show top 5
                    risk = weather.assess_logistics_risk(location)
                    
                    severity_color = "🔴" if risk['risk_level'] == "High" else \
                                   "🟡" if risk['risk_level'] == "Medium" else "🟢"
                    
                    with st.expander(f"{severity_color} {location} - {risk['risk_level']} Risk"):
                        st.write(f"**Delay Estimate:** {risk['delay_estimate_days']} days")
                        st.write(f"**Current Weather:** {risk['current_weather']['description']}")
                        if risk['risk_factors']:
                            st.write("**Risk Factors:**")
                            for factor in risk['risk_factors']:
                                st.write(f"  • {factor}")
            except Exception as e:
                st.error(f"Error loading weather data: {e}")
    
    with col2:
        st.subheader("Supply Chain News")
        try:
            from external_services import get_news_service
            news_service = get_news_service()
            news = news_service.get_supply_chain_news()
            
            for article in news[:5]:
                severity = "🔴" if "High" in str(article) else "🟡" if "Medium" in str(article) else "🟢"
                st.markdown(f"""
                **{severity} {article['title']}**  
                {article.get('description', '')[:200]}...  
                *{article['source']}*
                """)
                st.markdown("---")
        except Exception as e:
            st.info("News feed unavailable in demo mode")

# --- FOOTER ---
st.markdown("---")
st.caption("Supply Chain Guardian v2.0 | Powered by Google Cloud Vertex AI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about stock levels or supplier risks..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- AGENT LOGIC ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Guardian is analyzing data..."):
            # If you haven't deployed yet, show a mock response
            if not agent_id:
                time.sleep(1) # Simulate thinking
                full_response = "🛡️ **Guardian Insight:** The system is in 'Local Mock Mode'. To get real answers, please deploy your agent and paste the Resource ID in the sidebar."
            else:
                try:
                    # THE REAL CONNECTION POINT
                    if agent_id:
                        from vertexai.preview import reasoning_engines
                        remote_agent = reasoning_engines.ReasoningEngine(agent_id)
                        full_response = remote_agent.query(input=prompt)
                    elif LOCAL_AGENT_AVAILABLE:
                        # Fallback to local (in-container) execution on Cloud Run
                        local_guardian = get_supply_chain_guardian()
                        full_response = local_guardian.query(input=prompt)
                    else:
                        full_response = "⚠️ No agent configured. Please set AGENT_RESOURCE_NAME or ensure code is deployed correctly."

                except Exception as e:
                    full_response = f"❌ Error connecting to agent: {str(e)}"

            message_placeholder.markdown(full_response)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})