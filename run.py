# run.py - Point d'entrée unique du projet

import sys
import os
import site
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# --- BLOC DE COMPATIBILITÉ WINDOWS (Invisible pour Mac/Linux) ---
# Ce bloc ne s'exécute QUE si l'ordinateur est un Windows ('nt')
if os.name == 'nt':
    try:
        # Patch pour l'erreur "OpenMP" fréquente sur Windows
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        
        # Patch pour les DLLs Python 3.13 / Torch
        site_packages = site.getsitepackages()
        for p in site_packages:
            candidate = os.path.join(p, 'torch', 'lib')
            if os.path.exists(candidate):
                # 1. Ajout au PATH
                os.environ['PATH'] = candidate + os.pathsep + os.environ['PATH']
                # 2. Ajout sécurisé via os.add_dll_directory
                if hasattr(os, 'add_dll_directory'):
                    try: os.add_dll_directory(candidate)
                    except: pass
                # 3. Pré-chargement des dépendances critiques
                import ctypes
                try:
                    ctypes.cdll.LoadLibrary(os.path.join(candidate, 'c10.dll'))
                    ctypes.cdll.LoadLibrary(os.path.join(candidate, 'torch_cpu.dll'))
                except: pass
                break
    except Exception as e:
        print(f"⚠️ Note compatibilité Windows : {e}")
# -------------------------------------------------------------

# Import des composants (Après le patch !)
from mvc.views.main_window import MainWindow
from mvc.controllers.main_controller import MainController
from infrastructure.database.repository import DatabaseRepository
# (Note: PipelineRunner n'est pas utilisé directement ici, mais l'import ne gêne pas)
from app.pipeline_runner import ContinuousPipelineRunner 

def start_gui():
    """
    Lance l'interface graphique PyQt6.
    """
    print("\n[GUI] Démarrage de l'interface graphique...")
    
    # Création de l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Market Sentiment Analyzer")
    
    # Initialisation MVC
    db_repository = DatabaseRepository()
    view = MainWindow()
    
    # Le contrôleur a besoin de la Vue et du Repository
    controller = MainController(view, db_repository)
    
    # Affichage de la fenêtre
    view.show()
    
    print("[GUI] Interface prête !\n")
    
    # Boucle principale Qt
    sys.exit(app.exec())

def main():
    """
    Point d'entrée principal.
    Mode MANUEL : L'interface commande le scraping.
    """
    print("MARKET SENTIMENT ANALYZER")
    
    # Vérification de la structure
    project_root = Path(__file__).parent
    # Dossier de données persistantes (BDD + historiques)
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    print(f"\n[INIT] Racine du projet : {project_root}")
    print(f"[INIT] Dossier data : {data_dir}")
    
    print("Mode MANUEL activé : Cliquez sur Rafraîchir pour scraper.")
    
    # Démarrage de l'interface graphique uniquement
    start_gui()

if __name__ == "__main__":
    main()
