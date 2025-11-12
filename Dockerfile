# Step 1: Use official Python image
FROM python:3.11-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy dependency file
COPY requirements.txt .

# Step 5: Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Step 6: Copy project files
COPY . .

# Step 7: Expose port
EXPOSE 8000

# Step 8: Run server with Gunicorn
CMD ["gunicorn", "studentstudyportal.wsgi:application", "--bind", "0.0.0.0:8000"]

