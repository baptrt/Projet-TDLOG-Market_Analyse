# domain/entities/sentiment.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class SentimentResult:
    """
    Entité métier : Résultat d'analyse de sentiment.
    
    Représente le sentiment détecté pour un texte.
    """
    label: str  # "négatif", "neutre", "positif"
    score: float  # Probabilité associée (0-1)
    probabilities: Dict[str, float]  # Toutes les probabilités
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "label": self.label,
            "score": self.score,
            "probabilities": self.probabilities
        }
    
    @property
    def numeric_score(self) -> float:
        """
        Convertit le sentiment en score numérique.
        positif: +1, neutre: 0, négatif: -1
        """
        mapping = {"positif": 1.0, "neutre": 0.0, "négatif": -1.0}
        return mapping[self.label] * self.score