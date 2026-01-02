"""Strategy Agent - Predicts delays and provides strategic recommendations."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from database import get_db_manager, ShipmentTracking
from external_services import get_weather_service
import json
from datetime import datetime, timedelta

# --- TOOL FUNCTIONS ---

def predict_shipment_delays(product_id: str = None) -> str:
    """Predicts potential delays for shipments based on weather and external factors.
    
    Args:
        product_id: Optional product ID to check specific shipment delays
    
    Returns:
        JSON string with delay predictions and risk analysis
    """
    db = get_db_manager()
    weather_service = get_weather_service()
    
    # Get active shipments and extract data within session
    with db.get_session() as session:
        if product_id:
            shipments_query = session.query(ShipmentTracking).filter(
                ShipmentTracking.status == "in_transit",
                ShipmentTracking.product_id == product_id.upper()
            ).all()
        else:
            shipments_query = session.query(ShipmentTracking).filter(
                ShipmentTracking.status == "in_transit"
            ).all()
        
        # Extract all data while session is active
        shipments_data = [
            {
                "product_id": s.product_id,
                "origin": s.origin,
                "destination": s.destination,
                "expected_date": s.expected_date.isoformat()
            }
            for s in shipments_query
        ]
    
    predictions = []
    
    for shipment_data in shipments_data:
        # Check weather risk at origin and destination
        origin_risk = weather_service.assess_logistics_risk(shipment_data["origin"])
        dest_risk = weather_service.assess_logistics_risk(shipment_data["destination"])
        
        max_risk = origin_risk if origin_risk['delay_estimate_days'] > dest_risk['delay_estimate_days'] else dest_risk
        
        predictions.append({
            "product_id": shipment_data["product_id"],
            "origin": shipment_data["origin"],
            "destination": shipment_data["destination"],
            "expected_date": shipment_data["expected_date"],
            "predicted_delay_days": max_risk['delay_estimate_days'],
            "risk_level": max_risk['risk_level'],
            "risk_factors": max_risk['risk_factors'],
            "confidence": 0.85 if max_risk['risk_level'] == "High" else 0.7
        })
    
    return json.dumps(predictions)

def calculate_reorder_recommendations() -> str:
    """Analyzes inventory and predicts which products need reordering.
    
    Returns:
        JSON string with reorder recommendations based on stock levels and lead times
    """
    db = get_db_manager()
    products = db.get_all_products()
    weather_service = get_weather_service()
    
    recommendations = []
    
    for product in products:
        # Calculate if reorder is needed
        days_until_stockout = max(0, (product.stock_level - 5) // 2)  # Simplified consumption rate
        
        # Check weather impact on lead time
        supplier_risk = weather_service.assess_logistics_risk(product.supplier_location)
        adjusted_lead_time = product.lead_time_days + supplier_risk['delay_estimate_days']
        
        urgency = "Low"
        reorder_now = False
        
        if days_until_stockout < adjusted_lead_time:
            urgency = "High"
            reorder_now = True
        elif days_until_stockout < adjusted_lead_time + 7:
            urgency = "Medium"
            reorder_now = True
        
        if reorder_now or product.stock_level <= product.reorder_threshold:
            recommendations.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock_level,
                "reorder_threshold": product.reorder_threshold,
                "normal_lead_time": product.lead_time_days,
                "adjusted_lead_time": adjusted_lead_time,
                "days_until_stockout": days_until_stockout,
                "urgency": urgency,
                "recommended_quantity": max(50, product.reorder_threshold * 2),
                "reasoning": f"Stock below threshold. Weather risk adds {supplier_risk['delay_estimate_days']} days to delivery."
            })
    
    return json.dumps(recommendations)

def assess_supply_chain_resilience() -> str:
    """Provides overall supply chain health and resilience score.
    
    Returns:
        JSON string with resilience metrics and vulnerability analysis
    """
    db = get_db_manager()
    weather_service = get_weather_service()
    
    products = db.get_all_products()
    alerts = db.get_active_alerts()
    
    # Calculate metrics
    total_products = len(products)
    critical_products = len([p for p in products if p.status == "Critical"])
    low_products = len([p for p in products if p.status == "Low"])
    ok_products = len([p for p in products if p.status == "OK"])
    
    # Check supplier location risks
    supplier_locations = list(set([p.supplier_location for p in products]))
    high_risk_locations = []
    
    for location in supplier_locations:
        risk = weather_service.assess_logistics_risk(location)
        if risk['risk_level'] in ["High", "Medium"]:
            high_risk_locations.append({
                "location": location,
                "risk_level": risk['risk_level'],
                "factors": risk['risk_factors']
            })
    
    # Calculate resilience score (0-100)
    resilience_score = 100
    resilience_score -= critical_products * 15
    resilience_score -= low_products * 5
    resilience_score -= len(high_risk_locations) * 10
    resilience_score -= len(alerts) * 5
    resilience_score = max(0, min(100, resilience_score))
    
    health_status = "Excellent" if resilience_score >= 80 else \
                    "Good" if resilience_score >= 60 else \
                    "Fair" if resilience_score >= 40 else "At Risk"
    
    return json.dumps({
        "resilience_score": resilience_score,
        "health_status": health_status,
        "inventory_breakdown": {
            "total": total_products,
            "critical": critical_products,
            "low": low_products,
            "ok": ok_products
        },
        "active_alerts": len(alerts),
        "high_risk_locations": high_risk_locations,
        "assessed_at": datetime.utcnow().isoformat()
    })

# --- AGENT DEFINITION ---

class StrategyAgent:
    """Agent responsible for strategic planning, delay prediction, and supply chain optimization."""
    
    def __init__(self, project: str, location: str):
        self.project = project
        self.location = location
        
        # Define tools for Gemini
        self.tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="predict_shipment_delays",
                        description="Predict potential delays for shipments based on weather and external factors",
                        parameters={
                            "type": "object",
                            "properties": {
                                "product_id": {
                                    "type": "string",
                                    "description": "Optional: specific product ID to check delays for"
                                }
                            }
                        }
                    ),
                    FunctionDeclaration(
                        name="calculate_reorder_recommendations",
                        description="Analyze inventory and provide reorder recommendations considering lead times and weather",
                        parameters={"type": "object", "properties": {}}
                    ),
                    FunctionDeclaration(
                        name="assess_supply_chain_resilience",
                        description="Provide overall supply chain health score and vulnerability analysis",
                        parameters={"type": "object", "properties": {}}
                    )
                ]
            )
        ]
        
        # Initialize Gemini model
        try:
            self.model = GenerativeModel(
                "gemini-2.0-flash-exp",
                tools=self.tools,
                system_instruction="""You are a Strategy Agent in a supply chain management system.

