import os
import time
import json
from datetime import datetime

# --- 1. CORRECTION DU CHEMIN (Pour que Scrapy trouve le projet) ---
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # On suppose que le script est dans 'outputs/', donc on remonte d'un cran
    project_root = os.path.dirname(script_dir) 
    os.chdir(project_root)
    print(f"Dossier de travail : {os.getcwd()}")
except:
    pass # Si jamais on lance le script depuis la racine, on ignore
# ------------------------------------------------------------------

os.makedirs("outputs", exist_ok=True)

global_file = "outputs/global_news.json"
# IMPORTANT : Remplace 'link' par le nom du champ qui contient l'URL dans ton JSON
# Si tes articles ont un champ "url", mets UNIQUE_KEY = "url"
UNIQUE_KEY = "link" 

# Initialisation
if not os.path.exists(global_file):
    with open(global_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

i = 0

while True:
    i += 1
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_output_file = f"outputs/news_{i}.json"
    
    print(f"=== SCRAPING {i} : YAHOO FINANCE ({timestamp}) ===")
    
    # 1. Scraping
    exit_code = os.system(f"scrapy crawl yahoo_news -O {current_output_file}")
    
    # 2. Synchronisation intelligente (sans doublons)
    if exit_code == 0 and os.path.exists(current_output_file):
        try:
            # A. Charger les NOUVEAUX articles
            with open(current_output_file, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
            
            # Normaliser en liste (au cas où scrapy sort un seul objet)
            if isinstance(new_data, dict):
                new_data = [new_data]

            if new_data:
                print(f" -> {len(new_data)} articles récupérés. Vérification des doublons...")

                # B. Charger l'HISTORIQUE global
                with open(global_file, 'r', encoding='utf-8') as f:
                    try:
                        all_data = json.load(f)
                    except json.JSONDecodeError:
                        all_data = []
                
                # C. Créer un index des articles existants pour aller vite
                # On stocke toutes les URLs déjà présentes dans un "set"
                existing_ids = set()
                for article in all_data:
                    if UNIQUE_KEY in article:
                        existing_ids.add(article[UNIQUE_KEY])
                
                # D. Filtrage et Ajout
                added_count = 0
                for article in new_data:
                    # On récupère l'identifiant (URL) du nouvel article
                    article_id = article.get(UNIQUE_KEY)
                    
                    # Si l'article a un lien ET que ce lien n'est pas déjà connu
                    if article_id and article_id not in existing_ids:
                        all_data.append(article)
                        existing_ids.add(article_id) # On l'ajoute au set pour ne pas l'ajouter 2 fois si le scraping a des doublons internes
                        added_count += 1
                
                # E. Sauvegarde uniquement si on a ajouté quelque chose
                if added_count > 0:
                    with open(global_file, 'w', encoding='utf-8') as f:
                        json.dump(all_data, f, indent=4, ensure_ascii=False)
                    print(f" -> {added_count} nouveaux articles ajoutés au fichier global (Doublons ignorés).")
                else:
                    print(" -> Aucun nouvel article (tous sont déjà dans l'historique).")
            else:
                print(" -> Fichier scraping vide.")

        except Exception as e:
            print(f"ERREUR lors de la synchronisation : {e}")
    else:
        print("Erreur Scrapy ou fichier introuvable.")
    
    print("Waiting 1 hour...")
    time.sleep(3600)