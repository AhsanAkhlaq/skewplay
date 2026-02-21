FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (build-essential needed for some ML libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy both requirement files just in case
COPY requirements.txt ./

# Install python dependencies from both files (ignoring errors if one has duplicates)
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI default port
EXPOSE 8000

# Start uvicorn server with hot reload
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
