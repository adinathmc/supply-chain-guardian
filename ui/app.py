import streamlit as st
import time
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Supply Chain Guardian",
    page_icon="🛡️",
    layout="wide"
)

# --- MOCK DATA FOR SIDEBAR ---
# Person 1 will eventually replace this with real AlloyDB data
mock_inventory = {
    "Product": ["CHIP-X", "SENS-9", "LOGIC-A", "PWR-MOD"],
    "Stock": [15, 82, 44, 9],
    "Status": ["⚠️ Low", "✅ OK", "✅ OK", "🚨 Critical"]
}
df_inventory = pd.DataFrame(mock_inventory)

# --- SIDEBAR: MONITORING & CONFIG ---
with st.sidebar:
    st.title("🛡️ Guardian Ops")
    st.markdown("---")
    
    # Status Indicators
    st.subheader("System Status")
    st.success("🟢 Orchestrator: Online")
    st.success("🟢 Ops Agent: Connected")
    st.warning("🟡 Strat Agent: Syncing...")
    
    st.markdown("---")
    
    # Real-time Stats Table
    st.subheader("Live Inventory")
    st.table(df_inventory.set_index("Product"))
    
    st.markdown("---")
    
    # Configuration (For you to paste the ID after deploy.py)
    st.subheader("Deployment Settings")
    agent_id = st.text_input(
        "Agent Resource Name", 
        placeholder="projects/123.../reasoningEngines/456",
        help="Paste the ID from your deploy.py output here."
    )

# --- MAIN CHAT INTERFACE ---
st.title("Supply Chain Guardian AI")
st.caption("Monitoring global risks and inventory health in real-time.")

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
                    # THE REAL CONNECTION POINT
                    from vertexai.preview import reasoning_engines
                    remote_agent = reasoning_engines.ReasoningEngine(agent_id)
                    full_response = remote_agent.query(input=prompt)
                    # full_response = f"Simulating connection to deployed agent: {agent_id}..." 
                except Exception as e:
                    full_response = f"❌ Error connecting to agent: {str(e)}"

            message_placeholder.markdown(full_response)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})