"""Deploy Supply Chain Guardian to Google Cloud Vertex AI."""
import vertexai
from vertexai.preview import reasoning_engines
from main import get_supply_chain_guardian
import os
import sys

# 1. Configuration - Load from environment
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

if not PROJECT_ID or not STAGING_BUCKET:
    print("❌ Error: GOOGLE_CLOUD_PROJECT and STAGING_BUCKET environment variables must be set.")
    print("\n💡 Quick Setup:")
    print("  1. Create a .env file with:")
    print("     GOOGLE_CLOUD_PROJECT=your-project-id")
    print("     GOOGLE_CLOUD_REGION=us-central1")
    print("     STAGING_BUCKET=gs://your-bucket-name")
    print("\n  2. Run: source .env (Linux/Mac) or set variables in PowerShell")
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

# 3. Deploy the Orchestrator with all dependencies
print("\n📤 Packaging and deploying agents...")
print("   This may take 5-10 minutes...")

try:
    remote_guardian = reasoning_engines.ReasoningEngine.create(
        get_supply_chain_guardian(),
        requirements=[
            "google-cloud-aiplatform[agent_engines,adk]>=1.60.0",
            "google-cloud-storage>=2.0.0",
            "google-cloud-pubsub>=2.0.0",
            "cloudpickle==3.0.0",
            "pandas>=2.0.0",
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "requests>=2.31.0",
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
    print("\n📝 Test the deployed agent:")
    print("   from vertexai.preview import reasoning_engines")
    print(f"   agent = reasoning_engines.ReasoningEngine('{remote_guardian.resource_name}')")
    print("   response = agent.query(input='What is our inventory status?')")
    print("   print(response)")
    print("\n" + "="*60)

except Exception as e:
    print(f"\n❌ Deployment failed: {e}")
    print("\n🔍 Troubleshooting:")
    print("   • Verify service account has Vertex AI permissions")
    print("   • Check that all APIs are enabled")
    print("   • Ensure staging bucket exists and is accessible")
    print("   • Review logs in Google Cloud Console")
    sys.exit(1)