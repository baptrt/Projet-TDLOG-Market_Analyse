# Projet-TDLOG : Analyse de sentiment de marché

## Fonctionnalités

- **Scraping automatique** en arrière-plan (toutes les heures)
- **Analyse de sentiment** avec FinBERT
- **Interface graphique** PyQt6 pour visualiser les résultats
- **Graphiques interactifs** (barres et évolution temporelle)
- **Archivage JSON** de tous les articles scrapés
- **Base de données SQLite** pour la persistance

## Structure du projet 

```sh
PROJET-TDLOG/
│
├── run.py                          # POINT D'ENTRÉE UNIQUE
│
├── app/                            # COUCHE APPLICATION
│   ├── orchestrator.py             # Orchestre le pipeline complet
│   └── pipeline_runner.py          # Pipeline continu (scraping + analyse)
│
├── domain/                         # COUCHE MÉTIER 
│   ├── entities/                   # Entités métier
│   │   ├── article.py
│   │   └── sentiment.py
│   │
│   └── services/                   # Services métier
│       ├── sentiment_analyzer.py   # Moteur FinBERT
│       └── aggregator.py           # Agrégation
│
├── infrastructure/                 # COUCHE DONNÉES
│   ├── database/
│   │   ├── repository.py           # Interface d'accès DB
│   │   ├── models.py               # Schéma SQLite (users/favoris)
│   │   └── legacy/                 # DB legacy pour test d'intégration
│   │       └── database_handler.py
│   │
│   └── datasources/
│       ├── yahoo_scraper/
│       └── cnbc_scraper/           # Spider Scrapy actif
│
├── mvc/                            # INTERFACE GRAPHIQUE (Pattern MVC)
│   │
│   ├── models/                     # MODÈLE MVC
│   │   └── ui_state.py             # État de l'interface (données affichées)
│   │
│   ├── views/                      # VUE MVC
│   │   ├── main_window.py          # Fenêtre principale (PyQt6)
│   │   └── components/             # Composants réutilisables
│   │       ├── sentiment_bar_chart.py
│   │       └── sentiment_evolution_chart.py
│   │
│   └── controllers/                # CONTRÔLEUR MVC
│       └── main_controller.py      # Gestion événements UI
│
├── data/                              # RÉSULTATS
│   ├── articles.db                    # Base de données SQLite (articles)
│   ├── users.db                       # Base de données SQLite (utilisateurs)
│   ├── scraped_articles_archive.json  # Archive des articles scrapés
│   └── trend_history.json             # Historique des tendances
│
├── scripts/                        # Scripts utilitaires
│   └── view_scraped_archive.py     # Visualiser l'archive
│
tests/
├── unit/
│   ├── test_repository.py          # Tests accès base de données
│   ├── test_aggregator.py          # Tests agrégation sentiments
│   ├── test_sentiment_analyzer.py  # Tests analyse de sentiment
│   ├── test_statistics.py          # Tests analyses statistiques
│   ├── test_sarcasme_complexe.py   # Cas sarcasme (qualitatif)
│   └── test_textes_longs.py        # Texte long (performance)
├── integration/
│   ├── test_pipeline.py            # Test du pipeline
│   └── test_database_flow.py       # Test DB legacy (cycle de vie)
├── data/
│   └── test_articles.json          # Données de test
└── requirements.txt
```

## Installation et lancement

### Prérequis

```bash
pip install -r requirements.txt
```

**Dépendances principales :**
- `scrapy` : Web scraping
- `transformers`, `torch` : FinBERT (analyse de sentiment)
- `PyQt6` : Interface graphique
- `matplotlib` : Graphiques
- `sqlite3` : Base de données (inclus dans Python)

### Lancement de l'application complète

```bash
python run.py
```

**Cela démarre simultanément :**
1. Le **pipeline de scraping** en arrière-plan 
2. L'**interface graphique** dans la fenêtre principale

### Ce qui se passe automatiquement :

1. **Scraping** : Récupère les nouveaux articles de CNBC lorsque l'utilisateur clique "Rafraîchir"
2. **Analyse** : Analyse le sentiment de chaque article avec FinBERT
3. **Sauvegarde** : Stocke les résultats dans :
   - `data/articles.db` (base SQLite des articles)
   - `data/users.db` (base SQLite des utilisateurs)
   - `data/scraped_articles_archive.json` (archive JSON)
   - `data/trend_history.json` (historique des tendances)

### Interface graphique

L'interface permet de :
- **Filtrer** les articles par entreprise, sentiment, recherche textuelle
- **Consulter** le détail de chaque article
- **Visualiser** les graphiques de sentiment
- **Rafraîchir** pour voir les nouveaux articles scrapés

**Bouton "Rafraîchir" :** Lance un nouveau scraping et charge les nouveaux articles depuis la base sans redémarrer l'application.

### Changer de spider

Dans `mvc/controllers/main_controller.py`, lignes 19-23  :

```python
runner = ContinuousPipelineRunner(
    scrapy_project_path="infrastructure/datasources/cnbc_scraper",
    spider_name="cnbc",
    output_dir="outputs"
)
```
ou : 

```python
runner = ContinuousPipelineRunner(
    scrapy_project_path="infrastructure/datasources/yahoo_scraper",
    spider_name="yahoo_scraper",
    output_dir="outputs"
)
```

## Tests

### Tests unitaires

```bash
# Test de l'analyseur de sentiment
python -m pytest tests/unit/test_sentiment_analyzer.py

# Tous les tests unitaires
python -m pytest tests/unit/
```

### Tests d'intégration

```bash
# Test du pipeline complet
python -m pytest tests/integration/test_pipeline.py
```

## Architecture

Le projet suit une **architecture en couches** :

1. **Couche Présentation (MVC)** : Interface PyQt6
2. **Couche Application** : Orchestration du pipeline
3. **Couche Domaine** : Logique métier (analyse, agrégation)
4. **Couche Infrastructure** : Accès aux données (DB, scraping)

Note : un handler SQLite "legacy" est conservé dans
`infrastructure/database/legacy/database_handler.py` pour un test
d'intégration spécifique.

### Pattern MVC

- **Modèle** (`ui_state.py`) : État de l'interface
- **Vue** (`main_window.py`) : Affichage uniquement
- **Contrôleur** (`main_controller.py`) : Gestion des événements

## Fichiers de sortie

| Fichier | Description |
|---------|-------------|
| `data/articles.db` | Base SQLite (articles + sentiments) |
| `data/users.db` | Base SQLite (utilisateurs + favoris) |
| `data/scraped_articles_archive.json` | Archive complète des articles bruts scrapés |
| `data/trend_history.json` | Historique des scores de sentiment par entreprise |
