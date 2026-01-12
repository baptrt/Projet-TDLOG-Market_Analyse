# tests/unit/test_repository.py

import unittest
import os
import tempfile
from infrastructure.database.repository import DatabaseRepository
from domain.entities.article import Article

class TestDatabaseRepository(unittest.TestCase):
    """Tests unitaires du Repository (accès DB)."""
    
    def setUp(self):
        """Crée une DB temporaire pour chaque test."""
        # Fichier temporaire qui sera supprimé après le test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Repository avec DB temporaire
        self.repo = DatabaseRepository(db_name=self.temp_db.name)
    
    def tearDown(self):
        """Nettoie la DB après chaque test."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_save_article_nouveau(self):
        """Test : Sauvegarder un nouvel article."""
        article_dict = {
            "company": "Tesla",
            "title": "Tesla annonce des profits records",
            "content": "L'entreprise dépasse les attentes.",
            "source": "CNBC",
            "link": "https://example.com/article1",
            "published_date": "2024-01-15",
            "sentiment_label": "positif",
            "sentiment_score": 0.95,
            "sentiment_probas": {"positif": 0.95, "neutre": 0.03, "négatif": 0.02}
        }
        
        # Sauvegarder et vérifier que c'est un NOUVEAU article
        result = self.repo.save_article(article_dict)
        self.assertTrue(result, "L'article devrait être nouveau")
        
        # Vérifier que l'article est bien en base
        articles = self.repo.fetch_all_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Tesla annonce des profits records")
    
    def test_save_article_doublon(self):
        """Test : Tenter de sauvegarder un doublon."""
        article_dict = {
            "company": "Apple",
            "title": "Nouvel iPhone lancé",
            "content": "Apple présente son nouveau modèle.",
            "source": "TechCrunch",
            "link": "https://example.com/iphone",
            "published_date": "2024-01-20",
            "sentiment_label": "neutre",
            "sentiment_score": 0.80
        }
        
        # Première sauvegarde
        result1 = self.repo.save_article(article_dict)
        self.assertTrue(result1, "Première insertion OK")
        
        # Deuxième sauvegarde (même link + company = doublon)
        result2 = self.repo.save_article(article_dict)
        self.assertFalse(result2, "Doublon détecté")
        
        # Vérifier qu'il n'y a qu'un seul article
        articles = self.repo.fetch_all_articles()
        self.assertEqual(len(articles), 1)
    
    def test_fetch_all_articles(self):
        """Test : Récupérer tous les articles."""
        # Ajouter plusieurs articles
        for i in range(3):
            self.repo.save_article({
                "company": f"Company{i}",
                "title": f"Article {i}",
                "content": f"Contenu {i}",
                "source": "Test",
                "link": f"https://example.com/article{i}",
                "published_date": "2024-01-10",
                "sentiment_label": "neutre",
                "sentiment_score": 0.5
            })
        
        # Récupérer tous
        articles = self.repo.fetch_all_articles()
        self.assertEqual(len(articles), 3)
    
    def test_fetch_by_company(self):
        """Test : Filtrer par entreprise."""
        # Ajouter articles de différentes entreprises
        companies = ["Tesla", "Apple", "Tesla", "Microsoft"]
        
        for i, company in enumerate(companies):
            self.repo.save_article({
                "company": company,
                "title": f"Article {i}",
                "content": "Contenu",
                "source": "Test",
                "link": f"https://example.com/art{i}",
                "published_date": "2024-01-10",
                "sentiment_label": "positif",
                "sentiment_score": 0.8
            })
        
        # Filtrer Tesla uniquement
        tesla_articles = self.repo.fetch_articles_by_company("Tesla")
        self.assertEqual(len(tesla_articles), 2)
        
        for article in tesla_articles:
            self.assertEqual(article["company"], "Tesla")


if __name__ == '__main__':
    unittest.main()