# mvc/controllers/auth_controller.py

from typing import Optional
from infrastructure.database.models import UserModel, FavoritesModel

class AuthController:
    """
    Contrôleur pour gérer l'authentification et les favoris.
    """
    
    def __init__(self, user_db_path: str = "data/users.db", articles_db_path: str = "data/articles.db"):
        self.user_model = UserModel(user_db_path)
        self.favorites_model = FavoritesModel(user_db_path, articles_db_path)
        self.current_user: Optional[dict] = None
        self.last_error: str = ""
    
    def login(self, username: str, password: str) -> bool:
        """
        Connecte un utilisateur.
        
        Returns:
            True si succès, False sinon
        """
        self.last_error = ""
        try:
            user = self.user_model.authenticate(username, password)
        except Exception as exc:
            print(f"[AUTH] Erreur login: {exc}")
            self.last_error = "Erreur lors de la connexion"
            return False
        
        if user:
            self.current_user = user
            return True
        self.last_error = "Identifiants incorrects"
        return False
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> bool:
        """
        Enregistre un nouvel utilisateur.
        
        Returns:
            True si succès, False si l'utilisateur existe déjà
        """
        self.last_error = ""
        try:
            user_id = self.user_model.create_user(username, password, email)
        except Exception as exc:
            print(f"[AUTH] Erreur inscription: {exc}")
            self.last_error = "Erreur lors de l'inscription"
            return False
        
        if user_id:
            # Auto-login après inscription
            self.current_user = self.user_model.get_user_by_id(user_id)
            return True
        self.last_error = "Ce nom d'utilisateur existe déjà"
        return False
    
    def logout(self):
        """Déconnecte l'utilisateur actuel."""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[dict]:
        """Retourne l'utilisateur actuel."""
        return self.current_user
    
    # === GESTION DES FAVORIS ===
    
    def add_favorite(self, company: str) -> bool:
        """Ajoute une entreprise aux favoris de l'utilisateur connecté."""
        if not self.is_authenticated():
            return False
        
        return self.favorites_model.add_favorite(
            self.current_user["id"], 
            company
        )
    
    def remove_favorite(self, company: str) -> bool:
        """Retire une entreprise des favoris."""
        if not self.is_authenticated():
            return False
        
        return self.favorites_model.remove_favorite(
            self.current_user["id"], 
            company
        )
    
    def get_favorites(self) -> list:
        """Récupère les favoris de l'utilisateur connecté."""
        if not self.is_authenticated():
            return []
        
        return self.favorites_model.get_user_favorites(self.current_user["id"])
    
    def is_favorite(self, company: str) -> bool:
        """Vérifie si une entreprise est favorite."""
        if not self.is_authenticated():
            return False
        
        return self.favorites_model.is_favorite(
            self.current_user["id"], 
            company
        )
    
    def get_favorites_stats(self) -> dict:
        """Récupère les statistiques sur les favoris."""
        if not self.is_authenticated():
            return {}
        
        return self.favorites_model.get_favorites_stats(self.current_user["id"])
