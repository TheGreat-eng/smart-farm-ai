# Stage 1: Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by OpenCV (với tên gói đã sửa)
# --no-install-recommends giúp giảm kích thước image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "ai_service.py"]