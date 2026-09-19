FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cached if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Do NOT copy .env — all configuration must come from environment variables at runtime
# Do NOT copy venv/, tests/, or *.py scripts

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
