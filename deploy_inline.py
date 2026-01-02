"""Deploy Supply Chain Guardian to Google Cloud Vertex AI - Inline version."""
import vertexai
from vertexai.preview import reasoning_engines
from vertexai.generative_models import GenerativeModel
import os
import sys

# 1. Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

if not PROJECT_ID or not STAGING_BUCKET:
    print("❌ Error: GOOGLE_CLOUD_PROJECT and STAGING_BUCKET environment variables must be set.")
    sys.exit(1)

print("🚀 Starting deployment to Vertex AI Agent Engine...")
print(f"📦 Project: {PROJECT_ID}")
print(f"📍 Region: {LOCATION}")
print(f"🪣 Staging: {STAGING_BUCKET}")

# 2. Initialize Vertex AI
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    print("✅ Vertex AI initialized")
except Exception as e:
    print(f"❌ Vertex AI initialization failed: {e}")
    sys.exit(1)

# 3. Create agent with query() method
class SupplyChainGuardian:
    """Simple agent wrapper with query method for Reasoning Engine."""
    
    def __init__(self):
        self.model = GenerativeModel(
            "gemini-2.0-flash-exp",
            system_instruction="""You are Supply Chain Guardian - an intelligent AI system for supply chain management.

Your responsibilities:
- Monitor inventory and stock levels in real-time
- Predict delivery delays using weather and external data
- Analyze market trends and suggest products
- Provide supply chain health assessments
- Generate actionable insights for supply chain optimization

Be concise, data-driven, and action-oriented in your responses."""
        )
    
    def query(self, input: str) -> str:
        """Process a query and return a response."""
        try:
            response = self.model.generate_content(input)
            return response.text
        except Exception as e:
            return f"Error processing query: {str(e)}"

print("\n📤 Packaging and deploying agents...")
print("   This may take 5-10 minutes...")

try:
    remote_guardian = reasoning_engines.ReasoningEngine.create(
        SupplyChainGuardian(),
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]>=1.60.0",
            "google-cloud-storage>=2.0.0",
            "google-cloud-pubsub>=2.0.0",
            "pandas>=2.0.0",
            "sqlalchemy>=2.0.0",
            "requests",
        ],
        display_name="Supply Chain Guardian v2.0",
        description="Multi-agent AI system for supply chain management with inventory tracking, delay prediction, and market intelligence.",
    )
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT SUCCESSFUL!")
    print("="*60)
    print(f"\n📋 Agent Resource Name:")
    print(f"   {remote_guardian.resource_name}")
    print(f"\n🔗 View in Console:")
    print(f"   https://console.cloud.google.com/vertex-ai/reasoning-engines?project={PROJECT_ID}")
    print("\n💡 Next Steps:")
    print("   1. Copy the Resource Name above")
    print("   2. Paste it into your Streamlit app (ui/app.py)")
    print("   3. Run: streamlit run ui/app.py")
    print("\n" + "="*60)

except Exception as e:
    print(f"\n❌ Deployment failed: {e}")
    print("\n🔍 Troubleshooting:")
    print("   • Verify service account has Vertex AI permissions")
    print("   • Check that all APIs are enabled")
    print("   • Ensure staging bucket exists and is accessible")
    sys.exit(1)
