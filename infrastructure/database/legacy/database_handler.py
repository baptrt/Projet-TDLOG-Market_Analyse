import sqlite3
import json
import os

class DatabaseHandler:
    def __init__(self, db_name="market_sentiment.db"):
        # 1. On calcule le chemin vers le dossier 'outputs' à la racine
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "outputs")
        
        # On s'assure que le dossier existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.db_path = os.path.join(output_dir, db_name)
        
        # 2. Connexion à la base de données
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Crée la table 'articles' si elle n'existe pas déjà."""
        # AJOUT DE LA COLONNE 'status'
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                title TEXT,
                publisher TEXT,
                link TEXT UNIQUE,
                summary TEXT,
                full_text TEXT,
                published_at TEXT,
                sentiment_label TEXT,
                sentiment_score REAL,
                sentiment_probas TEXT,
                status TEXT DEFAULT 'A_TRAITER'
            )
        """)
        self.conn.commit()

    def save_article(self, article):
        """Sauvegarde un article brut (Scrapping). Renvoie True si succès."""
        # Gestion safe des probas (peuvent être None au stade scrapping)
        probas = article.get("sentiment_probas")
        probas_json = json.dumps(probas) if probas else None
        
        # Si on a déjà un sentiment, c'est 'TRAITE', sinon 'A_TRAITER'
        status = "TRAITE" if article.get("sentiment_label") else "A_TRAITER"

        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO articles (
                    company, title, publisher, link, summary, 
                    full_text, published_at, sentiment_label, 
                    sentiment_score, sentiment_probas, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get("company"),
                article.get("title"),
                article.get("publisher"),
                article.get("link"),
                article.get("summary"),
                article.get("full_text"),
                article.get("time"), 
                article.get("sentiment_label"),
                article.get("sentiment_score"),
                probas_json,
                status
            ))
            self.conn.commit()
            return True # POUR LE TEST
        except sqlite3.Error as e:
            print(f" Erreur SQL : {e}")
            return False # POUR LE TEST

    def get_pending_articles(self):
        """Récupère les articles qui n'ont pas encore été analysés (pour le pipeline)."""
        # On renvoie l'ID et le TEXTE pour l'analyseur
        self.cursor.execute("SELECT id, full_text FROM articles WHERE status = 'A_TRAITER'")
        # Renvoie une liste de tuples : [(1, "Texte..."), (2, "Autre texte...")]
        # On transforme ça en liste de dictionnaires 
        rows = self.cursor.fetchall()
        return [{'id': row[0], 'full_text': row[1]} for row in rows]

    def update_sentiment(self, article_id, label, score, probas):
        """Met à jour un article avec les résultats de l'IA."""
        probas_json = json.dumps(probas)
        try:
            self.cursor.execute("""
                UPDATE articles 
                SET sentiment_label = ?, 
                    sentiment_score = ?, 
                    sentiment_probas = ?,
                    status = 'TRAITE'
                WHERE id = ?
            """, (label, score, probas_json, article_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f" Erreur Update : {e}")
            return False

    def fetch_all_articles(self):
        """Récupère tout pour l'UI."""
        self.cursor.execute("SELECT * FROM articles ORDER BY published_at DESC")
        rows = self.cursor.fetchall()
        
        articles_list = []
        for row in rows:
            # row[10] = probas, row[11] = status
            probas_txt = row[10]
            
            probas_dict = json.loads(probas_txt) if probas_txt else {}

            articles_list.append({
                "id": row[0],
                "company": row[1],
                "title": row[2],
                "publisher": row[3],
                "link": row[4],
                "summary": row[5],
                "full_text": row[6],
                "time": row[7],
                "sentiment_label": row[8],
                "sentiment_score": row[9],
                "sentiment_probas": probas_dict,
                "status": row[11]
            })
        return articles_list  # <--- INDISPENSABLE

    def close(self):          # <--- INDISPENSABLE
        self.conn.close()