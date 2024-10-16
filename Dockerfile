# Using Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY . .

# Start the Flask application
CMD ["python", "FlaskBinance.py"]
