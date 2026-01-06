import sys
import os

# Ajout du chemin parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Controller.sentiment import SentimentAnalyzer

def test_finance_complex_cases():
    analyzer = SentimentAnalyzer()
    
    # Format : (Phrase, Sentiment Réel Attendu)
    financial_cases = [
        # --- 1. L'Ironie pure (Mots positifs pour un désastre) ---
        ("Quelle brillante stratégie de la direction : l'action a été divisée par deux en un mois.", "négatif"),
        ("Merci pour cette 'performance' incroyable, mon portefeuille a fondu comme neige au soleil.", "négatif"),
        ("Un grand bravo aux analystes qui recommandaient d'acheter juste avant le krach.", "négatif"),

        # --- 2. L'Euphémisme (Minimiser une catastrophe) ---
        ("Ce n'est pas une perte, c'est juste une 'réallocation involontaire' de mes fonds vers le néant.", "négatif"),
        ("L'entreprise n'est pas en faillite, elle traverse juste une 'crise de liquidité permanente'.", "négatif"),
        
        # --- 3. Le "Buy High Sell Low" (Le classique des traders) ---
        ("Ma technique favorite : acheter au plus haut historique et revendre quand ça vaut zéro.", "négatif"),
        
        # --- 4. La fausse bonne nouvelle ---
        ("Super, les dividendes augmentent de 1 centime alors que l'action en a perdu 50 euros.", "négatif")
    ]

    print("--- TEST ANALYSE : SARCASME FINANCIER DIFFICILE ---\n")

    score = 0
    for phrase, attendu in financial_cases:
        # 1. Analyse
        result_tuple = analyzer.analyze_article(phrase)
        result_label = result_tuple[0] # On garde juste le label (ex: 'positif')
        
        print(f"Phrase : \"{phrase}\"")
        print(f"   -> Sens réel attendu : {attendu}")
        print(f"   -> L'IA a détecté    : {result_label} (Score: {result_tuple[1]:.4f})")
        
        # 2. Verdict
        if attendu in result_label.lower():
            print("L'IA a compris le sarcasme !")
            score += 1
        elif result_label == "neutre":
            print("L'IA est confuse (Neutre)")
        else:
            print("L'IA s'est fait piéger (A pris le positif au premier degré)")
        
        print("-" * 50)

    print(f"\nScore de détection du sarcasme : {score}/{len(financial_cases)}")
    print("\nNote : Il est NORMAL que le score soit bas. FinBERT n'est pas entraîné pour l'ironie.")

if __name__ == "__main__":
    test_finance_complex_cases()