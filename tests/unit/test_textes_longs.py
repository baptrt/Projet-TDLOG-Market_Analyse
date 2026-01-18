import time
import sys
import os

# --- 1. GESTION DU CHEMIN (RACINE) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- 2. IMPORT CORRIGÉ (LE VRAI NOM DE LA CLASSE) ---
# On importe FinBERTSentimentAnalyzer au lieu de SentimentAnalyzer
from domain.services.sentiment_analyzer import FinBERTSentimentAnalyzer

def test_long_text():
    print("--- DÉBUT DU TEST DE PERFORMANCE ---")
    
    try:
        print("Initialisation de FinBERT...")
        # On utilise la nouvelle classe
        analyzer = FinBERTSentimentAnalyzer()
        print("✅ Modèle chargé avec succès.")
    except Exception as e:
        print(f"❌ Erreur init : {e}")
        return

    text = "L'inflation persiste mais les fondamentaux restent solides. " * 500
    print(f"Analyse de {len(text.split())} mots...")

    start = time.time()
    
    # J'ai ajouté une sécurité pour trouver le nom de la méthode (analyze ou analyze_article)
    if hasattr(analyzer, 'analyze_article'):
        result = analyzer.analyze_article(text)
    else:
        result = analyzer.analyze(text)
        
    duration = time.time() - start

    print(f"Résultat : {result}")
    print(f"Temps : {duration:.4f}s")
    
    if result:
        print("✅ SUCCÈS")

if __name__ == "__main__":
    test_long_text()