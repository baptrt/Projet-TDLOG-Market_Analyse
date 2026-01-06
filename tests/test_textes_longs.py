import time
import sys
import os

# Ajout du chemin parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Controller.sentiment import SentimentAnalyzer

def test_long_text():
    analyzer = SentimentAnalyzer()
    
    print("--- DÉBUT DU TEST DE PERFORMANCE (TEXTES LONGS) ---\n")

    # Phrase mitigée (Le modèle la voit souvent comme Neutre à cause de "Malgré", "Difficile", "Inflation")
    base_sentence = (
        "Malgré un environnement macroéconomique difficile et une "
        "inflation persistante, nos fondamentaux restent solides. "
    )
    long_text = base_sentence * 500 
    
    word_count = len(long_text.split())
    print(f"Test avec un texte de {word_count} mots...")

    start_time = time.time()
    
    # Appel de l'analyse
    result_tuple = analyzer.analyze_article(long_text)
    
    end_time = time.time()
    duration = end_time - start_time

    # --- CORRECTION DU CRASH ICI ---
    # On récupère le texte (index 0) depuis le tuple ('neutre', score, dict)
    sentiment_label = result_tuple[0] 

    print(f"Résultat complet : {result_tuple}")
    print(f"Sentiment extrait : {sentiment_label}")
    print(f"Temps d'exécution : {duration:.4f} secondes")
    
    # --- VALIDATION ---
    # On accepte "positif" OU "neutre" car la phrase est nuancée financièrement
    if sentiment_label.lower() in ["positif", "neutre"]:
        print("SUCCÈS : Le modèle a géré la charge et donné un résultat cohérent.")
    else:
        print(f"ÉCHEC : Résultat inattendu ({sentiment_label}).")

if __name__ == "__main__":
    test_long_text()