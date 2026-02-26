# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Install OpenJDK-17 and build dependencies
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk-headless libpq-dev gcc python3-dev && \
    apt-get clean;

# Set the working directory to /app
WORKDIR /app

# Copy requirements from the subfolder to the root of the build
COPY dsa-challenge-app/requirements.txt .

# Install any needed packages (using binary if possible, but libpq-dev is there as fallback)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary gunicorn

# Copy all files from the subfolder into the container
COPY dsa-challenge-app/ .

# Make port 5000 available
EXPOSE 5000

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Run app.py
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]
