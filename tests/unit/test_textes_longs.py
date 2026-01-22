import time
import sys
import os
import datetime

# 1. Configuration des chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# 2. Imports
from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer
from domain.entities.article import Article

def test_long_text():
    print("--- DÉBUT DU TEST DE PERFORMANCE ---")
    
    try:
        analyzer = FinBERTSentimentAnalyzer()
        print("✅ Modèle chargé.")
    except Exception as e:
        print(f"❌ Erreur init : {e}")
        return

    # Texte long
    base_sentence = "L'inflation persiste mais les fondamentaux restent solides. "
    raw_text = base_sentence * 500 
    
    # 3. CRÉATION DE L'ARTICLE (CORRIGÉE AVEC LES VRAIS NOMS)
    dummy_article = Article(
        title="Test Performance",
        content=raw_text,            # C'était 'content' !
        company="Test Corp",         # OBLIGATOIRE (vu dans ton fichier)
        source="Unit Test",          # C'était 'source' !
        url="http://test/unit",      # C'était 'url' !
        published_date=datetime.datetime.now()
    )

    print(f"Analyse d'un article de {len(raw_text.split())} mots...")

    start = time.time()
    
    try:
        # On lance l'analyse
        # (J'utilise analyze_article car c'est la méthode métier logique)
        if hasattr(analyzer, 'analyze_article'):
            result = analyzer.analyze_article(dummy_article)
        else:
            result = analyzer.analyze(dummy_article)
            
        duration = time.time() - start
        
        print(f"Résultat : {result}")
        print(f"Temps : {duration:.4f}s")
        print("✅ SUCCÈS")
        
    except Exception as e:
        print(f"❌ Erreur pendant l'analyse : {e}")

if __name__ == "__main__":
    test_long_text()