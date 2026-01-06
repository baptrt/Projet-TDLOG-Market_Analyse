# tests/unit/test_sentiment_analyzer.py

import unittest
from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.entities.article import Article

class TestSentimentAnalyzer(unittest.TestCase):
    """Tests unitaires du service d'analyse de sentiment."""
    
    @classmethod
    def setUpClass(cls):
        """Charge le modèle une seule fois pour tous les tests."""
        print("\n[INFO] Chargement du modèle FinBERT...")
        cls.analyzer = FinBERTSentimentAnalyzer()
    
    def test_phrase_positive(self):
        """Une phrase clairement positive doit être détectée."""
        text = "Tesla profits are skyrocketing, amazing earnings report! Best year ever."
        result = self.analyzer.analyze_text(text)
        
        print(f"\nTest Positif → {result.label} (Confiance : {result.score:.2f})")
        
        self.assertEqual(result.label, "positif")
        self.assertGreater(result.score, 0.7, "Le modèle devrait être confiant (>70%)")
    
    def test_phrase_negative(self):
        """Une phrase clairement négative doit être détectée."""
        text = "Apple is facing bankruptcy, huge losses. Disaster."
        result = self.analyzer.analyze_text(text)
        
        print(f"Test Négatif → {result.label} (Confiance : {result.score:.2f})")
        
        self.assertEqual(result.label, "négatif")
    
    def test_phrase_neutre(self):
        """Une phrase factuelle doit être neutre."""
        text = "Apple creates smartphones. The headquarters are in California."
        result = self.analyzer.analyze_text(text)
        
        print(f"Test Neutre  → {result.label} (Confiance : {result.score:.2f})")
        
        self.assertEqual(result.label, "neutre")
    
    def test_article_entity(self):
        """Test avec un objet Article complet."""
        article = Article(
            title="Record profits for Tesla",
            content="The company exceeded all expectations with stellar Q4 results.",
            company="TSLA",
            source="CNBC"
        )
        
        analyzed = self.analyzer.analyze_article(article)
        
        self.assertIsNotNone(analyzed.sentiment_label)
        self.assertIsNotNone(analyzed.sentiment_score)
        self.assertIn(analyzed.sentiment_label, ["positif", "neutre", "négatif"])


if __name__ == '__main__':
    unittest.main()