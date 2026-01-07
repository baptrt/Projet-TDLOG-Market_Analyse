# domain/services/sentiment_analyzer.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List
from domain.entities.article import Article
from domain.entities.sentiment import SentimentResult


class FinBERTSentimentAnalyzer:
    """
    Service métier : Analyse de sentiment financier avec FinBERT.
    
    Responsabilité unique : Analyser du texte et retourner un sentiment.
    """
    
    # Mapping anglais → français (constant de classe)
    LABEL_TRANSLATION = {
        "negative": "négatif",
        "neutral": "neutre",
        "positive": "positif"
    }
    
    def __init__(self):
        """Initialise le modèle FinBERT."""
        print("[FinBERT] Chargement du modèle...")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.id2label = self.model.config.id2label
        print("[FinBERT] Modèle chargé avec succès")
    
    def analyze_text(self, text: str) -> SentimentResult:
        """
        Analyse un texte et retourne le résultat de sentiment.
        
        Args:
            text: Texte à analyser (titre + contenu d'article)
        
        Returns:
            SentimentResult avec label, score et probabilités
        """
        # Tokenisation et inférence
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            padding=True,
            max_length=512  # Limite FinBERT
        )
        
        with torch.no_grad():  # Optimisation : pas de gradient
            outputs = self.model(**inputs)
        
        # Calcul des probabilités
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        
        # Prédiction = argmax
        predicted_idx = torch.argmax(probs).item()
        
        # Traduction du label
        label_en = self.id2label[predicted_idx]
        label_fr = self.LABEL_TRANSLATION[label_en]
        
        # Score de confiance
        confidence = probs[predicted_idx].item()
        
        # Dictionnaire des probabilités (en français)
        probabilities = {
            self.LABEL_TRANSLATION[self.id2label[i]]: probs[i].item()
            for i in range(len(probs))
        }
        
        return SentimentResult(
            label=label_fr,
            score=confidence,
            probabilities=probabilities
        )
    
    def analyze_article(self, article: Article) -> Article:
        """
        Analyse un article et met à jour ses champs de sentiment.
        
        Args:
            article: Article à analyser
        
        Returns:
            Article enrichi avec les données de sentiment
        """
        text = article.get_text_for_analysis()
        
        if not text:
            # Texte vide → sentiment neutre par défaut
            sentiment = SentimentResult(
                label="neutre",
                score=1.0,
                probabilities={"négatif": 0.0, "neutre": 1.0, "positif": 0.0}
            )
        else:
            sentiment = self.analyze_text(text)
        
        # Mise à jour de l'article (mutation)
        article.sentiment_label = sentiment.label
        article.sentiment_score = sentiment.score
        article.sentiment_probas = sentiment.probabilities
        
        return article
    
    def analyze_batch(self, articles: List[Article]) -> List[Article]:
        """
        Analyse un lot d'articles.
        
        Args:
            articles: Liste d'articles à analyser
        
        Returns:
            Articles enrichis avec sentiments
        """
        print(f"[Analyse] Traitement de {len(articles)} articles...")
        
        for i, article in enumerate(articles, 1):
            self.analyze_article(article)
            
            if i % 10 == 0:  # Affichage de progression
                print(f"  → {i}/{len(articles)} articles analysés")
        
        print(f"[Analyse] ✓ {len(articles)} articles traités")
        return articles