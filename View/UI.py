import json
import sys
import webbrowser
from PyQt6 import QtWidgets, QtCore

class NewsViewer(QtWidgets.QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.setWindowTitle("News Viewer")
        self.resize(1000, 600)

        # Charger le JSON
        with open(json_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        
        # Panneau de détails
        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        self.open_button = QtWidgets.QPushButton("Ouvrir l'article")
        self.open_button.setEnabled(False)
        
        # Extraire les noms uniques d'entreprises
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
        
        # Layout principal
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(QtWidgets.QLabel("Filtrer par entreprise :"))
        top_layout.addWidget(self.company_filter)
        top_layout.addWidget(self.search_box)

        detail_layout = QtWidgets.QVBoxLayout()
        detail_layout.addWidget(QtWidgets.QLabel("Résumé de l'article :"))
        detail_layout.addWidget(self.summary)
        detail_layout.addWidget(self.open_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(detail_layout)

        # Widgets principaux
        self.sentiment_filter = QtWidgets.QComboBox()
        self.sentiment_filter.addItems(["Tous", "Positif", "Neutre", "Négatif"])
        self.sentiment_filter.currentIndexChanged.connect(self.update_table)
        top_layout.addWidget(QtWidgets.QLabel("Filtrer par sentiment :"))
        top_layout.addWidget(self.sentiment_filter)

        # Connexions
        self.company_filter.currentIndexChanged.connect(self.update_table)
        self.search_box.textChanged.connect(self.update_table)
        self.table.itemSelectionChanged.connect(self.show_summary)
        self.open_button.clicked.connect(self.show_article)

        # Données initiales
        self.update_table()

    def update_table(self):
        """Met à jour la table selon les filtres."""
        company = self.company_filter.currentText()
        query = self.search_box.text().lower()
        sentiment = self.sentiment_filter.currentText().lower()

        # Filtrage
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

        # Vider la table
        self.table.setRowCount(0)
        self.summary.clear()
        self.open_button.setEnabled(False)

        # Remplir la table
        self.table.setRowCount(len(filtered))
        for row, item in enumerate(filtered):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item.get("company", "")))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("title", "")))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(item.get("publisher", "")))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(item.get("time", "")))

            sentiment_text = f"{item['sentiment_label'].capitalize()} ({item['sentiment_score']:.2f})"
            sentiment_item = QtWidgets.QTableWidgetItem(sentiment_text)

            # Coloration
            label = item['sentiment_label'].lower()
            if label == "positif":
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.green)
            elif label == "négatif":
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.red)
            else:
                sentiment_item.setBackground(QtCore.Qt.GlobalColor.yellow)

            self.table.setItem(row, 4, sentiment_item)

    def show_summary(self):
        """Affiche le résumé de l'article sélectionné."""
        selected = self.table.currentRow()
        if selected < 0:
            return

        item = self.filtered_data[selected]
        text = f"{item['title']}\n\n{item['summary']}\n\nSource : {item['publisher']}\nDate : {item['time']}"
        self.summary.setText(text)
        self.current_item = item
        self.open_button.setEnabled(True)
        
        text = (f"{item['title']}\n\n{item['summary']}\n\n"
        f"Sentiment : {item['sentiment_label'].capitalize()} "
        f"(score = {item['sentiment_score']:.2f})\n\n"
        f"Source : {item['publisher']}\nDate : {item['time']}")
        self.summary.setText(text)

    def show_article(self):
        """Affiche le texte complet de l'article sélectionné dans une nouvelle fenêtre."""
        if not hasattr(self, "current_item"):
            return

        item = self.current_item
        full_text = item.get("full_text", "Texte complet non disponible.")

        # Création d'une fenêtre modale
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = NewsViewer("articles_with_sentiment.json")  
    viewer.show()
    sys.exit(app.exec())

