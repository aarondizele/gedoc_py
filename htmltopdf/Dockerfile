# Utilise une image officielle avec dependencies WeasyPrint
FROM python:3.11-slim

# Install system dependencies for WeasyPrint (Debian-based)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libxml2 \
    libxslt1.1 \
    libgdk-pixbuf2.0-0 \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 9000

# Run gunicorn
CMD ["gunicorn", "htmltopdf.wsgi:application", "--bind", "0.0.0.0:9000"]
