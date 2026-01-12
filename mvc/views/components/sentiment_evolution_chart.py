# mvc/views/components/sentiment_evolution_chart.py

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict

class SentimentEvolutionChart(FigureCanvasQTAgg):
    """
    Composant : Graphique d'évolution temporelle du sentiment.
    
    Affiche l'évolution du sentiment par entreprise dans le temps.
    """
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 5))
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.setParent(parent)
    
    def update_chart(self, history_data: List[Dict]):
        """
        Met à jour le graphique avec l'historique.
        
        Args:
            history_data: Liste de {timestamp, scores} depuis trend_history.json
        """
        if not history_data:
            self._show_empty_state()
            return
        
        # Restructuration : {company: [(datetime, score), ...]}
        company_series = {}
        
        for entry in history_data:
            timestamp_str = entry["timestamp"]
            
            # Conversion string → datetime
            try:
                dt_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            
            scores = entry["scores"]
            
            for company, score in scores.items():
                company_series.setdefault(company, []).append((dt_obj, score))
        
        # Tracer les courbes
        self.ax.clear()
        
        for company, points in company_series.items():
            # Tri chronologique
            points.sort(key=lambda x: x[0])
            
            if points:
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                self.ax.plot(xs, ys, marker='o', markersize=4, label=company, linewidth=2)
        
        # Mise en forme
        self.ax.set_ylim(-1.1, 1.1)
        self.ax.set_ylabel("Sentiment Moyen")
        self.ax.set_title("Évolution du Sentiment (Temps Réel)")
        self.ax.axhline(y=0, color='black', linestyle='--', linewidth=0.5, alpha=0.3)
        
        # Format des dates sur l'axe X (matplotlib choisit le format adapté)
        locator = mdates.AutoDateLocator()
        formatter = mdates.AutoDateFormatter(locator)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.fig.autofmt_xdate()
        
        # Légende à l'extérieur du graphique
        self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.fig.tight_layout()
        self.draw()
    
    def _show_empty_state(self):
        """Affiche un message si aucune donnée."""
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Pas d'historique disponible", 
                     ha='center', va='center', transform=self.ax.transAxes)
        self.draw()