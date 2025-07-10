# Use a stable Python version (avoid 3.13 for now)
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port (only for web services)
EXPOSE 8000

# Start your app (change this to your actual command)
CMD ["python", "app.py"]
