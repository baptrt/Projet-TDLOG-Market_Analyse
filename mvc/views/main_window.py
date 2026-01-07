from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtGui import QColor
from mvc.views.components.sentiment_bar_chart import SentimentBarChart
from mvc.views.components.sentiment_evolution_chart import SentimentEvolutionChart

class MainWindow(QtWidgets.QWidget):
    """
    Vue MVC : Fenêtre principale de l'application.
    Responsabilité : Affichage uniquement.
    """
    
    # Signaux émis vers le contrôleur
    filter_changed = QtCore.pyqtSignal()
    article_selected = QtCore.pyqtSignal(int)
    open_article_clicked = QtCore.pyqtSignal()
    show_charts_clicked = QtCore.pyqtSignal()
    refresh_clicked = QtCore.pyqtSignal()  
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Sentiment Analyzer")
        self.resize(1000, 600)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Construit l'interface graphique."""
        # Barre de filtres
        filter_layout = QtWidgets.QHBoxLayout()
        
        filter_layout.addWidget(QtWidgets.QLabel("Entreprise :"))
        self.company_filter = QtWidgets.QComboBox()
        filter_layout.addWidget(self.company_filter)
        
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("Rechercher dans les titres...")
        filter_layout.addWidget(self.search_box)
        
        filter_layout.addWidget(QtWidgets.QLabel("Sentiment :"))
        self.sentiment_filter = QtWidgets.QComboBox()
        self.sentiment_filter.addItems(["Tous", "Positif", "Neutre", "Négatif"])
        filter_layout.addWidget(self.sentiment_filter)
        
        # Bouton rafraîchir
        self.refresh_button = QtWidgets.QPushButton("Rafraîchir")
        self.refresh_button.setToolTip("Recharger les articles depuis la base de données")
        filter_layout.addWidget(self.refresh_button)
        
        filter_layout.addStretch()
        
        # Label de statut
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        
        # Tableau des articles
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Date", "Entreprise", "Titre", "Sentiment", "Score de sûreté"
        ])
        # Correction ordre colonnes pour correspondre au header
        
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        
        # Zone de détails
        detail_layout = QtWidgets.QVBoxLayout()
        detail_layout.addWidget(QtWidgets.QLabel("Résumé de l'article :"))
        
        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        detail_layout.addWidget(self.summary)
        
        button_layout = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton("Ouvrir l'article complet")
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        self.chart_button = QtWidgets.QPushButton("Afficher les graphiques")
        button_layout.addWidget(self.chart_button)
        
        detail_layout.addLayout(button_layout)
        
        # Layout principal
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.table)
        main_layout.addLayout(detail_layout)
    
    def _connect_signals(self):
        """Connecte les signaux internes de la Vue."""
        self.company_filter.currentIndexChanged.connect(self.filter_changed.emit)
        self.search_box.textChanged.connect(self.filter_changed.emit)
        self.sentiment_filter.currentIndexChanged.connect(self.filter_changed.emit)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.open_button.clicked.connect(self.open_article_clicked.emit)
        self.chart_button.clicked.connect(self.show_charts_clicked.emit)
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
    
    def _on_selection_changed(self):
        """Gère le changement de sélection dans le tableau."""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.article_selected.emit(selected_row)
            
    # MÉTHODES PUBLIQUES
    def set_companies(self, companies: list):
        """Met à jour la liste des entreprises dans le filtre."""
        self.company_filter.clear()
        self.company_filter.addItem("Toutes les entreprises")
        self.company_filter.addItems(companies)
        
    def update_table(self, articles, highlight_ids=None):
        """
        Affiche les articles dans le tableau avec coloration par SENTIMENT.
        Positif = Vert, Négatif = Rouge, Neutre = Jaune.
        """
        self.table.setRowCount(len(articles))
        self.table.setSortingEnabled(False) # Désactiver le tri pendant l'insertion

        for row_idx, article in enumerate(articles):
            # 1. Remplissage des données
            # Col 0: Date
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(article.get('published_date', 'N/A'))))
            
            # Col 1: Entreprise
            self.table.setItem(row_idx, 1, QTableWidgetItem(article.get('company', 'N/A')))
            
            # Col 2: Titre
            self.table.setItem(row_idx, 2, QTableWidgetItem(article.get('title', 'Sans titre')))
            
            # Col 3: Sentiment
            label = str(article.get('sentiment_label', 'Neutre'))
            self.table.setItem(row_idx, 3, QTableWidgetItem(label))
            
            # Col 4: Score
            score = article.get('sentiment_score', 0)
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{score*100:.2f}%"))
            
            # 2. Gestion des COULEURS (La partie demandée)
            label_lower = label.lower()
            row_color = None
            
            if "positif" in label_lower or "positive" in label_lower:
                # Vert clair (Pastel)
                row_color = QColor(210, 255, 210)
            elif "négatif" in label_lower or "negative" in label_lower:
                # Rouge clair (Pastel)
                row_color = QColor(255, 210, 210)
            else:
                # Jaune clair (Pastel) pour Neutre
                row_color = QColor(255, 255, 224)
            
            # Application de la couleur à toute la ligne
            if row_color:
                for col in range(5):
                    self.table.item(row_idx, col).setBackground(row_color)

        self.table.setSortingEnabled(True)

    def show_article_summary(self, article: dict):
        """Affiche le résumé."""
        score = article.get('sentiment_score', 0.0)
        label = article.get('sentiment_label', 'Inconnu')

        full_content = article.get('content', '') or article.get('full_text', '')
        # Petit résumé maison si pas de summary explicite
        fake_summary = full_content[:300] + "..." if len(full_content) > 300 else full_content
        
        text = (
            f"TITRE : {article.get('title', 'Sans titre')}\n\n"
            f"{fake_summary}\n\n"
            f"SENTIMENT : {str(label).upper()} (Avec {score*100:.2f} % de sureté)\n"
            f"SOURCE : {article.get('source', 'Inconnue')}\n"      
            f"DATE : {article.get('published_date', 'Inconnue')}" 
        )
        
        self.summary.setText(text)
        self.open_button.setEnabled(True)

    def show_full_article(self, article: dict):
        """Affiche l'article complet dans une popup."""
        dialog = QtWidgets.QDialog(self)
        title = article.get("title", "Article")
        dialog.setWindowTitle(title)
        dialog.resize(800, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)

        source = article.get("source", "Source inconnue")
        date = article.get("published_date", "")
        
        header = QtWidgets.QLabel(f"<h2>{title}</h2><p><i>{source} — {date}</i></p>")
        header.setWordWrap(True)
        layout.addWidget(header)
        
        text_box = QtWidgets.QTextEdit()
        text_box.setReadOnly(True)
        # Gestion robuste du contenu (content ou full_text)
        content = article.get("content") or article.get("full_text") or "Contenu non disponible."
        text_box.setPlainText(content)
        layout.addWidget(text_box)
        
        close_button = QtWidgets.QPushButton("Fermer")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def show_charts_dialog(self, filtered_articles: list, trend_history: list):
        """Affiche la fenêtre des graphiques."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Analyse des Sentiments")
        dialog.resize(900, 600)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Onglets
        tabs = QtWidgets.QTabWidget()
        
        # Onglet 1 : Barres
        tab_bar = QtWidgets.QWidget()
        layout_bar = QtWidgets.QVBoxLayout(tab_bar)
        bar_chart = SentimentBarChart()
        bar_chart.update_chart(filtered_articles)
        layout_bar.addWidget(bar_chart)
        tabs.addTab(tab_bar, "Répartition Actuelle")
        
        # Onglet 2 : Évolution
        tab_line = QtWidgets.QWidget()
        layout_line = QtWidgets.QVBoxLayout(tab_line)
        line_chart = SentimentEvolutionChart()
        line_chart.update_chart(trend_history)
        layout_line.addWidget(line_chart)
        tabs.addTab(tab_line, "Historique")
        
        layout.addWidget(tabs)
        
        close_button = QtWidgets.QPushButton("Fermer")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def show_loading(self, message: str = "Chargement..."):
        """Affiche un indicateur de chargement."""
        self.status_label.setText(f"{message}")
        self.refresh_button.setEnabled(False)
        QtWidgets.QApplication.processEvents()
    
    def hide_loading(self):
        """Cache l'indicateur de chargement."""
        self.status_label.setText("")
        self.refresh_button.setEnabled(True)