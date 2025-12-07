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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                title TEXT,
                publisher TEXT,
                link TEXT UNIQUE,  -- UNIQUE empêche les doublons
                summary TEXT,
                full_text TEXT,
                published_at TEXT,
                sentiment_label TEXT,
                sentiment_score REAL,
                sentiment_probas TEXT -- On stocke le dictionnaire en texte JSON
            )
        """)
        self.conn.commit()

    def save_article(self, article):
        """Sauvegarde un article (dictionnaire) dans la base."""
        # On transforme le dictionnaire de probabilités en texte pour SQL
        probas_json = json.dumps(article.get("sentiment_probas", {}))

        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO articles (
                    company, title, publisher, link, summary, 
                    full_text, published_at, sentiment_label, 
                    sentiment_score, sentiment_probas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                probas_json
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Erreur SQL : {e}")

    def fetch_all_articles(self):
        """Récupère tout pour l'interface graphique."""
        # On trie par date décroissante (le plus récent en haut)
        self.cursor.execute("SELECT * FROM articles ORDER BY published_at DESC")
        rows = self.cursor.fetchall()
        
        articles_list = []
        for row in rows:
            # On reconstruit le dictionnaire exactement comme l'UI l'attend
            articles_list.append({
                "company": row[1],
                "title": row[2],
                "publisher": row[3],
                "link": row[4],
                "summary": row[5],
                "full_text": row[6],
                "time": row[7],
                "sentiment_label": row[8],
                "sentiment_score": row[9],
                # On reconvertit le texte SQL en vrai dictionnaire Python
                "sentiment_probas": json.loads(row[10]) 
            })
        return articles_list

    def close(self):
        self.conn.close()