# Use a standard Python base image
FROM python:3.6-slim

# Install system dependencies required for numpy and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libffi-dev \        
    libssl-dev \        
    python3-dev \       
    && rm -rf /var/lib/apt/lists/*

# Updating pip (optional, but recommended):
RUN pip install --upgrade pip

# Try building the environment:
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application files:
COPY . /application/
WORKDIR /application/

# Install custom packages:
RUN pip install .
RUN apt-get update && apt-get install -y traceroute

# Expose port:
EXPOSE 8000

# Create log directory:
RUN mkdir -p logs

# Upon firing up the container, the app starts:
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app","--log-level=debug","--access-logfile=logs/access.log","--error-logfile=logs/error.log"]