"""Market Intelligence Agent - Analyzes trends and suggests new products."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from external_services import get_news_service
from database import get_db_manager
import json
from datetime import datetime

# --- TOOL FUNCTIONS ---

def analyze_market_trends(category: str = "electronics") -> str:
    """Analyzes current market trends for a product category.
    
    Args:
        category: Product category to analyze (e.g., electronics, sensors)
    
    Returns:
        JSON string with trending products and growth metrics
    """
    news_service = get_news_service()
    trends = news_service.get_product_trends(category)
    
    return json.dumps({
        "category": category,
        "trending_products": trends,
        "analyzed_at": datetime.utcnow().isoformat()
    })

def get_supply_chain_events() -> str:
    """Fetches recent global supply chain events and disruptions.
    
    Returns:
        JSON string with news about supply chain disruptions, strikes, etc.
    """
    news_service = get_news_service()
    news = news_service.get_supply_chain_news()
    
    # Analyze severity of events
    events = []
    for article in news:
        severity = "Low"
        if any(word in article['title'].lower() for word in ['cyclone', 'hurricane', 'strike', 'shutdown']):
            severity = "High"
        elif any(word in article['title'].lower() for word in ['delay', 'warning', 'congestion']):
            severity = "Medium"
        
        events.append({
            "title": article['title'],
            "description": article['description'],
            "source": article['source'],
            "severity": severity,
            "published_at": article['published_at']
        })
    
    return json.dumps(events)

def suggest_new_products() -> str:
    """Suggests new products to add based on market trends and demand.
    
    Returns:
        JSON string with product suggestions and reasoning
    """
    news_service = get_news_service()
    db = get_db_manager()
    
    # Get current product categories
    existing_products = db.get_all_products()
    existing_categories = set([p.category for p in existing_products])
    
    # Get trends
    trends = news_service.get_product_trends("electronics")
    
    suggestions = []
    for trend in trends:
        # Check if we already stock similar products
        is_new = True
        for product in existing_products:
            if any(word in product.name.lower() for word in trend['product'].lower().split()):
                is_new = False
                break
        
        if is_new or trend['trend_score'] > 85:
            suggestions.append({
                "product_name": trend['product'],
                "category": "Electronics",
                "trend_score": trend['trend_score'],
                "growth_rate": trend.get('growth_rate', 'N/A'),
                "reasoning": trend.get('reasoning', ''),
                "recommendation": "Add to inventory" if is_new else "Increase stock",
                "priority": "High" if trend['trend_score'] > 90 else "Medium"
            })
    
    return json.dumps(suggestions)

def assess_competitor_risk(product_category: str = "electronics") -> str:
    """Assesses market competition and supply risks.
    
    Args:
        product_category: Category to assess
    
    Returns:
        JSON string with competitive landscape analysis
    """
    # In production, this would integrate with market research APIs
    return json.dumps({
        "category": product_category,
        "market_competition": "High",
        "supply_availability": "Medium",
        "price_trend": "Stable",
        "key_competitors": ["TechCorp", "GlobalElectronics", "FutureTech"],
        "risks": [
            "Increasing competition in IoT sensor market",
            "Supply constraints for advanced chips",
            "Price pressure from low-cost manufacturers"
        ],
        "opportunities": [
            "Growing demand for AI-enabled devices",
            "Expansion in renewable energy sector",
            "Smart city infrastructure projects"
        ]
    })

# --- AGENT DEFINITION ---

class MarketAgent:
    """Agent responsible for market intelligence, trend analysis, and product suggestions."""
    
    def __init__(self, project: str, location: str):
        self.project = project
        self.location = location
        
        # Define tools
        self.tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="analyze_market_trends",
                        description="Analyze current market trends for a product category",
                        parameters={
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "Product category (e.g., electronics, sensors)"
                                }
                            }
                        }
                    ),
                    FunctionDeclaration(
                        name="get_supply_chain_events",
                        description="Fetch recent global supply chain disruptions and events",
                        parameters={"type": "object", "properties": {}}
                    ),
                    FunctionDeclaration(
                        name="suggest_new_products",
                        description="Suggest new products to add based on market trends",
                        parameters={"type": "object", "properties": {}}
                    ),
                    FunctionDeclaration(
                        name="assess_competitor_risk",
                        description="Assess market competition and supply risks",
                        parameters={
                            "type": "object",
                            "properties": {
                                "product_category": {
                                    "type": "string",
                                    "description": "Category to assess"
                                }
                            }
                        }
                    )
                ]
            )
        ]
        
        # Initialize Gemini model
        try:
            self.model = GenerativeModel(
                "gemini-2.0-flash-exp",
                tools=self.tools,
                system_instruction="""You are a Market Intelligence Agent in a supply chain system.

Your responsibilities:
- Analyze market trends and identify emerging opportunities
- Monitor global supply chain events and disruptions
- Suggest new products based on demand patterns
- Assess competitive landscape and risks

Use provided tools to gather external intelligence. Provide data-driven recommendations with clear reasoning."""
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Gemini model: {e}")
            self.model = None
    
    def query(self, input: str) -> str:
        """Process a market intelligence query."""
        
        if not self.model:
            return self._simple_query(input)
        
        try:
            chat = self.model.start_chat()
            response = chat.send_message(input)
            
            # Handle function calls
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                if hasattr(part, 'function_call'):
                    fn_call = part.function_call
                    fn_name = fn_call.name
                    fn_args = dict(fn_call.args)
                    
                    # Execute function
                    if fn_name == "analyze_market_trends":
                        result = analyze_market_trends(fn_args.get("category", "electronics"))
                    elif fn_name == "get_supply_chain_events":
                        result = get_supply_chain_events()
                    elif fn_name == "suggest_new_products":
                        result = suggest_new_products()
                    elif fn_name == "assess_competitor_risk":
                        result = assess_competitor_risk(fn_args.get("product_category", "electronics"))
                    else:
                        result = json.dumps({"error": f"Unknown function: {fn_name}"})
                    
                    # Send result back
                    response = chat.send_message(
                        {
                            "function_response": {
                                "name": fn_name,
                                "response": {"result": result}
                            }
                        }
                    )
                else:
                    return response.text
            
            return response.text
            
        except Exception as e:
            print(f"⚠️ Gemini error: {e}. Falling back.")
            return self._simple_query(input)
    
    def _simple_query(self, input: str) -> str:
        """Fallback logic."""
        input_lower = input.lower()
        
        if "trend" in input_lower or "market" in input_lower:
            data = json.loads(analyze_market_trends())
            trends = data['trending_products']
            summary = "\n".join([
                f"• {t['product']}: Score {t['trend_score']} ({t.get('growth_rate', 'N/A')})"
                for t in trends[:5]
            ])
            return f"📈 Market Trends:\n{summary}"
        
        if "news" in input_lower or "event" in input_lower or "disruption" in input_lower:
            data = json.loads(get_supply_chain_events())
            summary = "\n".join([
                f"• [{e['severity']}] {e['title']}"
                for e in data[:5]
            ])
            return f"🌍 Supply Chain Events:\n{summary}"
        
        if "suggest" in input_lower or "new product" in input_lower:
            data = json.loads(suggest_new_products())
            if not data:
                return "✅ Current portfolio looks good"
            summary = "\n".join([
                f"• {s['product_name']}: Score {s['trend_score']} - {s['recommendation']}"
                for s in data[:5]
            ])
            return f"💡 Product Suggestions:\n{summary}"
        
        return "Market Agent: I can help analyze trends, monitor supply chain events, and suggest new products."
