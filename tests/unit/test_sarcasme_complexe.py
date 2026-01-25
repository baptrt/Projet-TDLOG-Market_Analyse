import sys
import os
import datetime

# 1. Configuration des chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. Nouveaux Imports
from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.entities.article import Article

def test_sarcasm():
    print("--- TEST DE DÉTECTION DE SARCASME ---")
    
    try:
        analyzer = FinBERTSentimentAnalyzer()
    except Exception as e:
        print(f"❌ Erreur init : {e}")
        return

    # Phrases pièges
    sarcastic_texts = [
        "Super, l'action a encore perdu 10%. Quelle journée fantastique.",
        "Génial, exactement ce dont on avait besoin : une nouvelle faillite.",
        "Bravo à la direction pour cette magnifique perte record."
    ]

    for text in sarcastic_texts:
        # On emballe chaque phrase dans un Article
        dummy_article = Article(
            title="Test Sarcasme",
            content=text,
            company="Sarcasm Corp",
            source="Test",
            url="http://test",
            published_date=datetime.datetime.now()
        )
        
        # Analyse
        if hasattr(analyzer, 'analyze_article'):
            result = analyzer.analyze_article(dummy_article)
        else:
            result = analyzer.analyze(dummy_article)
            
        print(f"Phrase : '{text}'")
        print(f" -> Détecté : {result.sentiment_label} (Score: {result.sentiment_score:.2f})")
        print("-" * 20)

if __name__ == "__main__":
    test_sarcasm()