import time
import sys
import os
import datetime
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
    # Ajoute la racine du projet pour les imports.

from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.entities.article import Article

def test_long_text():
    print("--- DÉBUT DU TEST DE PERFORMANCE ---")
    
    try:
        analyzer = FinBERTSentimentAnalyzer()
        print("Modèle chargé.")
    except Exception as e:
        print(f"Erreur init : {e}")
        return

    # Texte long pour tester la latence.
    base_sentence = "L'inflation persiste mais les fondamentaux restent solides. "
    raw_text = base_sentence * 500 
    
    dummy_article = Article(
        title="Test Performance",
        content=raw_text,
        company="Test Corp",
        source="Unit Test",
        url="http://test/unit",
        published_date=datetime.datetime.now()
    )

    print(f"Analyse d'un article de {len(raw_text.split())} mots...")

    # Mesure simple de temps d'inférence.
    start = time.time()
    
    try:
        if hasattr(analyzer, 'analyze_article'):
            result = analyzer.analyze_article(dummy_article)
        else:
            result = analyzer.analyze(dummy_article)
            
        duration = time.time() - start
        
        print(f"Résultat : {result}")
        print(f"Temps : {duration:.4f}s")
        print("SUCCÈS")
        
    except Exception as e:
        print(f"Erreur pendant l'analyse : {e}")

if __name__ == "__main__":
    test_long_text()
