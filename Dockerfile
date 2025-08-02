# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install Git and Git LFS so we can download the large model files
RUN apt-get update && apt-get install -y git git-lfs && git-lfs install

# Copy the file that lists the requirements
COPY requirements.txt .

# Install the Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (app.py, chat.py, saved_models/, etc.)
COPY . .

# The command to run the web server when the container launches
CMD ["gunicorn", "--workers", "1", "--threads", "1", "--timeout", "120", "app:app"]