"""Database models and connection management for Supply Chain Guardian."""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from contextlib import contextmanager
from google.cloud.alloydb.connector import Connector, IPTypes
import pg8000

Base = declarative_base()

# --- DATABASE MODELS ---

class Product(Base):
    """Inventory product model."""
    __tablename__ = 'products'
    
    id = Column(String(50), primary_key=True)  # e.g., CHIP-X
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    stock_level = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=10)
    unit_price = Column(Float)
    warehouse_location = Column(String(200))
    supplier_location = Column(String(200))  # Where it's shipped from
    lead_time_days = Column(Integer, default=7)  # Normal delivery time
    last_updated = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50))  # OK, Low, Critical

class StockAlert(Base):
    """Stock alert history."""
    __tablename__ = 'stock_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50))
    alert_type = Column(String(50))  # low_stock, critical_stock, delayed_shipment
    severity = Column(String(20))  # Low, Medium, High
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

class ShipmentTracking(Base):
    """Track incoming shipments."""
    __tablename__ = 'shipments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50))
    quantity = Column(Integer)
    origin = Column(String(200))
    destination = Column(String(200))
    expected_date = Column(DateTime)
    actual_date = Column(DateTime, nullable=True)
    status = Column(String(50))  # in_transit, delayed, delivered
    delay_days = Column(Integer, default=0)
    delay_reason = Column(Text, nullable=True)  # weather, port_strike, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherImpact(Base):
    """Track weather impacts on logistics."""
    __tablename__ = 'weather_impacts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(200))
    weather_type = Column(String(100))  # hurricane, storm, heat_wave
    severity = Column(String(20))  # Low, Medium, High
    impact_start = Column(DateTime)
    impact_end = Column(DateTime, nullable=True)
    affected_shipments = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductSuggestion(Base):
    """AI-generated product suggestions based on trends."""
    __tablename__ = 'product_suggestions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(200))
    category = Column(String(100))
    trend_score = Column(Float)  # 0-100
    reasoning = Column(Text)
    data_sources = Column(Text)  # JSON string of sources
    suggested_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)

