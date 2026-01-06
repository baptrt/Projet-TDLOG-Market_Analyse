import json
import os
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from mvc.models.ui_state import UIState
from mvc.views.main_window import MainWindow
from infrastructure.database.repository import DatabaseRepository
from app.pipeline_runner import ContinuousPipelineRunner

# WORKER : L'OUVRIER QUI TRAVAILLE EN ARRIÈRE-PLAN
class ScrapingWorker(QObject):
    """
    Classe dédiée à l'exécution du scraping dans un thread séparé
    pour ne pas geler l'interface graphique.
    """
    finished = pyqtSignal()  # Signal émis quand le travail est fini

    def run(self):
        # Configuration du runner pour un tir unique
        runner = ContinuousPipelineRunner(
            scrapy_project_path="infrastructure/datasources/cnbc_scraper",
            spider_name="cnbc",
            output_dir="outputs"
        )
        # Lancement du scraping (prend du temps)
        runner.run_once()
        # Notification de fin
        self.finished.emit()

# CONTROLEUR PRINCIPAL
class MainController(QObject):
    """
    Contrôleur MVC : Gère l'interaction entre Vue et Modèle.
    """
    
    def __init__(self, view: MainWindow, db_repository: DatabaseRepository):
        super().__init__()
        self.view = view
        self.db_repository = db_repository
        self.ui_state = UIState()
        
        # Chargement initial des données (ce qu'il y a déjà en base)
        self._load_data()
        
        # Connexion des signaux Vue → Contrôleur
        self._connect_view_signals()
        
        # Initialisation de l'affichage
        self._refresh_view()
    
    def _connect_view_signals(self):
        """Connecte les signaux de la Vue aux méthodes du Contrôleur."""
        self.view.filter_changed.connect(self.on_filter_changed)
        self.view.article_selected.connect(self.on_article_selected)
        self.view.open_article_clicked.connect(self.on_open_article_clicked)
        self.view.show_charts_clicked.connect(self.on_show_charts_clicked)
        self.view.refresh_clicked.connect(self.on_refresh_clicked)
    
    # CHARGEMENT DES DONNÉES
    def _load_data(self):
        """Charge les données depuis la base de données vers l'UIState."""
        try:
            # On met à jour le modèle avec les données fraîches de la DB
            self.ui_state.all_articles = self.db_repository.fetch_all_articles()
            self._load_trend_history()
            print(f"[Controller] {len(self.ui_state.all_articles)} articles chargés en mémoire")
        except Exception as e:
            print(f"Erreur chargement : {e}")
            self.ui_state.error_message = str(e)
    
    def _load_trend_history(self):
        """Charge l'historique des tendances depuis le fichier JSON."""
        history_path = "outputs/trend_history.json"
        
        if not os.path.exists(history_path):
            return
        
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                self.ui_state.trend_history = json.load(f)
        except Exception as e:
            print(f"Erreur chargement historique : {e}")
    
    # GESTION DES ÉVÉNEMENTS UI    
    def on_filter_changed(self):
        """Callback : Les filtres ont changé."""
        self.ui_state.selected_company = self.view.company_filter.currentText()
        self.ui_state.search_query = self.view.search_box.text()
        self.ui_state.sentiment_filter = self.view.sentiment_filter.currentText()
        
        self.ui_state.apply_filters()
        self.view.update_table(self.ui_state.filtered_articles)
    
    def on_article_selected(self, row_index: int):
        """Callback : Un article a été sélectionné."""
        if 0 <= row_index < len(self.ui_state.filtered_articles):
            self.ui_state.current_article = self.ui_state.filtered_articles[row_index]
            self.view.show_article_summary(self.ui_state.current_article)
    
    def on_open_article_clicked(self):
        """Callback : Ouverture popup article complet."""
        if self.ui_state.current_article:
            self.view.show_full_article(self.ui_state.current_article)
    
    def on_show_charts_clicked(self):
        """Callback : Affichage des graphiques."""
        self.view.show_charts_dialog(
            self.ui_state.filtered_articles,
            self.ui_state.trend_history
        )
    

    # LOGIQUE DE RAFFRAÎCHISSEMENT (SCRAPING ASYNCHRONE)
    def on_refresh_clicked(self):
        """
        Callback : Bouton 'Rafraîchir' cliqué.
        Lance le scraping dans un thread séparé.
        """
        print("[Controller] Démarrage du processus de rafraîchissement...")
        self.view.show_loading("Recherche de nouveaux articles (CNBC)...")
        
        # 1. Création du Thread et du Worker
        self.thread = QThread()
        self.worker = ScrapingWorker()
        
        # 2. On déplace le worker dans le thread
        self.worker.moveToThread(self.thread)
        
        # 3. Connexions des signaux (Câblage)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 4. Connexion CRUCIALE : Quand c'est fini, on appelle _on_scraping_finished
        self.worker.finished.connect(self._on_scraping_finished)
        
        # 5. Démarrage
        self.thread.start()

    def on_refresh_clicked(self):
        """Lance le scraping."""
        print("[Controller] Démarrage du processus de rafraîchissement...")
        
        # 1. On mémorise le "Plus grand ID" actuel avant de lancer la recherche
        # Si la liste est vide, le max est 0
        if self.ui_state.all_articles:
            self.last_max_id = max(a['id'] for a in self.ui_state.all_articles)
        else:
            self.last_max_id = 0
            
        print(f"[Controller] ID Max avant scraping : {self.last_max_id}")

        self.view.show_loading("Recherche de nouveaux articles...")
        
        # Lancement du Thread (Code identique à avant)
        self.thread = QThread()
        self.worker = ScrapingWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self._on_scraping_finished)
        self.thread.start()
        
    def _on_scraping_finished(self):
        """Appelé quand le scraping est fini."""
        print("[Controller] Scraping terminé.")
        
        # 1. On recharge tout depuis la base (Anciens + Nouveaux)
        self._load_data()
        
        # 2. On identifie les IDs qui sont strictement supérieurs à l'ancien Max
        new_ids = [
            a['id'] for a in self.ui_state.all_articles 
            if a['id'] > self.last_max_id
        ]
        
        self.view.hide_loading()
        
        # 3. Message de statut
        if new_ids:
            self.view.status_label.setText(f"Mise à jour réussie : {len(new_ids)} nouveaux articles !")
        else:
            self.view.status_label.setText("Aucun nouvel article trouvé.")

        # 4. Mise à jour des filtres (pour inclure les nouvelles entreprises éventuelles)
        companies = self.ui_state.get_unique_companies()
        self.view.set_companies(companies)
        
        # 5. On réapplique les filtres actuels 
        self.ui_state.apply_filters()
        
        # 6. On met à jour le tableau en passant la liste des IDs à surligner
        self.view.update_table(self.ui_state.filtered_articles, highlight_ids=new_ids)
        
    def _refresh_view(self):
        """Initialisation de la vue au démarrage."""
        companies = self.ui_state.get_unique_companies()
        self.view.set_companies(companies)
        self.ui_state.apply_filters()
        self.view.update_table(self.ui_state.filtered_articles)