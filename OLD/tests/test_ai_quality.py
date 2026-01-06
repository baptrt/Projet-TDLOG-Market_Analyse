import unittest
import sys
import os

# --- BLOC MAGIQUE POUR LES IMPORTS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
# -------------------------------------

from Controller.sentiment import SentimentAnalyzer

class TestAIQuality(unittest.TestCase):
    """
    Ce test vérifie que l'IA ne répond pas au hasard.
    On lui donne des phrases dont la réponse est évidente (Sanity Check).
    """

    @classmethod
    def setUpClass(cls):
        print("\n[INFO] Chargement du modèle FinBERT pour le test de QI...")
        # On charge le modèle une seule fois pour tous les tests (gain de temps)
        cls.analyzer = SentimentAnalyzer()

    def test_phrase_evidente_positive(self):
        """Test : Une phrase géniale doit être positive."""
        text = "Tesla profits are skyrocketing, amazing earnings report! Best year ever."
        
        label, score, _ = self.analyzer.analyze_article(text)
        
        print(f"\nTest Positif -> Label trouvé : {label} (Confiance : {score:.2f})")
        
        self.assertEqual(label, "positif", "ERREUR : L'IA aurait dû trouver ça positif !")
        self.assertGreater(score, 0.7, "ERREUR : L'IA devrait être très sûre d'elle (> 70%).")

    def test_phrase_evidente_negative(self):
        """Test : Une phrase horrible doit être négative."""
        text = "Apple is facing bankruptcy, huge losses and the CEO is fired. Disaster."
        
        label, score, _ = self.analyzer.analyze_article(text)
        
        print(f"Test Négatif -> Label trouvé : {label} (Confiance : {score:.2f})")
        
        self.assertEqual(label, "négatif", "ERREUR : L'IA aurait dû trouver ça négatif !")

    def test_phrase_evidente_neutre(self):
        """Test : Une phrase factuelle doit être neutre."""
        text = "Apple creates smartphones and computers. The headquarters are in California."
        
        label, score, _ = self.analyzer.analyze_article(text)
        
        print(f"Test Neutre  -> Label trouvé : {label} (Confiance : {score:.2f})")
        
        self.assertEqual(label, "neutre", "ERREUR : L'IA aurait dû trouver ça neutre (c'est un fait).")

if __name__ == '__main__':
    unittest.main()