import sqlite3
import json
import os
from typing import List, Dict

class DatabaseRepository:
    """
    Repository pattern : Accès à la base de données SQLite.
    Version 'Stateless' avec DEBUG PATH.
    """
    
    def __init__(self, db_name: str = "market_sentiment.db"):
        # On remonte : repository.py -> database -> infrastructure -> TDLOG (Racine)
        current_file = os.path.abspath(__file__)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        output_dir = os.path.join(base_dir, "outputs")
        
        os.makedirs(output_dir, exist_ok=True)
        self.db_path = os.path.join(output_dir, db_name)
        
        # Initialisation immédiate de la table
        self._create_tables()
    
    def _get_connection(self):
        """Ouvre une connexion fraîche (timeout augmenté pour éviter les verrous)."""
        return sqlite3.connect(self.db_path, timeout=10)

    def _create_tables(self):
        """Crée la table de manière atomique."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # On force la création
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company TEXT NOT NULL,
                        title TEXT NOT NULL,
                        source TEXT,             
                        link TEXT,
                        summary TEXT,
                        full_text TEXT,
                        published_date TEXT,
                        sentiment_label TEXT,
                        sentiment_score REAL,
                        sentiment_probas TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(link, company)
                    )
                """)
                # Création des index
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON articles(company)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON articles(published_date DESC)")
                conn.commit()
                
        except Exception as e:
            print(f"[DB CRITICAL] Impossible de créer la table : {e}")
    
    def save_article(self, article: Dict) -> bool: 
        """
        Sauvegarde un article.
        Retourne True si l'article est NOUVEAU, False si c'est un DOUBLON.
        """
        probas_json = json.dumps(article.get("sentiment_probas", {}))
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO articles (
                        company, title, source, link, summary,
                        full_text, published_date, sentiment_label,
                        sentiment_score, sentiment_probas
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.get("company"),
                    article.get("title"),
                    article.get("source") or article.get("publisher"),
                    article.get("link") or article.get("url"),
                    article.get("summary"),
                    article.get("content") or article.get("full_text"),
                    article.get("published_date") or article.get("time"),
                    article.get("sentiment_label"),
                    article.get("sentiment_score"),
                    probas_json
                ))
                conn.commit()

                # rowcount = 1 -> Une ligne ajoutée (Succès)
                # rowcount = 0 -> Rien ajouté (Doublon ignoré)
                return cursor.rowcount > 0 
                
        except Exception as e:
            if "no such table" in str(e):
                self._create_tables() #
                return False
            print(f"Erreur SQL save_article : {e}")
            return False
    
    def fetch_all_articles(self) -> List[Dict]:
        """Récupère les articles."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM articles ORDER BY published_date DESC")
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Erreur SQL fetch_all : {e}")
            return []
    
    def fetch_articles_by_company(self, company: str) -> List[Dict]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM articles 
                    WHERE company = ? 
                    ORDER BY published_date DESC
                """, (company,))
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"Erreur SQL fetch_company : {e}")
            return []

    def _row_to_dict(self, row) -> Dict:
        return {
            "id": row[0],
            "company": row[1],
            "title": row[2],
            "source": row[3],          
            "publisher": row[3],      
            "link": row[4],
            "url": row[4],            
            "summary": row[5],
            "content": row[6],         
            "published_date": row[7],
            "time": row[7],            
            "sentiment_label": row[8],
            "sentiment_score": row[9],
            "sentiment_probas": json.loads(row[10]) if row[10] else {}
        }