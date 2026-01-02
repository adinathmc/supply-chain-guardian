import vertexai
from vertexai.preview import reasoning_engines
from main import get_supply_chain_guardian # This is your orchestrator function

# 1. Configuration
PROJECT_ID = "inventory-agent-x"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://inventory-agent-x-staging-bucket"

# 2. Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

print("🚀 Starting deployment to Vertex AI Agent Engine...")

# 3. Deploy the Orchestrator
# This command packages your code and local dependencies
remote_guardian = reasoning_engines.ReasoningEngine.create(
    get_supply_chain_guardian(),
    requirements=[
        "google-cloud-aiplatform[agent_engines,adk]",
        "cloudpickle==3.0.0",
        "pandas",
        "sqlalchemy",
        "psycopg2-binary"
    ],
    display_name="Supply Chain Guardian Engine",
    description="Production-scale multi-agent system for logistics and inventory.",
)

print("\n✅ DEPLOYMENT SUCCESSFUL!")
print(f"Agent Resource Name: {remote_guardian.resource_name}")
print("Copy the Resource Name above and paste it into your Streamlit app.py!")