import sys
import os
from PyQt6 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# --- IMPORT SQL (NOUVEAU) ---
# On ajoute le dossier parent au chemin pour trouver Model
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Model.database import DatabaseHandler
# ----------------------------

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
        if not scores:
            return

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

class ChartWindow(QtWidgets.QDialog):
    """Fenêtre séparée pour afficher le diagramme à barres."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagramme des sentiments")
        self.resize(700, 500)

        layout = QtWidgets.QVBoxLayout(self)

        self.chart = SentimentBarChart()
        layout.addWidget(self.chart)

        # Mettre le graphique à jour
        self.chart.update_chart(data)

        close_button = QtWidgets.QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


class NewsViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("News Viewer (SQL Edition)")
        self.resize(1000, 600)

        # =======================================================
        # CONNEXION À LA BASE DE DONNÉES (REMPLACE LE JSON)
        # =======================================================
        try:
            db = DatabaseHandler()
            self.data = db.fetch_all_articles()
            db.close()
            print(f"Chargé {len(self.data)} articles depuis la base de données.")
        except Exception as e:
            print(f"Erreur de connexion BDD : {e}")
            self.data = []
        # =======================================================

        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        self.open_button = QtWidgets.QPushButton("Ouvrir l'article")
        self.open_button.setEnabled(False)

        self.company_filter = QtWidgets.QComboBox()
        self.company_filter.addItem("Toutes les entreprises")
        
        # On récupère la liste unique des entreprises
        if self.data:
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

            # Gestion des scores qui pourraient être None
            score = item.get('sentiment_score', 0.0)
            sentiment_text = f"{item['sentiment_label'].capitalize()} ({score:.2f})"
            sentiment_item = QtWidgets.QTableWidgetItem(sentiment_text)

            label = item.get('sentiment_label', 'neutre').lower()
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
        score = item.get('sentiment_score', 0.0)
        
        text = (f"{item['title']}\n\n{item['summary']}\n\n"
                f"Sentiment : {item['sentiment_label'].capitalize()} "
                f"(score = {score:.2f})\n\n"
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
        """Ouvre la fenêtre contenant le diagramme à barres."""
        if not hasattr(self, "filtered_data") or not self.filtered_data:
            return

        chart_win = ChartWindow(self.filtered_data, self)
        chart_win.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Plus besoin de passer le fichier JSON en argument
    viewer = NewsViewer()
    viewer.show()
    sys.exit(app.exec())