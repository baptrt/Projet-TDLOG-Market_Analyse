# Projet-TDLOG : Analyse de sentiment de marché

## Structure du projet 

```sh
└── Projet-TDLOG-Market_Analyse/
    ├── Controller
    │   ├── main.py
    │   └── sentiment.py
    ├── Model
    │   └── yahoo_scraper
    ├── README.md
    └── View
        └── UI.py
```

## Utilisation du scraping 

### Installation 

- Installer scrapy (pip install scrapy)
- Installer yfinance (pip install yfinance)

### Run

- Terminal : scrapy crawl yahoo_news -o "nom du fichier json dans lequel on souhaite stocker".json


## Utilisation de l'Interface Utilisateur

- Installer PyQt6 (pip install PyQt6)

### Run 

- Se placer dans le dossier yahoo_scraper (pour accéder au fichier .json)
