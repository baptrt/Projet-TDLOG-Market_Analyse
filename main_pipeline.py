import os
import time
import json
import subprocess
import sys
from datetime import datetime

# ================= CONFIGURATION =================

# 1. Chemins des dossiers 
SCRAPY_PROJECT_PATH = "/Users/baptistetrt/Desktop/Études/Ponts/TDLOG/Model/yahoo_scraper"
CONTROLLER_FOLDER_PATH   = "/Users/baptistetrt/Desktop/Études/Ponts/TDLOG/Controller" 

# 2. Configuration des fichiers de sortie
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Fichiers
FILE_RAW_GLOBAL = os.path.join(OUTPUT_DIR, "global_news.json")        # Entrée 
FILE_FINAL_SENTIMENT = os.path.join(OUTPUT_DIR, "articles_with_sentiment.json") # Sortie

PATH_SCRAPY_SPIDER = "yahoo_news"
UNIQUE_KEY = "link"

# ================= IMPORTATION =================
sys.path.append(CONTROLLER_FOLDER_PATH)

try:
    from sentiment import SentimentAnalyzer
    print("Module 'sentiment' importé avec succès.")
except ImportError as e:
    print(f"ERREUR CRITIQUE : Impossible d'importer sentiment.py : {e}")
    print(f"Vérifie que sentiment.py est bien dans : {CONTROLLER_FOLDER_PATH}")
    sys.exit(1)
# ===========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_pipeline():
    # Initialisation de l'analyseur
    analyzer = SentimentAnalyzer()

    # Vérif Scrapy
    if not os.path.exists(os.path.join(SCRAPY_PROJECT_PATH, "scrapy.cfg")):
        print(f"ERREUR : scrapy.cfg introuvable dans {SCRAPY_PROJECT_PATH}")
        return

    i = 0
    while True:
        i += 1
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y-%m-%d_%H-%M-%S")
        temp_file = os.path.join(OUTPUT_DIR, f"temp_scraping_{i}.json")
        
        print(f"\n=== CYCLE {i} DÉMARRÉ : {timestamp} ===")
        
        # --- ÉTAPE 1 : SCRAPING ---
        print("1. [En cours] Scraping Yahoo Finance...")
        try:
            subprocess.run(
                ["scrapy", "crawl", PATH_SCRAPY_SPIDER, "-O", temp_file],
                cwd=SCRAPY_PROJECT_PATH, 
                check=True
            )
        except subprocess.CalledProcessError:
            print("Erreur Scrapy. On passe au cycle suivant.")
            time.sleep(60)
            continue

        # --- ÉTAPE 2 : FUSION & DÉDUPLICATION ---
        print("2. [En cours] Fusion dans l'historique global...")
        new_items_count = 0
        
        # Chargement du fichier temp s'il existe
        new_data = []
        if os.path.exists(temp_file):
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
            except: pass
            if isinstance(new_data, dict): new_data = [new_data]
        
        # Chargement du fichier global existant
        all_data = []
        if os.path.exists(FILE_RAW_GLOBAL):
            with open(FILE_RAW_GLOBAL, 'r', encoding='utf-8') as f:
                try: all_data = json.load(f)
                except: all_data = []
                
        articles_dict = {}

        # 1. Remplissage du dictionnaire avec l'historique existant
        for item in all_data:
            link = item.get(UNIQUE_KEY)
            if link:
                # Nettoyage : on enlève tout ce qu'il y a après le '?' (tracking)
                clean_link = link.split('?')[0].strip().rstrip('/')
                articles_dict[clean_link] = item

        # 2. Ajout des nouveaux artiles
        for article in new_data:
            link = article.get(UNIQUE_KEY)
            if link:
                clean_link = link.split('?')[0].strip().rstrip('/')
                
                if clean_link not in articles_dict:
                    articles_dict[clean_link] = article
                    new_items_count += 1
                else:
                    pass

        # 3. Reconversion du dictionnaire en liste pour le JSON final
        all_data = list(articles_dict.values())
        
        # --- FIN CORRECTION ---

        # Sauvegarde du RAW global
        if new_items_count > 0 or not os.path.exists(FILE_RAW_GLOBAL):
            with open(FILE_RAW_GLOBAL, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=4, ensure_ascii=False)
        
        # Nettoyage
        if os.path.exists(temp_file): os.remove(temp_file)
        
        print(f"   -> {new_items_count} nouveaux articles ajoutés.")

        # --- ÉTAPE 3 : ANALYSE DE SENTIMENT ---
        print("3. [En cours] Exécution de SentimentAnalyzer...")
        
        try:
            # A. Analyse fichier par fichier 
            articles = analyzer.analyze_json_file(FILE_RAW_GLOBAL, FILE_FINAL_SENTIMENT)
            
            # B. Agrégation
            company_scores = analyzer.aggregate_sentiment_by_company(articles)

            print(" Analyse terminée. Scores actuels :")
            for company, score in company_scores.items():
                print(f"   - {company} : {score:.3f}")
            
            print(f"   -> Fichier mis à jour : {FILE_FINAL_SENTIMENT}")

        except Exception as e:
            print(f" Erreur dans l'analyseur de sentiment : {e}")

        # --- ÉTAPE 4 : ATTENTE ---
        elapsed = (datetime.now() - start_time).total_seconds()
        sleep_time = max(0, 3600 - elapsed)
        print(f"=== CYCLE TERMINÉ. Pause de {int(sleep_time/60)} minutes... ===\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_pipeline()