# --- DATABASE CONNECTION MANAGER ---

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, connection_string: str = None):
        """Initialize database manager with connection string or AlloyDB config."""
        
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal = None
        self.connection_established = False
        
        # AlloyDB Configuration
        self.alloydb_project = os.getenv("ALLOYDB_PROJECT")
        self.alloydb_region = os.getenv("ALLOYDB_REGION")
        self.alloydb_cluster = os.getenv("ALLOYDB_CLUSTER")
        self.alloydb_instance = os.getenv("ALLOYDB_INSTANCE")
        self.db_name = os.getenv("DB_NAME", "postgres")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_pass = os.getenv("DB_PASS", "supplychain123") # Default for demo
        
        # In Cloud Run, always fallback to SQLite (database queries go through API)
        if os.getenv("K_SERVICE"):
            print(f"☁️ Running in Cloud Run - using SQLite, queries should go through BACKEND_API")
            self.connection_string = "sqlite:///supply_chain.db"
            self.engine = create_engine(self.connection_string, echo=False, connect_args={"timeout": 5})
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            self.connection_established = False
            # Initialize schema on first run
            Base.metadata.create_all(self.engine)
            return
        
        # Priority: 1. connection_string param, 2. DB_CONNECTION_STRING env, 3. AlloyDB, 4. SQLite
        try:
            if self.connection_string:
                # Explicit connection string provided
                print(f"🔌 Using provided connection string")
                self._create_engine_with_timeout(self.connection_string)
            elif os.getenv("DB_CONNECTION_STRING"):
                # Use environment variable connection string
                conn_str = os.getenv("DB_CONNECTION_STRING")
                self.connection_string = conn_str
                print(f"🔌 Using DB_CONNECTION_STRING from environment")
                self._create_engine_with_timeout(conn_str)
            elif self.alloydb_cluster and self.alloydb_instance:
                # Use AlloyDB with Connector
                print(f"🔌 Connecting to AlloyDB: {self.alloydb_cluster}")
                self.engine = self._init_alloydb_engine()
                self._test_connection()
            else:
                # Fallback to local SQLite
                print(f"🔌 Using local SQLite database")
                self.connection_string = "sqlite:///supply_chain.db"
                self._create_engine_with_timeout(self.connection_string)
            
            # Keep objects usable after session commit/close (Streamlit reads outside session)
            if self.engine:
                self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
                # Initialize schema
                Base.metadata.create_all(self.engine)
                
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            print(f"⚠️ Falling back to SQLite")
            self.connection_string = "sqlite:///supply_chain.db"
            self.engine = create_engine(self.connection_string, echo=False, connect_args={"timeout": 5})
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            # Initialize schema
            Base.metadata.create_all(self.engine)
            self.connection_established = False
    
    def _create_engine_with_timeout(self, conn_str: str):
        """Create engine with connection timeout."""
        try:
            # Add connection pool settings and timeout for PostgreSQL
            if "postgresql" in conn_str:
                self.engine = create_engine(
                    conn_str,
                    echo=False,
                    pool_pre_ping=True,  # Verify connections before using
                    connect_args={
                        "connect_timeout": 5,  # 5 second timeout for initial connection
                    }
                )
            else:
                # SQLite
                self.engine = create_engine(conn_str, echo=False, connect_args={"timeout": 5})
            
            # Test connection immediately with timeout
            self._test_connection()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    
    def _test_connection(self):
        """Test if database connection works."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Database connection successful")
            self.connection_established = True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            self.connection_established = False
            raise

    def _init_alloydb_engine(self):
        """Initialize connection to AlloyDB."""
        print(f"🔌 Connecting to AlloyDB: {self.alloydb_cluster}...")
        
        # Initialize Connector
        connector = Connector()

        def getconn():
            conn = connector.connect(
                f"projects/{self.alloydb_project}/locations/{self.alloydb_region}/clusters/{self.alloydb_cluster}/instances/{self.alloydb_instance}",
                "pg8000",
                user=self.db_user,
                password=self.db_pass,
                db=self.db_name,
                ip_type=IPTypes.PUBLIC  # Use IP_TYPES.PRIVATE for internal Cloud Run
            )
            return conn

        # Create engine with the connector
        engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            echo=False
        )
        return engine
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created successfully!")
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_product(self, product_id: str):
        """Fetch a product by ID."""
        with self.get_session() as session:
            return session.query(Product).filter(Product.id == product_id).first()
    
    def get_all_products(self):
        """Fetch all products."""
        with self.get_session() as session:
            return session.query(Product).all()
    
    def update_stock(self, product_id: str, new_stock: int):
        """Update product stock level."""
        with self.get_session() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                product.stock_level = new_stock
                product.last_updated = datetime.utcnow()
                
                # Update status based on threshold
                if new_stock <= 0:
                    product.status = "Critical"
                elif new_stock <= product.reorder_threshold:
                    product.status = "Low"
                else:
                    product.status = "OK"
                
                session.commit()
                return True
        return False
    
    def create_alert(self, product_id: str, alert_type: str, severity: str, message: str):
        """Create a new stock alert."""
        with self.get_session() as session:
            alert = StockAlert(
                product_id=product_id,
                alert_type=alert_type,
                severity=severity,
                message=message
            )
            session.add(alert)
            session.commit()
            return alert.id
    
    def get_active_alerts(self):
        """Get all unresolved alerts."""
        with self.get_session() as session:
            return session.query(StockAlert).filter(StockAlert.resolved == False).all()
    
    def get_shipments_by_status(self, status: str):
        """Get shipments by status."""
        with self.get_session() as session:
            return session.query(ShipmentTracking).filter(
                ShipmentTracking.status == status
            ).all()

# Singleton instance
_db_manager = None

def get_db_manager():
    """Get or create database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
