FROM python:3.10-slim

# Installer les dépendances système nécessaires pour scrapy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Commande par défaut pour lancer le scraping
CMD ["scrapy", "crawl", "alloc_newfilms"]