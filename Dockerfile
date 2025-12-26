# Use the official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set work directory
WORKDIR /app

# Install system dependencies (needed for some Python packages like psycopg2 or pillow)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run collectstatic (Wagtail needs this for the admin UI)
# Note: This assumes you have a placeholder for STATIC_ROOT in settings
RUN python manage.py collectstatic --noinput

# Run the application using Gunicorn
CMD exec gunicorn mms_site.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0