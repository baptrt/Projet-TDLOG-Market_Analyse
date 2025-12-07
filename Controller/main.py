import sys
import os

# Permet de trouver les modules (Model, etc.)
sys.path.append(os.getcwd())

from Controller.sentiment import SentimentAnalyzer
from Model.database import DatabaseHandler  # <--- NOUVEL IMPORT

def main():
    analyzer = SentimentAnalyzer()

    print("--- DÉBUT DE L'ANALYSE ---")
    
    # 1. On fait l'analyse (Lecture JSON -> Analyse -> Création Objet Python)
    # Note : On garde la création du fichier JSON de sortie comme backup, c'est toujours utile
    articles = analyzer.analyze_json_file("outputs/news.json", "outputs/articles_with_sentiment.json")

    # 2. SAUVEGARDE EN BASE DE DONNÉES (SQL)
    print("💾 Sauvegarde dans la base de données SQL...")
    db = DatabaseHandler()
    
    count = 0
    for article in articles:
        db.save_article(article)
        count += 1
    
    db.close()
    print(f"✅ {count} articles traités et synchronisés en base de données.")

    # 3. Affichage console des scores
    company_scores = analyzer.aggregate_sentiment_by_company(articles)
    print("\nSentiment global par entreprise :")
    for company, score in company_scores.items():
        print(f"   -> {company} : {score:.3f}")

if __name__ == "__main__":
    main()