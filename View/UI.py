import json
import os
import sys
import datetime
from PyQt6 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class SentimentBarChart(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 4))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

    def update_chart(self, data):
        scores = {}

        for item in data:
            company = item["company"]
            probas = item["sentiment_probas"]

            # Score cohérent basé sur toutes les probabilités
            sentiment_value = (
                -1 * probas["négatif"]
                + 0 * probas["neutre"]
                + 1 * probas["positif"]
            )

            scores.setdefault(company, []).append(sentiment_value)

        # Moyenne réelle du sentiment
        avg_scores = {k: sum(v) / len(v) for k, v in scores.items()}

        self.ax.clear()

        companies = list(avg_scores.keys())
        values = list(avg_scores.values())

        colors = [
            "green" if s > 0.2 else "yellow" if -0.2 <= s <= 0.2 else "red"
            for s in values
        ]

        self.ax.bar(companies, values, color=colors)
        self.ax.set_ylim(-1, 1)
        self.ax.set_ylabel("Sentiment moyen (pondéré)")
        self.ax.set_title("Sentiment par entreprise (moyenne pondérée)")

        self.fig.tight_layout()
        self.draw()

class SentimentEvolutionChart(FigureCanvasQTAgg):
    """Graphique linéaire pour l'évolution du sentiment dans le temps."""
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 5))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

    def update_chart(self, history_file):
        # Vérification si le fichier existe
        if not os.path.exists(history_file):
            self.ax.clear()
            self.ax.text(0.5, 0.5, "Pas d'historique disponible", 
                         ha='center', va='center', transform=self.ax.transAxes)
            self.draw()
            return

        # Chargement des données
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        except Exception as e:
            print(f"Erreur lecture historique: {e}")
            return

        if not history_data:
            return

        # Restructuration des données : { "Apple": [(date, score), ...], ... }
        company_series = {}
        
        for entry in history_data:
            dt_str = entry["timestamp"]
            # Conversion string -> datetime (Format: 2026-01-04 17:32:31)
            try:
                dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fallback si le format diffère légèrement (ex: avec _ au lieu d'espace)
                try: dt_obj = datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
                except: continue

            scores = entry["scores"]
            
            for company, score in scores.items():
                company_series.setdefault(company, []).append((dt_obj, score))

        self.ax.clear()

        # Tracer une ligne par entreprise
        for company, points in company_series.items():
            # Trier par date pour être sûr que la ligne est droite
            points.sort(key=lambda x: x[0])
            
            if points:
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                self.ax.plot(xs, ys, marker='o', markersize=4, label=company)

        # Mise en forme du graphique
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_ylabel("Sentiment Moyen")
        self.ax.set_title("Évolution du Sentiment (Temps Réel)")
        
        # Formatage des dates sur l'axe X (Heure:Minute)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.fig.autofmt_xdate() # Rotation des dates pour lisibilité

        self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Ajustement pour que la légende ne soit pas coupée
        self.fig.tight_layout()
        self.draw()

class ChartWindow(QtWidgets.QDialog):
    """Fenêtre affichant les graphiques (Barres et Courbes) avec des onglets."""
    def __init__(self, current_data, history_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyse des Sentiments")
        self.resize(900, 600)

        layout = QtWidgets.QVBoxLayout(self)

        # Création des onglets
        tabs = QtWidgets.QTabWidget()
        
        # --- Onglet 1 : Vue Globale (Barres) ---
        self.tab_bar = QtWidgets.QWidget()
        layout_bar = QtWidgets.QVBoxLayout(self.tab_bar)
        self.bar_chart = SentimentBarChart()
        layout_bar.addWidget(self.bar_chart)
        # Mise à jour du diagramme à barres (données actuelles filtrées)
        self.bar_chart.update_chart(current_data)
        tabs.addTab(self.tab_bar, "Moyenne Actuelle")

        # --- Onglet 2 : Tendance (Courbes) ---
        self.tab_line = QtWidgets.QWidget()
        layout_line = QtWidgets.QVBoxLayout(self.tab_line)
        self.line_chart = SentimentEvolutionChart()
        layout_line.addWidget(self.line_chart)
        # Mise à jour de la courbe (fichier historique)
        self.line_chart.update_chart(history_path)
        tabs.addTab(self.tab_line, "Évolution Temporelle")

        layout.addWidget(tabs)

        close_button = QtWidgets.QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

class NewsViewer(QtWidgets.QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.setWindowTitle("News Viewer")
        self.resize(1000, 600)

        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        self.open_button = QtWidgets.QPushButton("Ouvrir l'article")
        self.open_button.setEnabled(False)

        self.company_filter = QtWidgets.QComboBox()
        self.company_filter.addItem("Toutes les entreprises")
        companies = sorted(set(item["company"] for item in self.data))
        self.company_filter.addItems(companies)

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText(" Rechercher dans les titres ou résumés...")

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Entreprise", "Titre", "Source", "Date", "Sentiment"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.sentiment_filter = QtWidgets.QComboBox()
        self.sentiment_filter.addItems(["Tous", "Positif", "Neutre", "Négatif"])

        # BOUTON POUR OUVRIR LA FENÊTRE DE GRAPHIQUE
        self.chart_button = QtWidgets.QPushButton("Afficher le diagramme des sentiments")
        self.chart_button.clicked.connect(self.open_chart_window)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(QtWidgets.QLabel("Filtrer par entreprise :"))
        top_layout.addWidget(self.company_filter)
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(QtWidgets.QLabel("Filtrer par sentiment :"))
        top_layout.addWidget(self.sentiment_filter)

        detail_layout = QtWidgets.QVBoxLayout()
        detail_layout.addWidget(QtWidgets.QLabel("Résumé de l'article :"))
        detail_layout.addWidget(self.summary)
        detail_layout.addWidget(self.open_button)
        detail_layout.addWidget(self.chart_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(detail_layout)

        self.company_filter.currentIndexChanged.connect(self.update_table)
        self.search_box.textChanged.connect(self.update_table)
        self.sentiment_filter.currentIndexChanged.connect(self.update_table)
        self.table.itemSelectionChanged.connect(self.show_summary)
        self.open_button.clicked.connect(self.show_article)

        self.update_table()

    def update_table(self):
        company = self.company_filter.currentText()
        query = self.search_box.text().lower()
        sentiment = self.sentiment_filter.currentText().lower()

        filtered = []
        for item in self.data:
            if company != "Toutes les entreprises" and item["company"] != company:
                continue
            if query and query not in item["title"].lower() and query not in item["summary"].lower():
                continue
            if sentiment != "tous" and item["sentiment_label"].lower() != sentiment:
                continue
            filtered.append(item)

        self.filtered_data = filtered

        self.table.setRowCount(0)
        self.summary.clear()
        self.open_button.setEnabled(False)

        self.table.setRowCount(len(filtered))
        for row, item in enumerate(filtered):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("company", "")))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("title", "")))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("publisher", "")))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("time", "")))

            sentiment_text = f"{item['sentiment_label'].capitalize()} ({item['sentiment_score']:.2f})"
            sentiment_item = QtWidgets.QTableWidgetItem(sentiment_text)

            label = item['sentiment_label'].lower()
            if label == "positif":
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.green)
            elif label == "négatif":
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.red)
            else:
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.yellow)

            self.table.setItem(row, 4, sentiment_item)

    def show_summary(self):
        selected = self.table.currentRow()
        if selected < 0:
            return

        item = self.filtered_data[selected]
        text = (f"{item['title']}\n\n{item['summary']}\n\n"
                f"Sentiment : {item['sentiment_label'].capitalize()} "
                f"(score = {item['sentiment_score']:.2f})\n\n"
                f"Source : {item['publisher']}\nDate : {item['time']}")
        self.summary.setText(text)

        self.current_item = item
        self.open_button.setEnabled(True)

    def show_article(self):
        if not hasattr(self, "current_item"):
            return

        item = self.current_item
        full_text = item.get("full_text", "Texte complet non disponible.")

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(item["title"])
        dialog.resize(800, 600)

        layout = QtWidgets.QVBoxLayout(dialog)

        header = QtWidgets.QLabel(f"<b>{item['title']}</b><br>{item['publisher']} — {item['time']}")
        header.setWordWrap(True)

        text_box = QtWidgets.QTextEdit()
        text_box.setReadOnly(True)
        text_box.setPlainText(full_text)

        close_button = QtWidgets.QPushButton("Fermer")
        close_button.clicked.connect(dialog.close)

        layout.addWidget(header)
        layout.addWidget(text_box)
        layout.addWidget(close_button)

        dialog.exec()

    def open_chart_window(self):
        """Ouvre la fenêtre contenant les diagrammes."""
        if not hasattr(self, "filtered_data"):
            return

        # Chemin vers ton fichier d'historique (adapte si besoin)
        history_file = "Outputs/trend_history.json"
        
        # On passe maintenant filtered_data ET history_file
        chart_win = ChartWindow(self.filtered_data, history_file, self)
        chart_win.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = NewsViewer("Outputs/articles_with_sentiment.json")
    viewer.show()
    sys.exit(app.exec())