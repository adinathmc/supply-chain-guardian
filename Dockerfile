FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install OS-level dependencies needed for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

# Streamlit expects the port in environment variable PORT. Use headless run.
CMD ["streamlit", "run", "ui/app.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.headless", "true"]
