# mvc/models/ui_state.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class UIState:
    """
    Modèle MVC : État de l'interface graphique.
    
    Stocke toutes les données affichées à l'écran.
    """
    # Données affichées
    all_articles: List[Dict] = field(default_factory=list)
    filtered_articles: List[Dict] = field(default_factory=list)
    current_article: Optional[Dict] = None
    
    # Filtres actifs
    selected_company: str = "Toutes les entreprises"
    search_query: str = ""
    sentiment_filter: str = "Tous"
    
    # État de l'application
    is_loading: bool = False
    error_message: str = ""
    
    # Données pour les graphiques
    chart_data: List[Dict] = field(default_factory=list)
    trend_history: List[Dict] = field(default_factory=list)
    
    # Favoris
    show_favorites_only: bool = False
    
    def get_unique_companies(self) -> List[str]:
        """Retourne la liste des entreprises uniques."""
        if not self.all_articles:
            return []
        return sorted(set(article["company"] for article in self.all_articles))
    
    def apply_filters(self):
        """Applique les filtres et met à jour filtered_articles."""
        filtered = []
        
        for article in self.all_articles:
            # Filtre entreprise
            if (self.selected_company != "Toutes les entreprises" and 
                article["company"] != self.selected_company):
                continue
            
            # Filtre recherche
            query = self.search_query.lower()
            if query and query not in article["title"].lower() and query not in article["summary"].lower():
                continue
            
            # Filtre sentiment
            if (self.sentiment_filter != "Tous" and 
                article["sentiment_label"].lower() != self.sentiment_filter.lower()):
                continue
            
            filtered.append(article)
        
        self.filtered_articles = filtered
