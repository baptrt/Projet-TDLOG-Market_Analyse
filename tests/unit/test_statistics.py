# tests/unit/test_statistics.py

import unittest
from domain.services.aggregator import SentimentAggregator
from domain.entities.article import Article

class TestStatisticalAnalysis(unittest.TestCase):
    """Tests des analyses statistiques de base."""
    
    def setUp(self):
        """Prépare des données de test."""
        self.aggregator = SentimentAggregator()
        
        # Ensemble d'articles variés
        self.articles = [
            # Tesla : 3 positifs, 1 négatif
            Article("Article 1", "Content", "Tesla", "CNBC", 
                   sentiment_label="positif", sentiment_score=0.9),
            Article("Article 2", "Content", "Tesla", "CNBC",
                   sentiment_label="positif", sentiment_score=0.85),
            Article("Article 3", "Content", "Tesla", "CNBC",
                   sentiment_label="positif", sentiment_score=0.8),
            Article("Article 4", "Content", "Tesla", "CNBC",
                   sentiment_label="négatif", sentiment_score=0.7),
            
            # Apple : équilibré
            Article("Article 5", "Content", "Apple", "Reuters",
                   sentiment_label="positif", sentiment_score=0.8),
            Article("Article 6", "Content", "Apple", "Reuters",
                   sentiment_label="négatif", sentiment_score=0.8),
        ]
    
    def test_moyenne_sentiments(self):
        """Test : Calcul de la moyenne des sentiments."""
        result = self.aggregator.aggregate_by_company(self.articles)
        
        # Tesla devrait avoir un score positif
        self.assertGreater(result["Tesla"], 0,
                          "Tesla a plus d'articles positifs")
        
        # Apple devrait être proche de 0 (équilibré)
        self.assertAlmostEqual(result["Apple"], 0.0, places=1,
                              msg="Apple devrait être neutre (équilibré)")
    
    def test_volatilite_sentiments(self):
        """Test : Mesurer la volatilité (écart-type)."""
        stats = self.aggregator.get_detailed_stats(self.articles)
        
        # Tesla : forte variation (3 positifs, 1 négatif)
        tesla_stats = stats["Tesla"]
        self.assertEqual(tesla_stats["positive"], 3)
        self.assertEqual(tesla_stats["negative"], 1)
        
        # Apple : variation modérée (équilibré)
        apple_stats = stats["Apple"]
        self.assertEqual(apple_stats["positive"], 1)
        self.assertEqual(apple_stats["negative"], 1)
    
    def test_distribution_sentiments(self):
        """Test : Analyser la distribution des sentiments."""
        stats = self.aggregator.get_detailed_stats(self.articles)
        
        for company, company_stats in stats.items():
            total = company_stats["total_articles"]
            pos = company_stats["positive"]
            neu = company_stats["neutral"]
            neg = company_stats["negative"]
            
            # La somme doit égaler le total
            self.assertEqual(pos + neu + neg, total,
                           f"Distribution incorrecte pour {company}")
            
            # Aucune valeur négative
            self.assertGreaterEqual(pos, 0)
            self.assertGreaterEqual(neu, 0)
            self.assertGreaterEqual(neg, 0)
    
    def test_score_range(self):
        """Test : Tous les scores doivent être entre -1 et +1."""
        result = self.aggregator.aggregate_by_company(self.articles)
        
        for company, score in result.items():
            self.assertGreaterEqual(score, -1.0,
                                  f"{company} : score trop bas")
            self.assertLessEqual(score, 1.0,
                                f"{company} : score trop haut")
    
    def test_comparaison_entreprises(self):
        """Test : Comparer les sentiments entre entreprises."""
        result = self.aggregator.aggregate_by_company(self.articles)
        
        # Tesla (majoritairement positif) > Apple (neutre)
        self.assertGreater(result["Tesla"], result["Apple"],
                          "Tesla devrait être plus positif qu'Apple")


if __name__ == '__main__':
    unittest.main()