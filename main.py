import os
import vertexai
from vertexai.generative_models import GenerativeModel
from agents.ops_agent import InventoryOpsAgent
from agents.strat_agent import StrategyAgent
from agents.market_agent import MarketAgent

# 1. Configuration - Use environment variables or defaults
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

if not PROJECT_ID:
    print("⚠️ Warning: GOOGLE_CLOUD_PROJECT not set. Using default 'inventory-agent-x' for testing.")
    PROJECT_ID = "inventory-agent-x"

# --- ORCHESTRATOR CLASS ---

class SupplyChainGuardian:
    """Main orchestrator that routes queries to specialized agents."""
    
    def __init__(self, project=PROJECT_ID, location=LOCATION):
        self.project = project
        self.location = location
        
        try:
            vertexai.init(project=project, location=location)
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Vertex AI: {e}")
        
        # Initialize Sub-Agents
        self.ops_agent = InventoryOpsAgent(project, location)
        self.strategy_agent = StrategyAgent(project, location)
        self.market_agent = MarketAgent(project, location)
        
        # Initialize router model
        try:
            self.router = GenerativeModel(
                "gemini-2.0-flash-exp",
                system_instruction="""You are a routing agent for a supply chain management system.

You have access to three specialized agents:
1. **Ops Agent**: Handles inventory status, stock alerts, warehouse locations, weather risks
2. **Strategy Agent**: Predicts delays, provides reorder recommendations, assesses supply chain health
3. **Market Agent**: Analyzes market trends, monitors global events, suggests new products

Your job: Determine which agent should handle each query and route it appropriately.

Response format:
- For ops queries: "OPS: [query]"
- For strategy queries: "STRATEGY: [query]"
- For market queries: "MARKET: [query]"
- For multi-agent queries: Route to most relevant primary agent

Examples:
- "What's the stock of CHIP-X?" → OPS
- "Predict delays for incoming shipments" → STRATEGY
- "What products should we add?" → MARKET
- "Weather risk in Mumbai?" → OPS
- "Supply chain resilience?" → STRATEGY"""
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize router model: {e}")
            self.router = None
        
    def query(self, input: str) -> str:
        """Orchestrates the query between agents with intelligent routing."""
        print(f"🤖 Guardian received: {input}")
        
        # Use Gemini to route, or fallback to keyword-based routing
        if self.router:
            try:
                routing_response = self.router.generate_content(
                    f"Route this query: {input}"
                ).text.strip()
                
                if "OPS:" in routing_response.upper():
                    print("👉 Routing to Ops Agent...")
                    return self.ops_agent.query(input)
                elif "STRATEGY:" in routing_response.upper() or "STRAT:" in routing_response.upper():
                    print("👉 Routing to Strategy Agent...")
                    return self.strategy_agent.query(input)
                elif "MARKET:" in routing_response.upper():
                    print("👉 Routing to Market Agent...")
                    return self.market_agent.query(input)
            except Exception as e:
                print(f"⚠️ Router error: {e}. Using fallback routing.")
        
        # Fallback: Keyword-based routing
        input_lower = input.lower()
        
        # Ops Agent keywords
        if any(word in input_lower for word in ["stock", "inventory", "warehouse", "alert", "weather"]):
            print("👉 Delegating to Ops Agent...")
            return self.ops_agent.query(input)
        
        # Strategy Agent keywords
        elif any(word in input_lower for word in ["delay", "predict", "reorder", "recommend", "resilience", "health"]):
            print("👉 Delegating to Strategy Agent...")
            return self.strategy_agent.query(input)
        
        # Market Agent keywords
        elif any(word in input_lower for word in ["trend", "market", "suggest", "product", "news", "event", "competition"]):
            print("👉 Delegating to Market Agent...")
            return self.market_agent.query(input)
        
        # Default: Use ops agent
        else:
            print("👉 Delegating to Ops Agent (default)...")
            return self.ops_agent.query(input)

# Helper for Reasoning Engine creation
def get_supply_chain_guardian():
    return SupplyChainGuardian()

# 2. LOCAL TESTING BLOCK
if __name__ == "__main__":
    print("🛰️ Starting local Guardian test...")
    print("="*60)
    
    # Initialize database if needed
    try:
        from setup_database import setup_database
        from database import get_db_manager
        
        db = get_db_manager()
        # Check if database is initialized
        try:
            products = db.get_all_products()
            if not products:
                print("\n📦 Database is empty. Initializing...")
                setup_database()
        except:
            print("\n📦 Initializing database...")
            setup_database()
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
    
    print("\n" + "="*60)
    agent = get_supply_chain_guardian()
    
    # Test queries
    print("\n--- Test 1: Inventory Status ---")
    response1 = agent.query(input="What is our current stock status?")
    print(f"🛡️ Response: {response1}\n")
    
    print("\n--- Test 2: Delay Prediction ---")
    response2 = agent.query(input="Are there any expected delays in shipments?")
    print(f"🛡️ Response: {response2}\n")
    
    print("\n--- Test 3: Market Trends ---")
    response3 = agent.query(input="What products should we consider adding?")
    print(f"🛡️ Response: {response3}\n")
    
    print("\n--- Test 4: Weather Risk ---")
    response4 = agent.query(input="What's the weather risk in Mumbai?")
    print(f"🛡️ Response: {response4}\n")
    
    print("\n✅ All tests complete!")

    
    print("\n--- Test 2: General ---")
    response2 = agent.query(input="Who are you?")
    print(f"🛡️ Response: {response2}")