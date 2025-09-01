# Use an official lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy dependency file and install
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the web server application code
COPY ./app /app/app

# Copy your actual compiler code
COPY ./compiler /app/compiler

# Expose the port the app runs on
EXPOSE 8000

# CORRECT CMD: Start the Uvicorn web server, not the compiler script
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
