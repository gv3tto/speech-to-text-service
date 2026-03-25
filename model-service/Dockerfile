# Start from a Python image with GPU support
FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir setuptools && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Tell Docker what command to run when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
