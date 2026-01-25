import sys
import os
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
# Ajoute la racine du projet pour les imports.

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
        db_path = os.path.join(project_root, "outputs", self.db_name)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass

    def test_cycle_vie_article(self):
        """Vérifie : Insertion -> Lecture (En attente) -> Update -> Lecture (Fini)"""
        print("\n--- Test Base de Données : Cycle de vie ---")
        
        # Insertion d'un article sans sentiment.
        article = {
            "company": "TotalEnergies",
            "title": "Le pétrole monte",
            "publisher": "Reuters",
            "link": "http://test.com/oil",
            "summary": "Résumé...",
            "full_text": "Texte complet de l'article...",
            "time": "2026-01-12",
        }
        succes = self.db.save_article(article)
        self.assertTrue(succes, "L'article devrait être sauvegardé")

        # Vérifie l'état "en attente".
        pending = self.db.get_pending_articles()
        self.assertEqual(len(pending), 1, "Il devrait y avoir 1 article en attente")
        id_article = pending[0]['id']
        
        print(f"   -> Article récupéré avec ID : {id_article}")

        # Mise à jour du sentiment.
        fake_probas = {"positif": 0.8, "négatif": 0.1, "neutre": 0.1}
        self.db.update_sentiment(id_article, "positif", 0.8, fake_probas)

        pending_after = self.db.get_pending_articles()
        self.assertEqual(len(pending_after), 0, "La liste d'attente devrait être vide")

        # Vérifie les champs finaux.
        all_articles = self.db.fetch_all_articles()
        saved_article = next(a for a in all_articles if a['id'] == id_article)
        
        self.assertEqual(saved_article['sentiment_label'], "positif")
        self.assertEqual(saved_article['status'], "TRAITE")
        print("   -> Cycle complet validé")

if __name__ == '__main__':
    unittest.main()
