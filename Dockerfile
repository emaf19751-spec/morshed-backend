# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install Python dependencies (FastAPI, psycopg2, OpenAI, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY app ./app

# Environment setup
ENV PYTHONUNBUFFERED=1

# Expose port (Render expects 8000)
EXPOSE 8000

# Start FastAPI using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

