import os
import vertexai
from vertexai.preview.reasoning_engines import templates
from agents.ops_agent import InventoryOpsAgent

# 1. Configuration - Use environment variables or defaults
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

if not PROJECT_ID:
    # Fallback for local testing if not set, but warn
    print("⚠️ Warning: GOOGLE_CLOUD_PROJECT not set. Using default 'inventory-agent-x' for testing.")
    PROJECT_ID = "inventory-agent-x"

def get_supply_chain_guardian():
    """Initializer for Vertex AI Reasoning Engine."""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # Initialize Person 2's Agent
    ops_agent_instance = InventoryOpsAgent(
        project=PROJECT_ID,
        location=LOCATION
    ).get_agent()

    # The Master Orchestrator (Person 4's logic)
    guardian = templates.LlmAgent(
        model="gemini-1.5-pro",
        system_instruction="""
        You are the 'Supply Chain Guardian' Orchestrator. 
        You manage a team of specialized agents:
        - Use the 'InventoryOpsAgent' for any queries regarding stock levels, warehouse locations, or immediate weather risks.
        - If you don't have the Strat Agent yet, answer strategic questions to the best of your ability using your general knowledge.
        
        Always be professional, concise, and proactive in identifying risks.
        """,
        tools=[ops_agent_instance] 
    )
    return guardian

# 2. LOCAL TESTING BLOCK
# This only runs when you type 'python main.py' in your terminal
if __name__ == "__main__":
    print("🛰️ Starting local Guardian test...")
    agent = get_supply_chain_guardian()
    
    # Simple test query
    response = agent.query(input="What is our current stock status?")
    print(f"\n🛡️ Guardian Response: {response}")