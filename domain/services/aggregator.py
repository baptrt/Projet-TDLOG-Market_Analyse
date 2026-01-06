# domain/services/aggregator.py

from typing import List, Dict
from collections import defaultdict
from domain.entities.article import Article


class SentimentAggregator:
    """
    Service métier : Agrégation des sentiments par entreprise.
    
    Responsabilité unique : Calculer des scores agrégés.
    """
    
    def aggregate_by_company(self, articles: List[Article]) -> Dict[str, float]:
        """
        Calcule le sentiment moyen par entreprise.
        
        Formule : score_moyen = Σ(sentiment_numérique * confiance) / nb_articles
        
        Args:
            articles: Liste d'articles analysés
        
        Returns:
            Dictionnaire {company: score_moyen}
            Score entre -1 (très négatif) et +1 (très positif)
        """
        # Grouper par entreprise
        companies = self._group_by_company(articles)
        
        # Calculer le score moyen pour chaque entreprise
        results = {}
        for company, company_articles in companies.items():
            results[company] = self._calculate_average_sentiment(company_articles)
        
        return results
    
    def _group_by_company(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """Regroupe les articles par entreprise."""
        companies = defaultdict(list)
        
        for article in articles:
            companies[article.company].append(article)
        
        return dict(companies)
    
    def _calculate_average_sentiment(self, articles: List[Article]) -> float:
        """
        Calcule le sentiment moyen pour une liste d'articles.
        
        Conversion : positif=+1, neutre=0, négatif=-1
        Pondération par la confiance (sentiment_score)
        """
        if not articles:
            return 0.0
        
        mapping = {"positif": +1, "neutre": 0, "négatif": -1}
        weighted_scores = []
        
        for article in articles:
            if article.sentiment_label and article.sentiment_score:
                numeric_value = mapping[article.sentiment_label]
                confidence = article.sentiment_score
                weighted_scores.append(numeric_value * confidence)
        
        return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0
    
    def get_detailed_stats(self, articles: List[Article]) -> Dict[str, Dict]:
        """
        Calcule des statistiques détaillées par entreprise.
        
        Returns:
            {
                "Apple": {
                    "avg_sentiment": 0.45,
                    "total_articles": 23,
                    "positive": 15,
                    "neutral": 5,
                    "negative": 3
                },
                ...
            }
        """
        companies = self._group_by_company(articles)
        stats = {}
        
        for company, company_articles in companies.items():
            label_counts = {"positif": 0, "neutre": 0, "négatif": 0}
            
            for article in company_articles:
                if article.sentiment_label:
                    label_counts[article.sentiment_label] += 1
            
            stats[company] = {
                "avg_sentiment": self._calculate_average_sentiment(company_articles),
                "total_articles": len(company_articles),
                "positive": label_counts["positif"],
                "neutral": label_counts["neutre"],
                "negative": label_counts["négatif"]
            }
        
        return stats