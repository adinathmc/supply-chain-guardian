import vertexai
from vertexai.preview.reasoning_engines import templates
from agents.ops_agent import InventoryOpsAgent
# from agents.strat_agent import StrategicAgent # Person 3 will provide this

def get_supply_chain_guardian():
    # 1. Person 2's Agent becomes a "Tool" for your main Agent
    ops_agent_instance = InventoryOpsAgent(
        project="inventory-agent-x",
        location="us-central1"
    ).get_agent()

    # 2. The Master Orchestrator (Person 4's logic)
    guardian = templates.LlmAgent(
        model="gemini-1.5-pro",
        system_instruction="""
        You are the Supply Chain Guardian. 
        You have an Ops Agent to check inventory and a Strat Agent for trends.
        If a user asks about stock, delegate to the Ops Agent.
        """,
        tools=[ops_agent_instance] # This is Agent-to-Agent (A2A) orchestration
    )
    return guardian