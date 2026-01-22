# mvc/controllers/main_controller.py

from PyQt6.QtWidgets import QMessageBox
from mvc.models.ui_state import UIState
from mvc.controllers.auth_controller import AuthController
from mvc.views.login_dialog import LoginDialog
import json
from pathlib import Path

class MainController:
    """
    Contrôleur MVC : Gère la logique de l'interface.
    """
    
    def __init__(self, view, db_repository):
        self.view = view
        self.repository = db_repository
        self.ui_state = UIState()
        
        # Contrôleur d'authentification
        self.auth_controller = AuthController()
        
        self._connect_signals()
        
        # Authentification au démarrage
        self._show_login_dialog()
    
    def _connect_signals(self):
        """Connecte les signaux de la Vue aux méthodes du Contrôleur."""
        self.view.filter_changed.connect(self._on_filter_changed)
        self.view.article_selected.connect(self._on_article_selected)
        self.view.open_article_clicked.connect(self._on_open_article)
        self.view.show_charts_clicked.connect(self._on_show_charts)
        self.view.refresh_clicked.connect(self._on_refresh)
        
        # NOUVEAUX SIGNAUX
        self.view.logout_clicked.connect(self._on_logout)
        self.view.toggle_favorite_clicked.connect(self._on_toggle_favorite)
        self.view.show_favorites_only_changed.connect(self._on_favorites_filter_changed)
    
    # === AUTHENTIFICATION ===
    
    def _show_login_dialog(self):
        """Affiche la fenêtre de connexion."""
        self._login_dialog = LoginDialog(self.view)
        
        # Connexion des signaux du dialog
        self._login_dialog.login_successful.connect(self._on_login_attempt)
        self._login_dialog.register_successful.connect(self._on_register_attempt)
        
        result = self._login_dialog.exec()
        
        # Si l'utilisateur ferme sans se connecter
        if result == 0 and not self.auth_controller.is_authenticated():
            QMessageBox.information(
                self.view,
                "Mode Invité",
                "Vous pouvez utiliser l'application sans compte,\nmais les favoris ne seront pas disponibles."
            )
            self._load_initial_data()
    
    def _on_login_attempt(self, username: str, password: str):
        """Gère une tentative de connexion."""
        try:
            success = self.auth_controller.login(username, password)
        except Exception:
            if getattr(self, "_login_dialog", None):
                self._login_dialog.show_error("Erreur lors de la connexion")
            return
        
        if not success:
            if getattr(self, "_login_dialog", None):
                error_msg = self.auth_controller.last_error or "Identifiants incorrects"
                self._login_dialog.show_error(error_msg)
            return
        
        if getattr(self, "_login_dialog", None):
            self._login_dialog.accept()
        
        # Met à jour l'interface
        self.view.set_user(username)
        self._load_initial_data()
        
        QMessageBox.information(
            self.view,
            "Connexion réussie",
            f"Bienvenue {username} !"
        )
    
    def _on_register_attempt(self, username: str, password: str, email: str):
        """Gère une tentative d'inscription."""
        try:
            success = self.auth_controller.register(username, password, email)
        except Exception:
            if getattr(self, "_login_dialog", None):
                self._login_dialog.show_error("Erreur lors de l'inscription")
            return
        
        if not success:
            if getattr(self, "_login_dialog", None):
                error_msg = self.auth_controller.last_error or "Ce nom d'utilisateur existe déjà"
                self._login_dialog.show_error(error_msg)
            return
        
        if getattr(self, "_login_dialog", None):
            self._login_dialog.accept()
        
        # Met à jour l'interface
        self.view.set_user(username)
        self._load_initial_data()
        
        QMessageBox.information(
            self.view,
            "Inscription réussie",
            f"Compte créé avec succès !\nBienvenue {username} !"
        )
    
    def _on_logout(self):
        """Gère la déconnexion."""
        reply = QMessageBox.question(
            self.view,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_controller.logout()
            self.view.clear_user()
            
            # Réinitialise les filtres
            self.ui_state.show_favorites_only = False
            self._apply_filters()
    
    # === GESTION DES FAVORIS ===
    
    def _on_toggle_favorite(self, company: str):
        """Ajoute/retire une entreprise des favoris."""
        if not self.auth_controller.is_authenticated():
            QMessageBox.warning(
                self.view,
                "Connexion requise",
                "Vous devez être connecté pour utiliser les favoris."
            )
            return
        
        is_fav = self.auth_controller.is_favorite(company)
        
        if is_fav:
            self.auth_controller.remove_favorite(company)
            msg = f"'{company}' retiré des favoris"
        else:
            self.auth_controller.add_favorite(company)
            msg = f"'{company}' ajouté aux favoris"
        
        # Rafraîchit l'affichage
        self._apply_filters()
        
        # Notification
        self.view.status_label.setText(msg)
    
    def _on_favorites_filter_changed(self, show_only: bool):
        """Active/désactive le filtre favoris."""
        self.ui_state.show_favorites_only = show_only
        self._apply_filters()
    
    # === LOGIQUE MÉTIER ===
    
    def _load_initial_data(self):
        """Charge les données au démarrage."""
        self.view.show_loading("Chargement des articles...")
        
        all_articles = self.repository.get_all_articles()
        
        if not all_articles:
            self.view.hide_loading()
            QMessageBox.information(
                self.view, 
                "Aucune donnée",
                "Aucun article trouvé.\nCliquez sur 'Rafraîchir' pour lancer le scraping."
            )
            return
        
        self.ui_state.all_articles = all_articles
        
        # Liste des entreprises
        companies = sorted(set(a["company"] for a in all_articles if a.get("company")))
        self.view.set_companies(companies)
        
        self._apply_filters()
        self.view.hide_loading()
    
    def _on_refresh(self):
        """Rafraîchit les données."""
        self.view.show_loading("Chargement des données en cours...")
        
        # Lancement du scraping
        try:
            from app.pipeline_runner import ContinuousPipelineRunner
            runner = ContinuousPipelineRunner()
            result = runner.run_once()
        except Exception as exc:
            self.view.hide_loading()
            QMessageBox.critical(
                self.view,
                "Erreur de scraping",
                f"Le scraping a échoué : {exc}"
            )
            return
        
        # Recharge les données
        self._load_initial_data()
        if result:
            found = result.get("found", 0)
            added = result.get("added", 0)
            self.view.status_label.setText(
                f"Scraping terminé : {found} articles trouvés, {added} ajoutés."
            )
    
    def _apply_filters(self):
        """Applique les filtres et met à jour l'affichage."""
        filtered = self.ui_state.all_articles.copy()
        
        # Filtre entreprise
        selected_company = self.view.company_filter.currentText()
        if selected_company != "Toutes les entreprises":
            filtered = [a for a in filtered if a.get("company") == selected_company]
        
        # Filtre sentiment
        selected_sentiment = self.view.sentiment_filter.currentText()
        if selected_sentiment != "Tous":
            sentiment_map = {
                "Positif": ["positif", "positive"],
                "Neutre": ["neutre", "neutral"],
                "Négatif": ["négatif", "negative"]
            }
            keywords = sentiment_map.get(selected_sentiment, [])
            filtered = [
                a for a in filtered 
                if any(k in str(a.get("sentiment_label", "")).lower() for k in keywords)
            ]
        
        # Filtre recherche
        search_text = self.view.search_box.text().lower()
        if search_text:
            filtered = [
                a for a in filtered
                if search_text in str(a.get("title", "")).lower()
            ]
        
        # Filtre favoris
        user_favorites = []
        if self.auth_controller.is_authenticated():
            user_favorites = self.auth_controller.get_favorites()
            
            if self.ui_state.show_favorites_only and user_favorites:
                filtered = [
                    a for a in filtered
                    if a.get("company") in user_favorites
                ]
        
        self.ui_state.filtered_articles = filtered
        self.view.update_table(filtered, user_favorites=user_favorites)
    
    def _on_filter_changed(self):
        """Réagit aux changements de filtres."""
        self._apply_filters()
    
    def _on_article_selected(self, row_index: int):
        """Gère la sélection d'un article."""
        if 0 <= row_index < len(self.ui_state.filtered_articles):
            article = self.ui_state.filtered_articles[row_index]
            self.ui_state.selected_article = article
            self.view.show_article_summary(article)
    
    def _on_open_article(self):
        """Ouvre l'article complet."""
        if self.ui_state.selected_article:
            self.view.show_full_article(self.ui_state.selected_article)
    
    def _on_show_charts(self):
        """Affiche les graphiques."""
        # Charge l'historique des tendances
        history_path = Path("data/trend_history.json")
        trend_history = []
        
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                trend_history = json.load(f)
        
        user_favorites = []
        if self.auth_controller.is_authenticated():
            user_favorites = self.auth_controller.get_favorites()
        show_only_favorites = self.ui_state.show_favorites_only and user_favorites

        if show_only_favorites:
            filtered_history = []
            for entry in trend_history:
                scores = entry.get("scores", {})
                filtered_scores = {
                    company: score
                    for company, score in scores.items()
                    if company in user_favorites
                }
                if filtered_scores:
                    filtered_history.append({
                        "timestamp": entry.get("timestamp"),
                        "scores": filtered_scores
                    })
            trend_history = filtered_history

        self.view.show_charts_dialog(
            self.ui_state.filtered_articles,
            trend_history
        )
