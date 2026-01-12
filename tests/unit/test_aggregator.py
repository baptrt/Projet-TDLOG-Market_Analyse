# tests/unit/test_aggregator.py

import unittest
from domain.services.aggregator import SentimentAggregator
from domain.entities.article import Article

class TestSentimentAggregator(unittest.TestCase):
    """Tests unitaires de l'agrégateur de sentiments."""
    
    def setUp(self):
        """Initialise l'agrégateur."""
        self.aggregator = SentimentAggregator()
    
    def test_aggregate_simple(self):
        """Test : Agrégation simple avec une entreprise."""
        articles = [
            Article(
                title="Article 1",
                content="Contenu positif",
                company="Tesla",
                source="CNBC",
                sentiment_label="positif",
                sentiment_score=0.9
            ),
            Article(
                title="Article 2",
                content="Contenu négatif",
                company="Tesla",
                source="CNBC",
                sentiment_label="négatif",
                sentiment_score=0.8
            )
        ]
        
        result = self.aggregator.aggregate_by_company(articles)
        
        # Vérifications
        self.assertIn("Tesla", result)
        
        # Score = (1 * 0.9 + (-1) * 0.8) / 2 = 0.05
        self.assertAlmostEqual(result["Tesla"], 0.05, places=2)
    
    def test_aggregate_multiple_companies(self):
        """Test : Agrégation avec plusieurs entreprises."""
        articles = [
            Article(
                title="Article Apple",
                content="Très positif",
                company="Apple",
                source="TechCrunch",
                sentiment_label="positif",
                sentiment_score=0.95
            ),
            Article(
                title="Article Microsoft",
                content="Très négatif",
                company="Microsoft",
                source="Reuters",
                sentiment_label="négatif",
                sentiment_score=0.90
            )
        ]
        
        result = self.aggregator.aggregate_by_company(articles)
        
        # Vérifier les deux entreprises
        self.assertEqual(len(result), 2)
        self.assertIn("Apple", result)
        self.assertIn("Microsoft", result)
        
        # Apple positif, Microsoft négatif
        self.assertGreater(result["Apple"], 0)
        self.assertLess(result["Microsoft"], 0)
    
    def test_aggregate_all_neutral(self):
        """Test : Tous les articles sont neutres."""
        articles = [
            Article(
                title=f"Article {i}",
                content="Contenu neutre",
                company="Google",
                source="Bloomberg",
                sentiment_label="neutre",
                sentiment_score=0.85
            )
            for i in range(5)
        ]
        
        result = self.aggregator.aggregate_by_company(articles)
        
        # Score neutre = 0
        self.assertAlmostEqual(result["Google"], 0.0, places=2)
    
    def test_detailed_stats(self):
        """Test : Statistiques détaillées."""
        articles = [
            Article(
                title="Article 1",
                content="Positif",
                company="Amazon",
                source="WSJ",
                sentiment_label="positif",
                sentiment_score=0.9
            ),
            Article(
                title="Article 2",
                content="Positif aussi",
                company="Amazon",
                source="WSJ",
                sentiment_label="positif",
                sentiment_score=0.85
            ),
            Article(
                title="Article 3",
                content="Négatif",
                company="Amazon",
                source="WSJ",
                sentiment_label="négatif",
                sentiment_score=0.7
            )
        ]
        
        stats = self.aggregator.get_detailed_stats(articles)
        
        # Vérifier structure
        self.assertIn("Amazon", stats)
        amazon_stats = stats["Amazon"]
        
        self.assertEqual(amazon_stats["total_articles"], 3)
        self.assertEqual(amazon_stats["positive"], 2)
        self.assertEqual(amazon_stats["negative"], 1)
        self.assertEqual(amazon_stats["neutral"], 0)
        
        # Score moyen devrait être positif
        self.assertGreater(amazon_stats["avg_sentiment"], 0)
    
    def test_empty_articles(self):
        """Test : Liste vide."""
        result = self.aggregator.aggregate_by_company([])
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()