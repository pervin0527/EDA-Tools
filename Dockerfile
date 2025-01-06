# Base Image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y procps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY ./src /app/src

# Expose Streamlit default port
EXPOSE 8501