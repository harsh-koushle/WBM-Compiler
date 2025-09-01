# Use an official lightweight Python image as a base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your compiler's source code into the container
COPY ./compiler /app

# Install any dependencies your compiler might have (if any)
# If your compiler needs libraries, add a requirements.txt in the compiler/ folder
# and uncomment the next line:
# RUN pip install --no-cache-dir -r requirements.txt

# This command runs when the container starts.
# We will override this with the specific file to compile.
# This just confirms the setup is okay.
CMD ["python", "main.py"]