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

        # Widgets principaux
        self.company_filter = QtWidgets.QComboBox()
        self.company_filter.addItem("Toutes les entreprises")

        # Extraire les noms uniques d'entreprises
        companies = sorted(set(item["company"] for item in self.data))
        self.company_filter.addItems(companies)

        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText(" Rechercher dans les titres ou résumés...")

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Entreprise", "Titre", "Source", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Panneau de détails
        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        self.open_button = QtWidgets.QPushButton("Ouvrir l'article")
        self.open_button.setEnabled(False)

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

        # Connexions
        self.company_filter.currentIndexChanged.connect(self.update_table)
        self.search_box.textChanged.connect(self.update_table)
        self.table.itemSelectionChanged.connect(self.show_summary)
        self.open_button.clicked.connect(self.open_link)

        # Données initiales
        self.update_table()

    def update_table(self):
        """Met à jour la table selon les filtres."""
        company = self.company_filter.currentText()
        query = self.search_box.text().lower()

        filtered = []
        for item in self.data:
            if company != "Toutes les entreprises" and item["company"] != company:
                continue
            if query and query not in item["title"].lower() and query not in item["summary"].lower():
                continue
            filtered.append(item)

        self.table.setRowCount(len(filtered))
        for row, item in enumerate(filtered):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item["company"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["title"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(item["publisher"]))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(item["time"]))

        self.filtered_data = filtered
        self.summary.clear()
        self.open_button.setEnabled(False)

    def show_summary(self):
        """Affiche le résumé de l'article sélectionné."""
        selected = self.table.currentRow()
        if selected < 0:
            return

        item = self.filtered_data[selected]
        text = f"📰 {item['title']}\n\n{item['summary']}\n\nSource : {item['publisher']}\nDate : {item['time']}"
        self.summary.setText(text)
        self.current_link = item["link"]
        self.open_button.setEnabled(True)

    def open_link(self):
        """Ouvre le lien de l'article dans le navigateur."""
        if hasattr(self, "current_link"):
            webbrowser.open(self.current_link)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    viewer = NewsViewer("news.json")  
    viewer.show()
    sys.exit(app.exec())

