import sys
import os
import unittest

# --- GESTION DES IMPORTS (Adapté à la structure de ton camarade) ---
# On récupère le chemin du dossier actuel (tests/integration)
current_dir = os.path.dirname(os.path.abspath(__file__))
# On remonte de 2 crans pour atteindre la racine du projet
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
# -------------------------------------------------------------------

# On importe ta classe DatabaseHandler
# (Assure-toi que le fichier est bien dans Model/database.py)
# On importe directement depuis ton dossier Model qui existe bien
from Model.database import DatabaseHandler

class TestDatabaseFlow(unittest.TestCase):
    """Test d'intégration dédié à la persistance des données (SQLite)"""

    def setUp(self):
        """Avant chaque test : on crée une BDD vierge"""
        self.db_name = "test_integration_db.sqlite"
        self.db = DatabaseHandler(self.db_name)

    def tearDown(self):
        """Après chaque test : on nettoie"""
        self.db.close()
        # On supprime le fichier de test pour ne pas polluer
        db_path = os.path.join(project_root, "outputs", self.db_name)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass # Parfois Windows bloque le fichier, pas grave

    def test_cycle_vie_article(self):
        """Vérifie : Insertion -> Lecture (En attente) -> Update -> Lecture (Fini)"""
        print("\n--- Test Base de Données : Cycle de vie ---")
        
        # 1. Insertion d'un article brut (Scrapping)
        article = {
            "company": "TotalEnergies",
            "title": "Le pétrole monte",
            "publisher": "Reuters",
            "link": "http://test.com/oil",
            "summary": "Résumé...",
            "full_text": "Texte complet de l'article...",
            "time": "2026-01-12",
            # Pas de sentiment au début
        }
        succes = self.db.save_article(article)
        self.assertTrue(succes, "L'article devrait être sauvegardé")

        # 2. Vérification qu'il est 'A_TRAITER'
        pending = self.db.get_pending_articles()
        self.assertEqual(len(pending), 1, "Il devrait y avoir 1 article en attente")
        id_article = pending[0]['id'] # Ou pending[0][0] selon ta version de database.py
        
        print(f"   -> Article récupéré avec ID : {id_article}")

        # 3. Simulation de l'analyse (Update)
        fake_probas = {"positif": 0.8, "négatif": 0.1, "neutre": 0.1}
        self.db.update_sentiment(id_article, "positif", 0.8, fake_probas)

        # 4. Vérification qu'il n'est plus en attente
        pending_after = self.db.get_pending_articles()
        self.assertEqual(len(pending_after), 0, "La liste d'attente devrait être vide")

        # 5. Vérification des données finales
        all_articles = self.db.fetch_all_articles()
        saved_article = next(a for a in all_articles if a['id'] == id_article)
        
        self.assertEqual(saved_article['sentiment_label'], "positif")
        self.assertEqual(saved_article['status'], "TRAITE")
        print("   -> Cycle complet validé ✅")

if __name__ == '__main__':
    unittest.main()