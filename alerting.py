"""Alerting system for critical inventory and supply chain events."""
import os
from typing import List, Dict, Any
from datetime import datetime
from database import get_db_manager
import json

try:
    from google.cloud import pubsub_v1
    PUBSUB_AVAILABLE = True
except ImportError:
    PUBSUB_AVAILABLE = False
    print("⚠️ google-cloud-pubsub not installed. Pub/Sub alerts disabled.")

class AlertingService:
    """Manages alerts for critical inventory and supply chain events."""
    
    def __init__(self):
        self.db = get_db_manager()
        self.alert_email = os.getenv("ALERT_EMAIL")
        self.pubsub_topic = os.getenv("PUBSUB_TOPIC")
        
        # Initialize Pub/Sub if available
        if PUBSUB_AVAILABLE and self.pubsub_topic:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                print(f"✅ Pub/Sub alerting enabled: {self.pubsub_topic}")
            except Exception as e:
                print(f"⚠️ Pub/Sub init error: {e}")
                self.publisher = None
        else:
            self.publisher = None
    
    def check_and_alert(self) -> List[Dict[str, Any]]:
        """Check inventory status and create alerts for critical conditions."""
        products = self.db.get_all_products()
        alerts_created = []
        
        for product in products:
            # Check critical stock
            if product.stock_level <= 0:
                alert = self._create_alert(
                    product_id=product.id,
                    alert_type="critical_stock",
                    severity="High",
                    message=f"{product.name} is OUT OF STOCK! Immediate action required."
                )
                alerts_created.append(alert)
                
            # Check low stock
            elif product.stock_level <= product.reorder_threshold:
                alert = self._create_alert(
                    product_id=product.id,
                    alert_type="low_stock",
                    severity="Medium",
                    message=f"{product.name} stock is below reorder threshold ({product.stock_level}/{product.reorder_threshold})"
                )
                alerts_created.append(alert)
        
        # Check delayed shipments
        delayed_shipments = self.db.get_shipments_by_status("delayed")
        for shipment in delayed_shipments:
            if shipment.delay_days > 3:
                alert = self._create_alert(
                    product_id=shipment.product_id,
                    alert_type="delayed_shipment",
                    severity="High",
                    message=f"Shipment delayed by {shipment.delay_days} days. Reason: {shipment.delay_reason}"
                )
                alerts_created.append(alert)
        
        return alerts_created
    
    def _create_alert(self, product_id: str, alert_type: str, severity: str, message: str) -> Dict[str, Any]:
        """Create an alert in the database and notify via configured channels."""
        # Save to database
        alert_id = self.db.create_alert(product_id, alert_type, severity, message)
        
        alert_data = {
            "alert_id": alert_id,
            "product_id": product_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Send notifications
        if severity in ["High", "Critical"]:
            self._send_notification(alert_data)
        
        return alert_data
    
    def _send_notification(self, alert_data: Dict[str, Any]):
        """Send alert notification via Pub/Sub or log."""
        # Pub/Sub notification
        if self.publisher and self.pubsub_topic:
            try:
                message_json = json.dumps(alert_data)
                future = self.publisher.publish(
                    self.pubsub_topic,
                    message_json.encode("utf-8"),
                    severity=alert_data['severity'],
                    alert_type=alert_data['alert_type']
                )
                print(f"📢 Alert published to Pub/Sub: {alert_data['product_id']} - {alert_data['severity']}")
            except Exception as e:
                print(f"❌ Pub/Sub publish error: {e}")
        
        # Console notification (fallback)
        else:
            print(f"🚨 [{alert_data['severity']}] {alert_data['message']}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all active alerts."""
        alerts = self.db.get_active_alerts()
        
        by_severity = {
            "High": [],
            "Medium": [],
            "Low": []
        }
        
        for alert in alerts:
            severity = alert.severity
            if severity in by_severity:
                by_severity[severity].append({
                    "id": alert.id,
                    "product_id": alert.product_id,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "created_at": alert.created_at.isoformat()
                })
        
        return {
            "total_alerts": len(alerts),
            "high_severity": len(by_severity["High"]),
            "medium_severity": len(by_severity["Medium"]),
            "low_severity": len(by_severity["Low"]),
            "alerts_by_severity": by_severity
        }

# Singleton
_alerting_service = None

def get_alerting_service():
    """Get or create alerting service singleton."""
    global _alerting_service
    if _alerting_service is None:
        _alerting_service = AlertingService()
    return _alerting_service

# CLI for manual alert checking
if __name__ == "__main__":
    print("🔔 Running Alert Check...")
    service = get_alerting_service()
    
    alerts = service.check_and_alert()
    
    if alerts:
        print(f"\n✅ Created {len(alerts)} alerts")
        for alert in alerts:
            print(f"  • [{alert['severity']}] {alert['product_id']}: {alert['message']}")
    else:
        print("\n✅ No critical conditions detected")
    
    print("\n📊 Alert Summary:")
    summary = service.get_alert_summary()
    print(f"  Total Active Alerts: {summary['total_alerts']}")
    print(f"  High Priority: {summary['high_severity']}")
    print(f"  Medium Priority: {summary['medium_severity']}")
