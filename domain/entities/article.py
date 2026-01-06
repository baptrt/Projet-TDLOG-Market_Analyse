# domain/entities/article.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Article:
    """
    Entité métier : Représente un article financier.
    """
    title: str
    content: str
    company: str
    source: str
    url: Optional[str] = None
    published_date: Optional[datetime] = None
    
    # Champs ajoutés après analyse
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_probas: Optional[dict] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """Crée un Article depuis un dictionnaire JSON."""
        return cls(
            title=data.get("title", ""),
            
            content=data.get("full_text") or data.get("content") or data.get("text") or data.get("summary", ""),
            
            company=data.get("company", "Unknown"),
            
            source=data.get("source") or data.get("publisher") or "Source Inconnue",
            
            url=data.get("url") or data.get("link"),

            published_date=data.get("published_date") or data.get("time") or data.get("date")
        )
    
    def to_dict(self) -> dict:
        """Convertit l'Article en dictionnaire (pour JSON/DB)."""
        
        date_val = None
        if self.published_date:
            # Si c'est un vrai objet datetime, on le convertit en string ISO
            if hasattr(self.published_date, 'isoformat'):
                date_val = self.published_date.isoformat()
            # Si c'est déjà une string (cas du scraping), on la garde telle quelle
            else:
                date_val = str(self.published_date)

        return {
            "title": self.title,
            "content": self.content,
            "company": self.company,
            "source": self.source,
            "url": self.url,
            "published_date": date_val, 
            "sentiment_label": self.sentiment_label,
            "sentiment_score": self.sentiment_score,
            "sentiment_probas": self.sentiment_probas
        }
    
    def get_text_for_analysis(self) -> str:
        """Retourne le texte à analyser (titre + contenu)."""
        return f"{self.title}. {self.content}".strip()