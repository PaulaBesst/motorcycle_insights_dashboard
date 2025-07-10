# Use stable Python version
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Set working directory to the folder where app.py lives
WORKDIR /app/dashboard

# Expose port if needed (for web apps like Flask/FastAPI/Streamlit)
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]
