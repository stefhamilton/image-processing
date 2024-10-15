# Use a slim Python image as a base
FROM python:3.10-slim

# Set a directory for the app inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Open port 5000 (for example, if you are running a web server)
EXPOSE 5000

# Command to run your application
CMD ["python", "./scripts/create_kml.py"]
