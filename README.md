# Gogo School

Application web Flask de gestion des notes des étudiants : saisie des
étudiants (nom, prénoms, filière, notes), calcul automatique des moyennes
et classement par filière avec filtre.

## Fonctionnalités

- Page d'accueil de présentation de Gogo School
- Formulaire d'ajout d'un étudiant (nom, prénoms, filière, notes sur 20)
- Calcul automatique de la moyenne de chaque étudiant
- Classement avec gestion des ex æquo
- Filtre par filière
- Suppression d'un étudiant

## Technologies

- Python 3.12
- Flask
- Docker

## Structure du projet

```
├── app.py              Code de l'application Flask
├── requirements.txt    Dépendances Python
├── Dockerfile          Construction de l'image Docker
└── .dockerignore       Fichiers exclus de l'image
```

## Lancer l'application avec Docker

```bash
docker pull gam1soc/gogo-school:v1
docker run -p 5000:5000 -v donnees:/data gam1soc/gogo-school:v1
```

Puis ouvrir http://localhost:5000

L'option `-v donnees:/data` conserve la liste des étudiants quand le
conteneur est supprimé.

## Construire l'image soi-même

```bash
docker build -t gogo-school .
docker run -p 5000:5000 -v donnees:/data gogo-school
```

## Déploiement

- Image Docker Hub : https://hub.docker.com/r/gam1soc/gogo-school
- Application en ligne : http://13.60.184.99

## Équipe

- Gogo Ange Michel 