# KCET AI Prep Assistant - Docker Image
# Uses: llama3.1, sarvam-1 (Ollama), all-MiniLM-L6-v2 (Hugging Face)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p pdfs chroma_db

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PATH=/app/chroma_db
ENV PDF_FOLDER=/app/pdfs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --timeout=3s \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start Streamlit app
CMD ["streamlit", "run", "app.py", "--port=8501", "--host=0.0.0.0"]