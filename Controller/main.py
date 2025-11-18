from sentiment import SentimentAnalyzer

def main():
    analyzer = SentimentAnalyzer()

    articles = analyzer.analyze_json_file("news.json", "articles_with_sentiment.json")

    company_scores = analyzer.aggregate_sentiment_by_company(articles)

    print("Sentiment global par entreprise :")
    for company, score in company_scores.items():
        print(f"{company} : {score:.3f}")

if __name__ == "__main__":
    main()
