# Use Python slim image for a lightweight, production-ready container
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for scientific packages (numpy, pandas, scipy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files and folders in the backend folder (context) into /app
COPY . .

EXPOSE 8000

# Set python path to /app so that it can resolve "ai" and "scripts" imports
ENV PYTHONPATH=/app

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
