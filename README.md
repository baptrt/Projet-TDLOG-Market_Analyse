# Projet-TDLOG : Analyse de sentiment de marché

## Structure du projet 

```sh
PROJET-TDLOG/
│
├── run.py                  #  POINT D'ENTRÉE UNIQUE (Lance tout)
│
├── Controller/             #  Cerveau
│   ├── main.py             # Orchestrateur de l'analyse
│   └── sentiment.py        # Moteur IA (FinBERT) et calculs
│
├── Model/                  #  Données
│   ├── database.py         # Gestionnaire Base de Données (SQLite)
│   ├── yahoo_scraper/      # Robot Scrapy + yfinance
│   └── cnbc_scraper/       # Robot Scrapy with HTML 
│
├── View/                   #  Interface
│   └── UI.py               # Application de bureau (PyQt6 + Matplotlib)
│
├── outputs/                #  Stockage (Généré automatiquement)
│   ├── market_sentiment.db # Base de données SQL finale
│   ├── news.json           # Données brutes (Scraping)
│   └── articles_...json    # Backup JSON des résultats
│
└── tests/                  #  Qualité Logicielle
    ├── test_aggregation.py # Test unitaire logique (Snapshot)
    └── test_scraper.py     # Test d'intégration (Audit données)
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
