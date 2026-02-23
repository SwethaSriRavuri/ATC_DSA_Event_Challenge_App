# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Install OpenJDK-17
# We need this to run and compile Java code
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk-headless && \
    apt-get clean;

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
# Using Gunicorn for production
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]
