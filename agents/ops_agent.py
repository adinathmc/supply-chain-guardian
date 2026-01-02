"""Inventory Operations Agent - Handles real-time inventory tracking and alerts."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration
from database import get_db_manager
from external_services import get_weather_service
from typing import Dict, Any
import json

# --- TOOL FUNCTIONS ---

def get_inventory_status(product_id: str) -> str:
    """Retrieves the current stock status and warehouse location for a product.
    
    Args:
        product_id: The product identifier (e.g., CHIP-X, SENS-9)
    
    Returns:
        JSON string with product details including stock, location, and status
    """
    db = get_db_manager()
    product = db.get_product(product_id.upper())
    
    if not product:
        return json.dumps({"error": f"Product {product_id} not found"})
    
    return json.dumps({
        "product_id": product.id,
        "name": product.name,
        "stock_level": product.stock_level,
        "status": product.status,
        "warehouse_location": product.warehouse_location,
        "reorder_threshold": product.reorder_threshold,
        "supplier_location": product.supplier_location,
        "lead_time_days": product.lead_time_days,
        "last_updated": product.last_updated.isoformat() if product.last_updated else None
    })

def get_all_inventory() -> str:
    """Retrieves status of all products in inventory.
    
    Returns:
        JSON string with list of all products and their status
    """
    db = get_db_manager()
    products = db.get_all_products()
    
    return json.dumps([
        {
            "product_id": p.id,
            "name": p.name,
            "stock_level": p.stock_level,
            "status": p.status,
            "warehouse_location": p.warehouse_location
        }
        for p in products
    ])

def check_weather_risk(location: str) -> str:
    """Checks for weather-related logistics risks at a specific location.
    
    Args:
        location: City or region name (e.g., Mumbai, Florida)
    
    Returns:
        JSON string with risk assessment including severity and delay estimates
    """
    weather_service = get_weather_service()
    risk_assessment = weather_service.assess_logistics_risk(location)
    return json.dumps(risk_assessment)

def get_active_alerts() -> str:
    """Retrieves all active/unresolved stock alerts.
    
    Returns:
        JSON string with list of active alerts
    """
    db = get_db_manager()
    alerts = db.get_active_alerts()
    
    return json.dumps([
        {
            "id": alert.id,
            "product_id": alert.product_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "created_at": alert.created_at.isoformat()
        }
        for alert in alerts
    ])

def update_stock_level(product_id: str, new_stock: int) -> str:
    """Updates the stock level for a product.
    
    Args:
        product_id: The product identifier
        new_stock: The new stock level
    
    Returns:
        JSON string with update confirmation
    """
    db = get_db_manager()
    success = db.update_stock(product_id.upper(), new_stock)
    
    if success:
        return json.dumps({"success": True, "message": f"Stock updated for {product_id}"})
    else:
        return json.dumps({"success": False, "message": f"Product {product_id} not found"})

# --- AGENT DEFINITION ---

class InventoryOpsAgent:
    """Agent responsible for inventory monitoring, stock alerts, and operational queries."""
    
    def __init__(self, project: str, location: str):
        self.project = project
        self.location = location
        
        # Define tools for Gemini function calling
        self.tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration(
                        name="get_inventory_status",
                        description="Get current stock status and details for a specific product",
                        parameters={
                            "type": "object",
                            "properties": {
                                "product_id": {
                                    "type": "string",
                                    "description": "Product identifier (e.g., CHIP-X, SENS-9)"
                                }
                            },
                            "required": ["product_id"]
                        }
                    ),
                    FunctionDeclaration(
                        name="get_all_inventory",
                        description="Get status of all products in inventory",
                        parameters={"type": "object", "properties": {}}
                    ),
                    FunctionDeclaration(
                        name="check_weather_risk",
                        description="Check weather-related logistics risks for a location",
                        parameters={
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City or region name"
                                }
                            },
                            "required": ["location"]
                        }
                    ),
                    FunctionDeclaration(
                        name="get_active_alerts",
                        description="Get all active stock alerts",
                        parameters={"type": "object", "properties": {}}
                    ),
                    FunctionDeclaration(
                        name="update_stock_level",
                        description="Update stock level for a product",
                        parameters={
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product ID"},
                                "new_stock": {"type": "integer", "description": "New stock quantity"}
                            },
                            "required": ["product_id", "new_stock"]
                        }
                    )
                ]
            )
        ]
        
        # Initialize Gemini model with tools
        try:
            self.model = GenerativeModel(
                "gemini-2.0-flash-exp",
                tools=self.tools,
                system_instruction="""You are an Inventory Operations Agent in a supply chain management system.