Your responsibilities:
- Predict delivery delays using weather data and external factors
- Provide reordering recommendations based on consumption patterns and lead times
- Assess supply chain resilience and identify vulnerabilities
- Offer strategic insights for risk mitigation

Always use provided tools to analyze real data. Focus on actionable recommendations and quantified risk assessments."""
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Gemini model: {e}")
            self.model = None
    
    def query(self, input: str) -> str:
        """Process a strategic query using Gemini with function calling."""
        
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
                    if fn_name == "predict_shipment_delays":
                        result = predict_shipment_delays(fn_args.get("product_id"))
                    elif fn_name == "calculate_reorder_recommendations":
                        result = calculate_reorder_recommendations()
                    elif fn_name == "assess_supply_chain_resilience":
                        result = assess_supply_chain_resilience()
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
        """Fallback logic when Gemini is unavailable."""
        input_lower = input.lower()
        
        if "delay" in input_lower or "shipment" in input_lower:
            data = json.loads(predict_shipment_delays())
            if not data:
                return "✅ No active shipments to track"
            summary = "\n".join([
                f"• {d['product_id']}: {d['predicted_delay_days']} day delay (Risk: {d['risk_level']})"
                for d in data[:5]
            ])
            return f"📊 Delay Predictions:\n{summary}"
        
        if "reorder" in input_lower or "recommend" in input_lower:
            data = json.loads(calculate_reorder_recommendations())
            if not data:
                return "✅ No immediate reorders needed"
            summary = "\n".join([
                f"• {d['product_id']}: Order {d['recommended_quantity']} units ({d['urgency']} priority)"
                for d in data[:5]
            ])
            return f"📦 Reorder Recommendations:\n{summary}"
        
        if "resilience" in input_lower or "health" in input_lower:
            data = json.loads(assess_supply_chain_resilience())
            return f"💪 Supply Chain Health: {data['health_status']} (Score: {data['resilience_score']}/100)\n" \
                   f"  Critical Products: {data['inventory_breakdown']['critical']}\n" \
                   f"  Active Alerts: {data['active_alerts']}\n" \
                   f"  High-Risk Locations: {len(data['high_risk_locations'])}"
        
        return "Strategy Agent: I can help predict delays, recommend reorders, and assess supply chain resilience."
