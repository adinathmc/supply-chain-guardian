"""Initialize database with sample data for Supply Chain Guardian."""
from database import DatabaseManager, Product, ShipmentTracking
from datetime import datetime, timedelta
import os

def setup_database():
    """Create tables and populate with sample data."""
    
    print("🔧 Initializing Supply Chain Guardian Database...")
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Create tables
    db.create_tables()
    
    # Sample products
    sample_products = [
        Product(
            id="CHIP-X",
            name="X-Series Microchip",
            category="Electronics",
            stock_level=15,
            reorder_threshold=20,
            unit_price=45.99,
            warehouse_location="California, USA",
            supplier_location="Mumbai, India",
            lead_time_days=14,
            status="Low"
        ),
        Product(
            id="SENS-9",
            name="IoT Sensor Module",
            category="Electronics",
            stock_level=82,
            reorder_threshold=30,
            unit_price=28.50,
            warehouse_location="Texas, USA",
            supplier_location="Ho Chi Minh City, Vietnam",
            lead_time_days=21,
            status="OK"
        ),
        Product(
            id="LOGIC-A",
            name="Logic Controller A",
            category="Electronics",
            stock_level=44,
            reorder_threshold=25,
            unit_price=112.00,
            warehouse_location="New York, USA",
            supplier_location="Shenzhen, China",
            lead_time_days=18,
            status="OK"
        ),
        Product(
            id="PWR-MOD",
            name="Power Module",
            category="Electronics",
            stock_level=9,
            reorder_threshold=15,
            unit_price=67.25,
            warehouse_location="Florida, USA",
            supplier_location="Kochi, India",
            lead_time_days=16,
            status="Critical"
        ),
        Product(
            id="DISPLAY-HD",
            name="HD Display Panel",
            category="Display",
            stock_level=55,
            reorder_threshold=20,
            unit_price=89.99,
            warehouse_location="California, USA",
            supplier_location="Seoul, South Korea",
            lead_time_days=12,
            status="OK"
        ),
    ]
    
    # Sample shipments
    today = datetime.utcnow()
    sample_shipments = [
        ShipmentTracking(
            product_id="CHIP-X",
            quantity=50,
            origin="Mumbai, India",
            destination="California, USA",
            expected_date=today + timedelta(days=5),
            status="in_transit",
            delay_days=0
        ),
        ShipmentTracking(
            product_id="PWR-MOD",
            quantity=30,
            origin="Kochi, India",
            destination="Florida, USA",
            expected_date=today + timedelta(days=3),
            status="delayed",
            delay_days=2,
            delay_reason="Cyclone warning in Arabian Sea affecting port operations"
        ),
        ShipmentTracking(
            product_id="SENS-9",
            quantity=100,
            origin="Ho Chi Minh City, Vietnam",
            destination="Texas, USA",
            expected_date=today + timedelta(days=12),
            status="in_transit",
            delay_days=0
        ),
    ]
    
    # Insert data
    with db.get_session() as session:
        # Add products
        for product in sample_products:
            existing = session.query(Product).filter(Product.id == product.id).first()
            if not existing:
                session.add(product)
                print(f"✅ Added product: {product.id}")
        
        # Add shipments
        for shipment in sample_shipments:
            session.add(shipment)
            print(f"✅ Added shipment: {shipment.product_id}")
        
        session.commit()
    
    print("\n🎉 Database initialized successfully!")
    print(f"📦 Products: {len(sample_products)}")
    print(f"🚢 Shipments: {len(sample_shipments)}")
    print(f"\n💾 Database: {db.connection_string}")

if __name__ == "__main__":
    setup_database()
