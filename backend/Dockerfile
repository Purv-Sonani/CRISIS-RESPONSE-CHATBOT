FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rasa
RUN pip install --upgrade pip
RUN pip install rasa==3.6.21

# Copy project files
COPY . /app

# --- HUGGING FACE SPECIFIC SETUP ---

# 1. Setup non-root user (Required for HF Spaces)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

RUN sed -i 's/\r$//' /app/start_services.sh && \
    chmod +x /app/start_services.sh

# 2. Train the model inside the container
RUN rasa train

# Expose the specific Hugging Face port
EXPOSE 7860

# Start command
CMD ["./start_services.sh"]
