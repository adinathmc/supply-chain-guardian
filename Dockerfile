FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

# Default to Streamlit UI (can be overridden at deploy time)
CMD ["streamlit", "run", "ui/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
