import os
import sys
import subprocess

# Fonction pour nettoyer le terminal (optionnel)
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_scraper():
    print("\n" + "="*50)
    print("🚀 1. LANCEMENT DU SCRAPER (Récupération des news)")
    print("="*50)
    
    # Chemin vers le fichier du spider Scrapy
    spider_path = os.path.join("Model", "yahoo_scraper", "yahoo_scraper", "spiders", "yahoo_news.py")
    
    # Fichier de sortie
    output_file = os.path.join("outputs", "news.json")
    
    if not os.path.exists(spider_path):
        print(f"❌ ERREUR : Spider introuvable ici : {spider_path}")
        return False

    # Commande : scrapy runspider ... -O outputs/news.json
    try:
        subprocess.run(["scrapy", "runspider", spider_path, "-O", output_file], check=True)
        print(f"✅ Scraping terminé. Données brutes dans : {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur pendant le scraping : {e}")
        return False

def run_analysis():
    print("\n" + "="*50)
    print("🧠 2. LANCEMENT DE L'IA (Analyse de sentiment)")
    print("="*50)
    
    # On ajoute le dossier courant pour que Python trouve le Controller
    sys.path.append(os.getcwd())
    
    try:
        from Controller.main import main as controller_main
        # On lance la fonction main() du Controller
        controller_main() 
        print("✅ Analyse terminée.")
        return True
    except Exception as e:
        print(f"❌ Erreur pendant l'analyse : {e}")
        return False

def run_view():
    print("\n" + "="*50)
    print("📊 3. LANCEMENT DE L'INTERFACE (UI)")
    print("="*50)
    
    ui_path = os.path.join("View", "UI.py")
    
    # On lance l'UI dans un processus séparé
    subprocess.run([sys.executable, ui_path])

if __name__ == "__main__":
    # Création du dossier outputs s'il n'existe pas
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    # Exécution de la chaîne
    if run_scraper():
        if run_analysis():
            run_view()