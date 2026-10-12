# Image de base : Python 3.12 en version allégée (slim), pour une image plus petite
FROM python:3.12-slim

# Dossier de travail dans le conteneur : les commandes suivantes s'y exécutent
WORKDIR /app

# Copie du fichier des dépendances en premier, pour profiter du cache Docker
COPY requirements.txt .

# Installation de Flask (--no-cache-dir évite de garder le cache pip dans l'image)
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application dans le conteneur
COPY . .

# Indique que l'application écoute sur le port 5000
EXPOSE 5000

# Commande exécutée au démarrage du conteneur : lance l'application Flask
CMD ["python", "app.py"]