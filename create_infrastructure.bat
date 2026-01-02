@echo off
setlocal

REM Configuration
REM User expects to set PROJECT_ID before running, but we can ask for it if missing.
if "%PROJECT_ID%"=="" (
    set /p PROJECT_ID="Enter your Google Cloud Project ID: "
)

if "%REGION%"=="" set REGION=us-central1
if "%DB_PASS%"=="" set DB_PASS=supplychain123

echo ==================================================
echo 🚀 Creating Infrastructure for Supply Chain Guardian
echo Project: %PROJECT_ID%
echo Region:  %REGION%
echo ==================================================

REM 1. Enable APIs
echo.
echo Enabling APIs...
call gcloud services enable alloydb.googleapis.com servicenetworking.googleapis.com compute.googleapis.com cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

echo.
echo Waiting 30s for API permissions to propagate...
timeout /t 30

REM 1.5 Configure Private Services Access (Required for AlloyDB)
echo.
echo Configuring VPC Peering for AlloyDB...
call gcloud compute addresses create google-managed-services-default --global --purpose=VPC_PEERING --prefix-length=16 --description="peering range for Google" --network=default
call gcloud services vpc-peerings connect --service=servicenetworking.googleapis.com --ranges=google-managed-services-default --network=default

REM 2. Setup AlloyDB
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating AlloyDB Cluster (this takes ~15 mins)...
call gcloud alloydb clusters create supply-chain-cluster --region=%REGION% --password=%DB_PASS%

echo Creating AlloyDB Instance...
call gcloud alloydb instances create supply-chain-instance --cluster=supply-chain-cluster --region=%REGION% --cpu-count=2 --instance-type=PRIMARY

REM 3. Build and Deploy UI (Containerized Agent)
echo.
echo Building Container Image...
call gcloud builds submit --tag gcr.io/%PROJECT_ID%/supply-chain-ui

echo.
echo Deploying to Cloud Run...
call gcloud run deploy supply-chain-ui --image gcr.io/%PROJECT_ID%/supply-chain-ui --platform managed --region=%REGION% --allow-unauthenticated --set-env-vars="GOOGLE_CLOUD_PROJECT=%PROJECT_ID%,GOOGLE_CLOUD_REGION=%REGION%,ALLOYDB_PROJECT=%PROJECT_ID%,ALLOYDB_REGION=%REGION%,ALLOYDB_CLUSTER=supply-chain-cluster,ALLOYDB_INSTANCE=supply-chain-instance,DB_USER=postgres,DB_PASS=%DB_PASS%"

echo.
echo ==================================================
echo ✅ Deployment Complete!
echo Access your Supply Chain Guardian at the URL above.
echo ==================================================

endlocal
