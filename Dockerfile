FROM python:3.9-slim

# # Updating pip
# RUN pip install --upgrade pip

# Try building the environment:
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy application files:
COPY . /application/
WORKDIR /application/

# Install custom packages:
RUN pip install .
RUN apt-get update
RUN apt-get install -y traceroute

# Expose port:
EXPOSE 8000

# Create log directory:
RUN mkdir -p logs

# Upon firing up the container, the app starts:
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app","--log-level=debug","--access-logfile=logs/access.log","--error-logfile=logs/error.log"]
