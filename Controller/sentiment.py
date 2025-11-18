import json
from typing import List, Dict, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class FinBERTSentiment:
    """
    Analyse de sentiment spécialisée finance basée sur FinBERT.
    Labels : négatif / neutre / positif (en français)
    """

    def __init__(self):
        print("[FinBERT] Chargement du modèle…")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

        # Labels issus du modèle (en anglais)
        self.id2label = self.model.config.id2label  # {0:'negative',1:'neutral',2:'positive'}

        # Mapping anglais -> français
        self.label_fr = {
            "negative": "négatif",
            "neutral": "neutre",
            "positive": "positif"
        }

    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Analyse un texte et renvoie (label_fr, probabilité_assoc)
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = self.model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]

        # Prédiction = argmax
        idx = torch.argmax(probs).item()

        # Label anglais du modèle
        label_en = self.id2label[idx]

        # Traduction en français
        label = self.label_fr[label_en]

        # Score de la classe prédite
        confidence = probs[idx].item()

        return label, confidence



class SentimentAnalyzer:
    """
    Interface simple pour analyser un article ou un fichier JSON.
    Utilise seulement FinBERT.
    """

    def __init__(self):
        self.model = FinBERTSentiment()

    def analyze_article(self, text: str) -> Tuple[str, float]:
        return self.model.analyze(text)

    def analyze_json_file(self, input_json: str, output_json: str = None) -> List[Dict]:
        with open(input_json, "r") as f:
            articles = json.load(f)

        for article in articles:
            # Sécurise si la clé manque
            text = article.get("full_text") or article.get("content") or article.get("text") or ""
            label, score = self.analyze_article(text)
            article["sentiment_label"] = label
            article["sentiment_score"] = score

        if output_json:
            with open(output_json, "w") as f:
                json.dump(articles, f, indent=4, ensure_ascii=False)

        return articles

    def group_by_company(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        companies = {}
        for a in articles:
            company = a.get("company", "Unknown")
            companies.setdefault(company, []).append(a)
        return companies
    
    def aggregate_company_sentiment(self, articles: List[Dict]) -> float:
        mapping = {"positif": +1, "neutre": 0, "négatif": -1}
        scores = []

        for a in articles:
            label = a["sentiment_label"]
            confidence = a["sentiment_score"]
            scores.append(mapping[label] * confidence)

        return sum(scores) / len(scores) if scores else 0.0
    
    def aggregate_sentiment_by_company(self, articles: List[Dict]) -> Dict[str, float]:
        groups = self.group_by_company(articles)
        results = {}

        for company, company_articles in groups.items():
            results[company] = self.aggregate_company_sentiment(company_articles)

        return results
