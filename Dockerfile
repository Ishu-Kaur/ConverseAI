# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed system-level packages
# (Sometimes needed for libraries like numpy or tensorflow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Run the build scripts to generate the data and model files
# This happens INSIDE the container during the Render build process
RUN python prepare_data.py && python 02_train_chatbot.py

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
# This uses gunicorn, a production-ready web server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]