Your responsibilities:
- Monitor stock levels and alert on low/critical inventory
- Check weather conditions affecting logistics
- Provide real-time inventory status
- Answer operational queries about products and warehouses

Always use the provided tools to fetch real data. Be concise and actionable in your responses."""
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Gemini model: {e}")
            self.model = None
    
    def query(self, input: str) -> str:
        """Process a query using Gemini with function calling or fallback logic."""
        
        # If Gemini is not available, use simple routing
        if not self.model:
            return self._simple_query(input)
        
        try:
            # Use Gemini with function calling
            chat = self.model.start_chat()
            response = chat.send_message(input)
            
            # Handle function calls
            tool_calls = {}
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                if hasattr(part, 'function_call'):
                    fn_call = part.function_call
                    fn_name = fn_call.name
                    fn_args = dict(fn_call.args)
                    
                    # Execute the function
                    if fn_name == "get_inventory_status":
                        result = get_inventory_status(fn_args.get("product_id", ""))
                    elif fn_name == "get_all_inventory":
                        result = get_all_inventory()
                    elif fn_name == "check_weather_risk":
                        result = check_weather_risk(fn_args.get("location", ""))
                    elif fn_name == "get_active_alerts":
                        result = get_active_alerts()
                    elif fn_name == "update_stock_level":
                        result = update_stock_level(
                            fn_args.get("product_id", ""),
                            fn_args.get("new_stock", 0)
                        )
                    else:
                        result = json.dumps({"error": f"Unknown function: {fn_name}"})
                    
                    # Send function response back
                    response = chat.send_message(
                        {
                            "function_response": {
                                "name": fn_name,
                                "response": {"result": result}
                            }
                        }
                    )
                else:
                    # Got final text response
                    return response.text
            
            return response.text
            
        except Exception as e:
            print(f"⚠️ Gemini error: {e}. Falling back to simple routing.")
            return self._simple_query(input)
    
    def _simple_query(self, input: str) -> str:
        """Fallback: Simple keyword-based routing when Gemini is unavailable."""
        input_lower = input.lower()
        
        if "all" in input_lower and ("inventory" in input_lower or "stock" in input_lower):
            data = json.loads(get_all_inventory())
            summary = "\n".join([
                f"• {p['product_id']}: {p['stock_level']} units - {p['status']}"
                for p in data
            ])
            return f"📦 Current Inventory:\n{summary}"
        
        # Check for specific product IDs
        product_ids = ["CHIP-X", "SENS-9", "LOGIC-A", "PWR-MOD", "DISPLAY-HD"]
        for pid in product_ids:
            if pid.lower() in input_lower:
                data = json.loads(get_inventory_status(pid))
                if "error" not in data:
                    return f"📦 {data['name']} ({data['product_id']}):\n" \
                           f"  Stock: {data['stock_level']} units\n" \
                           f"  Status: {data['status']}\n" \
                           f"  Location: {data['warehouse_location']}"
        
        if "alert" in input_lower:
            data = json.loads(get_active_alerts())
            if not data:
                return "✅ No active alerts"
            summary = "\n".join([
                f"• [{a['severity']}] {a['product_id']}: {a['message']}"
                for a in data
            ])
            return f"🚨 Active Alerts:\n{summary}"
        
        if "weather" in input_lower:
            # Try to extract location
            locations = ["Mumbai", "Kochi", "Florida", "California", "Texas", "Vietnam"]
            for loc in locations:
                if loc.lower() in input_lower:
                    data = json.loads(check_weather_risk(loc))
                    return f"🌤️ Weather Risk for {loc}:\n" \
                           f"  Risk Level: {data['risk_level']}\n" \
                           f"  Delay Estimate: {data['delay_estimate_days']} days\n" \
                           f"  Factors: {', '.join(data.get('risk_factors', ['None']))}"
        
        return f"Ops Agent: I can help with inventory status, stock alerts, and weather risks. " \
               f"Try asking about specific products or locations."
