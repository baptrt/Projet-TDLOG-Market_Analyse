import sys
import os
import unittest
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
# Ajoute la racine du projet pour les imports.

from infrastructure.database.repository import DatabaseRepository

class TestDatabaseFlow(unittest.TestCase):
    """Test d'intégration dédié à la persistance des données (SQLite)."""

    def setUp(self):
        """Avant chaque test : on crée une BDD vierge."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        self.db_name = os.path.basename(temp_db.name)
        self.db = DatabaseRepository(db_name=self.db_name)
        os.unlink(temp_db.name)

    def tearDown(self):
        """Après chaque test : on nettoie."""
        db_path = os.path.join(project_root, "data", self.db_name)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass

    def test_cycle_vie_article(self):
        """Vérifie : Insertion -> Lecture -> Update -> Lecture."""
        print("\n--- Test Base de Données : Cycle de vie ---")
        
        article = {
            "company": "TotalEnergies",
            "title": "Le pétrole monte",
            "publisher": "Reuters",
            "link": "http://test.com/oil",
            "summary": "Résumé...",
            "full_text": "Texte complet de l'article...",
            "time": "2026-01-12",
        }
        success = self.db.save_article(article)
        self.assertTrue(success, "L'article devrait être sauvegardé")

        all_articles = self.db.fetch_all_articles()
        self.assertEqual(len(all_articles), 1, "Il devrait y avoir 1 article")
        id_article = all_articles[0]['id']
        
        print(f"   -> Article récupéré avec ID : {id_article}")

        fake_probas = {"positif": 0.8, "négatif": 0.1, "neutre": 0.1}
        updated = self.db.update_sentiment(id_article, "positif", 0.8, fake_probas)
        self.assertTrue(updated, "La mise à jour du sentiment doit réussir")

        saved_article = next(a for a in self.db.fetch_all_articles() if a['id'] == id_article)
        
        self.assertEqual(saved_article['sentiment_label'], "positif")
        self.assertAlmostEqual(saved_article['sentiment_score'], 0.8, places=2)
        print("   -> Cycle complet validé")

if __name__ == '__main__':
    unittest.main()
