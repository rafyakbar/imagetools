# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the RabbitMQ setup script
COPY setup_rabbitmq.py .

# Command to run the RabbitMQ setup script
#CMD ["python", "setup_rabbitmq.py"]