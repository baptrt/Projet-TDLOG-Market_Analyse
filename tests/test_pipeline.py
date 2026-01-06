# tests/integration/test_pipeline.py

import unittest
import json
import os
from pathlib import Path

from app.orchestrator import MarketSentimentOrchestrator

class TestPipelineIntegration(unittest.TestCase):
    """Tests d'intégration du pipeline complet."""
    
    @classmethod
    def setUpClass(cls):
        """Initialise l'orchestrateur."""
        cls.orchestrator = MarketSentimentOrchestrator()
        cls.test_data_path = Path("tests/data/test_articles.json")
    
    def test_pipeline_complet(self):
        """
        Test du pipeline de bout en bout.
        
        Vérifie : Chargement → Analyse → Agrégation
        """
        # Chargement des données de test
        self.assertTrue(self.test_data_path.exists(), "Fichier de test manquant")
        
        # Exécution du pipeline
        result = self.orchestrator.run_analysis_pipeline(
            input_json_path=str(self.test_data_path),
            output_json_path=None  # Pas de sauvegarde pour le test
        )
        
        # Vérifications
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0, "Aucune entreprise analysée")
        
        # Tous les scores doivent être entre -1 et +1
        for company, score in result.items():
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)
            print(f"✓ {company}: {score:+.3f}")


if __name__ == '__main__':
    unittest.main()