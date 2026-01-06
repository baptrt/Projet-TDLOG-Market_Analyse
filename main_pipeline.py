import os
import time
import json
import subprocess
import sys
from datetime import datetime

# ================= CONFIGURATION DYNAMIQUE =================

# 1. Chemins des dossiers 
SCRAPY_PROJECT_PATH = "Model/cnbc_scraper"
CONTROLLER_FOLDER_PATH   = "Controller" 

# 2. Configuration des fichiers de sortie
# On utilise le dossier 'outputs' comme défini dans ton nettoyage
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Fichiers
FILE_FINAL_SENTIMENT = os.path.join(OUTPUT_DIR, "articles_with_sentiment.json") # Base de données cumulée
FILE_TRENDS = os.path.join(OUTPUT_DIR, "trend_history.json") # Historique pour le graphique

PATH_SCRAPY_SPIDER = "cnbc"  # Nom du spider Scrapy à utiliser
UNIQUE_KEY = "link"

# ================= IMPORTATION SÉCURISÉE =================
# On ajoute le dossier Controller au chemin de recherche Python
sys.path.append(CONTROLLER_FOLDER_PATH)

try:
    # Maintenant Python peut trouver sentiment.py
    from sentiment import SentimentAnalyzer
    print("Module 'sentiment' importé avec succès.")
except ImportError as e:
    print(f"ERREUR CRITIQUE : Impossible d'importer sentiment.py : {e}")
    print(f"Le chemin calculé était : {CONTROLLER_FOLDER_PATH}")
    sys.exit(1)
# ===========================================================

# Création du dossier outputs s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_pipeline():
    analyzer = SentimentAnalyzer()

    # Vérif Scrapy
    if not os.path.exists(os.path.join(SCRAPY_PROJECT_PATH, "scrapy.cfg")):
        print(f"ERREUR : scrapy.cfg introuvable dans {SCRAPY_PROJECT_PATH}")
        return
    
    # Création du fichier final s'il n'existe pas (pour éviter erreur UI)
    if not os.path.exists(FILE_FINAL_SENTIMENT):
        print(f"Création du fichier vide : {FILE_FINAL_SENTIMENT}")
        with open(FILE_FINAL_SENTIMENT, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    i = 0
    while True:
        i += 1
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Fichiers temporaires pour ce cycle uniquement
        temp_raw_file = os.path.join(OUTPUT_DIR, f"temp_scraping_{i}.json")
        temp_analyzed_file = os.path.join(OUTPUT_DIR, f"temp_analyzed_{i}.json")
        
        print(f"\n=== CYCLE {i} DÉMARRÉ : {timestamp} ===")
        
        # --- ÉTAPE 1 : SCRAPING (Nouveaux articles seulement) ---
        print("1. [En cours] Scraping Yahoo Finance...")
        try:
            # On lance la commande scrapy depuis le bon dossier
            subprocess.run(
                ["scrapy", "crawl", PATH_SCRAPY_SPIDER, "-O", temp_raw_file],
                cwd=SCRAPY_PROJECT_PATH, 
                check=True
            )
        except subprocess.CalledProcessError:
            print("Erreur Scrapy. On passe au cycle suivant.")
            time.sleep(60)
            continue

        # Vérifier si des articles ont été trouvés
        if not os.path.exists(temp_raw_file) or os.path.getsize(temp_raw_file) < 5:
            print("   -> Aucun article récupéré ou fichier vide.")
        else:
            # --- ÉTAPE 2 : ANALYSE DES NOUVEAUX ARTICLES ---
            print("2. [En cours] Analyse de sentiment des nouveaux articles...")
            try:
                # On analyse uniquement le fichier temporaire (rapide)
                new_analyzed_articles = analyzer.analyze_json_file(temp_raw_file, temp_analyzed_file)
                
                if new_analyzed_articles:
                    # --- ÉTAPE 3 : MISE À JOUR DU GRAPHIQUE (TRENDS) ---
                    # Calcul des scores moyens pour ce lot spécifique
                    company_scores_current = analyzer.aggregate_sentiment_by_company(new_analyzed_articles)
                    
                    print(f"   -> Scores du cycle actuel ({timestamp}) :")
                    for company, score in company_scores_current.items():
                        print(f"      - {company} : {score:.3f}")

                    # Sauvegarde dans l'historique
                    trend_entry = {
                        "timestamp": timestamp,
                        "scores": company_scores_current
                    }

                    trend_history = []
                    if os.path.exists(FILE_TRENDS):
                        try:
                            with open(FILE_TRENDS, "r", encoding="utf-8") as f:
                                trend_history = json.load(f)
                        except: trend_history = []
                    
                    trend_history.append(trend_entry)
                    
                    with open(FILE_TRENDS, "w", encoding="utf-8") as f:
                        json.dump(trend_history, f, indent=4, ensure_ascii=False)

                    # --- ÉTAPE 4 : FUSION DANS LA BASE CUMULÉE (POUR UI) ---
                    print("3. [En cours] Fusion dans la base de données finale...")
                    
                    # Chargement de l'existant
                    all_articles = []
                    if os.path.exists(FILE_FINAL_SENTIMENT):
                        try:
                            with open(FILE_FINAL_SENTIMENT, 'r', encoding='utf-8') as f:
                                all_articles = json.load(f)
                        except: all_articles = []

                    # Dictionnaire pour déduplication (clé = lien)
                    articles_map = {}
                    for item in all_articles:
                        link = item.get("link")
                        company = item.get("company")
                        if link and company:
                            articles_map[(link, company)] = item
                    
                    added_count = 0
                    for item in new_analyzed_articles:
                        link = item.get("link")
                        company = item.get("company")
                        if link and company:
                            composite_key = (link, company)
                            
                            if composite_key not in articles_map:
                                articles_map[composite_key] = item
                                added_count += 1
                    
                    # Sauvegarde finale
                    final_list = list(articles_map.values())
                    with open(FILE_FINAL_SENTIMENT, 'w', encoding='utf-8') as f:
                        json.dump(final_list, f, indent=4, ensure_ascii=False)
                    
                    print(f"   -> Base mise à jour : {added_count} nouveaux articles ajoutés.")
                
                else:
                    print("   -> Aucun article valide après analyse.")

            except Exception as e:
                print(f"ERREUR lors de l'analyse ou de la fusion : {e}")

        # Nettoyage des fichiers temporaires
        if os.path.exists(temp_raw_file): os.remove(temp_raw_file)
        if os.path.exists(temp_analyzed_file): os.remove(temp_analyzed_file)

        # --- ÉTAPE 5 : ATTENTE ---
        elapsed = (datetime.now() - start_time).total_seconds()
        sleep_time = max(0, 3600 - elapsed) # 1 h
        print(f"=== CYCLE TERMINÉ. Pause de {int(sleep_time/60)} minutes... ===\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_pipeline()