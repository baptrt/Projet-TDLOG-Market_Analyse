# app/orchestrator.py

import json
from typing import List, Dict
from pathlib import Path

from domain.entities.article import Article
from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.services.aggregator import SentimentAggregator


class MarketSentimentOrchestrator:
    """
    Orchestrateur de l'analyse de sentiment de marché.
    
    Architecture Pipeline :
    1. Chargement des données → 2. Analyse sentiment → 3. Agrégation → 4. Sauvegarde
    
    Cette classe coordonne les différents services sans contenir de logique métier.
    """
    
    def __init__(self):
        """Initialise les services métier."""
        self.sentiment_analyzer = FinBERTSentimentAnalyzer()
        self.aggregator = SentimentAggregator()
    
    def run_analysis_pipeline(
        self, 
        input_json_path: str, 
        output_json_path: str = None
    ) -> Dict[str, float]:
        """
        Exécute le pipeline complet d'analyse.
        
        Pipeline :
        1. Charger articles depuis JSON
        2. Analyser sentiment avec FinBERT
        3. Agréger par entreprise
        4. Sauvegarder résultats
        
        Args:
            input_json_path: Chemin du fichier JSON d'entrée
            output_json_path: Chemin de sortie (optionnel)
        
        Returns:
            Dictionnaire {company: score_moyen}
        """
        print("Démarrage du pipeline d'analyse de sentiment")
        
        # ÉTAPE 1 : Chargement des données
        print("[1/4] Chargement des articles...")
        articles = self._load_articles_from_json(input_json_path)
        print(f" {len(articles)} articles chargés\n")
        
        # ÉTAPE 2 : Analyse de sentiment
        print("[2/4] Analyse de sentiment (FinBERT)...")
        analyzed_articles = self.sentiment_analyzer.analyze_batch(articles)
        print()
        
        # ÉTAPE 3 : Agrégation par entreprise
        print("[3/4] Agrégation des sentiments par entreprise...")
        company_scores = self.aggregator.aggregate_by_company(analyzed_articles)
        print(f" {len(company_scores)} entreprises analysées\n")
        
        # ÉTAPE 4 : Sauvegarde
        if output_json_path:
            print("[4/4] Sauvegarde des résultats...")
            self._save_results(analyzed_articles, output_json_path)
            print(f" Résultats sauvegardés : {output_json_path}\n")

        print("Pipeline terminé avec succès")
        
        return company_scores
    
    def _load_articles_from_json(self, json_path: str) -> List[Article]:
        """
        Charge les articles depuis un fichier JSON.
        
        Couche de transformation : JSON → Entités Article
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        articles = [Article.from_dict(item) for item in data]
        return articles
    
    def _save_results(self, articles: List[Article], output_path: str):
        """Sauvegarde les articles analysés en JSON."""
        output_data = [article.to_dict() for article in articles]
        
        # Créer le dossier si nécessaire
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    def get_detailed_report(self, articles: List[Article]) -> Dict:
        """Génère un rapport détaillé avec statistiques."""
        return self.aggregator.get_detailed_stats(articles)