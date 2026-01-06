# Projet-TDLOG : Analyse de sentiment de marché

## Structure du projet 

```sh
PROJET-TDLOG/
│
├── run.py                          # Point d'entrée unique
│
├── app/                            # COUCHE APPLICATION
│   ├── __init__.py
│   └── orchestrator.py             # Orchestre le pipeline complet
│
├── domain/                         # COUCHE MÉTIER (Business Logic)
│   ├── __init__.py
│   ├── entities/                   # Entités métier
│   │   ├── __init__.py
│   │   ├── article.py
│   │   └── sentiment.py
│   │
│   └── services/                   # Services métier
│       ├── __init__.py
│       ├── sentiment_analyzer.py   # Moteur FinBERT
│       └── aggregator.py           # Agrégation
│
├── infrastructure/                 # COUCHE DONNÉES
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── repository.py           # Interface d'accès DB
│   │   └── models.py               # Schéma SQLite
│   │
│   └── datasources/
│       ├── __init__.py
│       ├── yahoo_scraper/
│       └── cnbc_scraper/
│
├── mvc/                            # INTERFACE GRAPHIQUE (Pattern MVC)
│   ├── __init__.py
│   │
│   ├── models/                     # MODÈLE MVC
│   │   ├── __init__.py
│   │   └── ui_state.py             # État de l'interface (données affichées)
│   │
│   ├── views/                      # VUE MVC
│   │   ├── __init__.py
│   │   ├── main_window.py          # Fenêtre principale (PyQt6)
│   │   ├── chart_widget.py         # Widget graphiques (Matplotlib)
│   │   └── components/             # Composants réutilisables
│   │       ├── __init__.py
│   │       ├── ticker_input.py
│   │       └── results_table.py
│   │
│   └── controllers/                # CONTRÔLEUR MVC
│       ├── __init__.py
│       └── main_controller.py      # Gestion événements UI
│
├── outputs/                        # Résultats
├── tests/                          # Tests
├── config/                         # Configuration
└── requirements.txt
```

## Utilisation du scraping 

### Installation 

- Installer scrapy (pip install scrapy)
- Installer yfinance (pip install yfinance)

### Run

- Terminal : scrapy crawl yahoo_news -o "nom du fichier json dans lequel on souhaite stocker".json
- Faire tourner en fond le scraping régulier (toutes les heures) : nohup python3 yahoo_scraper/run_scraper.py > scraper.log 2>&1 &


## Utilisation de l'Interface Utilisateur

- Installer PyQt6 (pip install PyQt6)

### Run 

- Se placer dans le dossier yahoo_scraper (pour accéder au fichier .json)
