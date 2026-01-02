# Deploying Supply Chain Guardian to Google Cloud

This document explains two straightforward options to deploy the Streamlit UI and agent: **Cloud Run (recommended)** and **App Engine (flexible)**. The repository already contains a `Dockerfile` and a sample `cloudbuild.yaml` for Cloud Build + Cloud Run.

Prerequisites:
- Install and authenticate the Google Cloud SDK: `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`
- Enable required APIs: Cloud Run, Cloud Build, Artifact Registry (or Container Registry), Vertex AI if you plan to use it.

Recommended: Cloud Run (managed)

1. Build & push image (locally using Docker)

```bash
docker build -t gcr.io/PROJECT_ID/supply-chain-guardian:latest .
docker push gcr.io/PROJECT_ID/supply-chain-guardian:latest
```

2. Deploy to Cloud Run

```bash
gcloud run deploy supply-chain-guardian \
  --image gcr.io/PROJECT_ID/supply-chain-guardian:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

Notes:
- Cloud Run will set the `PORT` env var automatically; the included `Dockerfile` exposes `8080`.
- If you need to set environment variables (for example `GOOGLE_CLOUD_PROJECT` or API keys), add `--set-env-vars KEY=VALUE` to `gcloud run deploy` or configure them in the Cloud Run console.

Using Cloud Build (CI):
- Build & deploy via the included `cloudbuild.yaml`:

```bash
gcloud builds submit --config cloudbuild.yaml --substitutions=PROJECT_ID=YOUR_PROJECT_ID
```

Alternative: App Engine (flexible) — simpler if you prefer non-container but less flexible for custom system deps

1. Create `app.yaml` in the repository root:

```yaml
runtime: python
env: flex
manual_scaling:
  instances: 1
```

2. Deploy:

```bash
gcloud app deploy app.yaml --project=PROJECT_ID --quiet
```

Environment variables, secrets & service accounts
- Do NOT hardcode credentials. Use Secret Manager and grant the Cloud Run service account access to secrets.
- To set service account for Cloud Run:

```bash
gcloud run services update-iam-policy supply-chain-guardian --region=us-central1 --platform=managed
# or during deploy: --service-account YOUR_SA@PROJECT_ID.iam.gserviceaccount.com
```

Vertex AI and other Google APIs
- If you plan to use Vertex AI (the code references `vertexai`), grant the service account the `Vertex AI Developer` role and ensure `vertexai` is authenticated via Workload Identity or a service account key.

Local testing
- Run streamlit locally:

```bash
pip install -r requirements.txt
streamlit run ui/app.py
```

Troubleshooting
- If packages fail to install in Docker, ensure necessary system packages (libpq-dev, build-essential) are in the `Dockerfile` — already included.
- For database connectivity (Postgres), supply DB URL via env vars and configure VPC connector for private networks if needed.

If you want, I can:
- Add a `gcloud` deployment script, or
- Create an `app.yaml` for App Engine, or
- Set up Artifact Registry / GitHub Actions for CI/CD.
