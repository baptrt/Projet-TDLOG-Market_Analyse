# run.py - Point d'entrée unique du projet

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# Import des composants
from mvc.views.main_window import MainWindow
from mvc.controllers.main_controller import MainController
from infrastructure.database.repository import DatabaseRepository
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
