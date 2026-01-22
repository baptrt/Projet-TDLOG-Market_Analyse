# infrastructure/database/models.py
# Extension des modèles pour supporter les utilisateurs et favoris

import sqlite3
from pathlib import Path
from typing import Optional, List
import hashlib

class DatabaseSchema:
    """Schéma de base de données étendu avec gestion utilisateurs."""
    
    @staticmethod
    def init_database(db_path: str = "data/users.db"):
        """Initialise toutes les tables nécessaires."""
        resolved_path = resolve_db_path(db_path)
        Path(resolved_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(resolved_path)
        cursor = conn.cursor()

        # Utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT
            )
        """)
        
        # Favoris (relation many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT NOT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, company)
            )
        """)
        
        # Préférences utilisateur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, preference_key)
            )
        """)
        
        # Index pour performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_favorites_user 
            ON user_favorites(user_id)
        """)
        
        conn.commit()
        conn.close()
        
        print("[DB] Tables utilisateurs créées avec succès")


def resolve_db_path(db_path: str) -> str:
    """Résout un chemin de BDD relatif vers la racine du projet."""
    path = Path(db_path)
    if path.is_absolute():
        return str(path)
    project_root = Path(__file__).resolve().parents[2]
    # Force un emplacement stable même si le cwd change
    return str(project_root / path)


class UserModel:
    """Modèle pour la gestion des utilisateurs."""
    
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = resolve_db_path(db_path)
        DatabaseSchema.init_database(self.db_path)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe avec SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Optional[int]:
        """Crée un nouvel utilisateur."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"[USER] Utilisateur '{username}' créé avec ID {user_id}")
            return user_id
            
        except sqlite3.IntegrityError:
            print(f"[USER] Erreur : L'utilisateur '{username}' existe déjà")
            return None
    
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authentifie un utilisateur."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute("""
            SELECT id, username, email, created_at
            FROM users
            WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            # Mise à jour du dernier login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (result[0],))
            conn.commit()
            
            user = {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3]
            }
            
            conn.close()
            print(f"[AUTH] Utilisateur '{username}' authentifié")
            return user
        
        conn.close()
        print(f"[AUTH] Échec d'authentification pour '{username}'")
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Récupère un utilisateur par son ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, created_at, last_login
            FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3],
                "last_login": result[4]
            }
        return None


class FavoritesModel:
    """Modèle pour la gestion des favoris."""
    
    def __init__(self, user_db_path: str = "data/users.db", articles_db_path: str = "data/articles.db"):
        self.user_db_path = resolve_db_path(user_db_path)
        self.articles_db_path = resolve_db_path(articles_db_path)
    
    def add_favorite(self, user_id: int, company: str) -> bool:
        """Ajoute une entreprise aux favoris."""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_favorites (user_id, company)
                VALUES (?, ?)
            """, (user_id, company))
            
            conn.commit()
            conn.close()
            
            print(f"[FAVORITES] '{company}' ajouté aux favoris de l'utilisateur {user_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"[FAVORITES] '{company}' déjà dans les favoris")
            return False
    
    def remove_favorite(self, user_id: int, company: str) -> bool:
        """Retire une entreprise des favoris."""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM user_favorites
            WHERE user_id = ? AND company = ?
        """, (user_id, company))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            print(f"[FAVORITES] '{company}' retiré des favoris")
        
        return deleted
    
    def get_user_favorites(self, user_id: int) -> List[str]:
        """Récupère la liste des entreprises favorites."""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT uf.company
            FROM user_favorites uf
            JOIN users u ON u.id = uf.user_id
            WHERE u.id = ?
            ORDER BY uf.added_at DESC
        """, (user_id,))
        
        favorites = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return favorites
    
    def is_favorite(self, user_id: int, company: str) -> bool:
        """Vérifie si une entreprise est favorite."""
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM user_favorites
            WHERE user_id = ? AND company = ?
        """, (user_id, company))
        
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def get_favorites_stats(self, user_id: int) -> dict:
        """Statistiques sur les favoris de l'utilisateur."""
        favorites = self.get_user_favorites(user_id)
        
        conn = sqlite3.connect(self.user_db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        articles_db_path = self.articles_db_path.replace("'", "''")
        cursor.execute(f"ATTACH DATABASE '{articles_db_path}' AS articles_db")

        for company in favorites:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_articles,
                    AVG(sentiment_score) as avg_sentiment,
                    sentiment_label
                FROM articles_db.articles
                WHERE company = ?
                GROUP BY sentiment_label
            """, (company,))
            
            results = cursor.fetchall()
            
            stats[company] = {
                "total_articles": sum(r[0] for r in results),
                "avg_sentiment": sum(r[1] for r in results if r[1]) / len(results) if results else 0,
                "sentiment_distribution": {r[2]: r[0] for r in results}
            }
        
        conn.close()
        return stats
