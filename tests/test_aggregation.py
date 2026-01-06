import unittest
import json
import os
import sys



# --- BLOC MAGIQUE POUR LES IMPORTS (Ne touche pas à ça) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
# --------------------------------------------------------

from Controller.sentiment import SentimentAnalyzer

class TestLogicAggregation(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
        self.snapshot_path = os.path.join(current_dir, "data", "snapshot_sentiment.json")

    def test_calcul_moyenne_exacte(self):
        """
        Test Répétable : Vérifie que la moyenne est calculée correctement.
        """
        print("\n[INFO] Exécution du test 'test_calcul_moyenne_exacte'...")
        
        with open(self.snapshot_path, 'r', encoding='utf-8') as f:
            articles_figes = json.load(f)

        resultats = self.analyzer.aggregate_sentiment_by_company(articles_figes)

        # Pour TSLA : (+0.9 + 0.8) / 2 = 0.85 (Attention, j'ai corrigé le calcul de tête)
        # Vérifions les maths de ton fichier snapshot :
        # Si c'est +0.9 et +0.8 -> moyenne 0.85
        # Si c'est +0.9 et -0.8 -> moyenne 0.05
        # Adapte la valeur 0.05 ci-dessous selon ton calcul exact attendu !
        
        self.assertAlmostEqual(resultats["TSLA"], 0.05, places=5, msg="Erreur TSLA")
        self.assertAlmostEqual(resultats["AAPL"], 0.0, places=5, msg="Erreur AAPL")
        
        print("[SUCCÈS] Le calcul est bon.")




if __name__ == '__main__':
    unittest.main()