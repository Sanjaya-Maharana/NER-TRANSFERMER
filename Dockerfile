# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for building some Python packages
RUN apk --no-cache add g++ gcc libffi-dev musl-dev

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Command to run the Gunicorn server with Uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--workers", "2", "--bind", "0.0.0.0:8000"]
