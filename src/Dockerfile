# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app
# Copy the application files into the working directory
COPY . .
# Install the application dependencies
# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8080
# Define the entry point for the container
# 
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
RUN python main.py
