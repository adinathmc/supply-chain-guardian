FROM python:3.11-slim
WORKDIR /app

# Install only what we need
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code from build context (when run from api/ folder)
COPY . ./api/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
