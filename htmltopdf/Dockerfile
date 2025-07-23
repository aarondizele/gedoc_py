# Utilise une image Python slim
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crée le répertoire de travail
WORKDIR /app

# Installe les dépendances système nécessaires à WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie les fichiers de dépendances Python
COPY requirements.txt .

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le projet
COPY . .

# Copie et rend exécutable le script d’entrée
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Spécifie le point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
