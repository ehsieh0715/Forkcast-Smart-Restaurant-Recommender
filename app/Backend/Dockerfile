FROM python:3.11-slim

# Install system dependencies (GDAL and its dependencies)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_VERSION=3.6.0

# Set working directory
WORKDIR /app

# Copy Backend files to /app folders
COPY requirements.txt /app/

# Install system dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose the port the app runs on, default of flask is 5000
EXPOSE 5000

# Set default command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]