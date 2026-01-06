# mvc/views/components/sentiment_bar_chart.py

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from typing import List, Dict

class SentimentBarChart(FigureCanvasQTAgg):
    """
    Composant : Graphique en barres du sentiment par entreprise.
    
    Vue MVC réutilisable.
    """
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 4))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)
    
    def update_chart(self, articles: List[Dict]):
        """
        Met à jour le graphique avec de nouvelles données.
        
        Args:
            articles: Liste d'articles avec sentiments
        """
        if not articles:
            self._show_empty_state()
            return
        
        # Calcul des scores moyens par entreprise
        scores = {}
        for article in articles:
            company = article["company"]
            probas = article["sentiment_probas"]
            
            # Score pondéré : -1 (négatif) à +1 (positif)
            sentiment_value = (
                -1 * probas.get("négatif", 0) +
                 0 * probas.get("neutre", 0) +
                 1 * probas.get("positif", 0)
            )
            
            scores.setdefault(company, []).append(sentiment_value)
        
        # Moyenne par entreprise
        avg_scores = {company: sum(values) / len(values) 
                      for company, values in scores.items()}
        
        # Tri par score décroissant
        sorted_companies = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        companies = [c[0] for c in sorted_companies]
        values = [c[1] for c in sorted_companies]
        
        # Couleurs selon le sentiment
        colors = [
            "green" if s > 0.2 else "yellow" if -0.2 <= s <= 0.2 else "red"
            for s in values
        ]
        
        # Mise à jour du graphique
        self.ax.clear()
        self.ax.bar(companies, values, color=colors)
        self.ax.set_ylim(-1, 1)
        self.ax.set_ylabel("Sentiment moyen (pondéré)")
        self.ax.set_title("Sentiment par entreprise")
        self.ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        
        # Rotation des labels si nécessaire
        if len(companies) > 5:
            self.ax.tick_params(axis='x', rotation=45)
        
        self.fig.tight_layout()
        self.draw()
    
    def _show_empty_state(self):
        """Affiche un message si aucune donnée."""
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Aucune donnée à afficher", 
                     ha='center', va='center', transform=self.ax.transAxes)
        self.draw()