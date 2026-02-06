"""
Configuration pour l'API Foodles
"""
import os
from typing import Optional


class FoodlesConfig:
    """Configuration pour accéder à l'API Foodles"""
    
    def __init__(self):
        # Récupère les tokens depuis les variables d'environnement ou les définit manuellement
        self.session_id: Optional[str] = os.getenv('FOODLES_SESSION_ID')
        self.csrf_token: Optional[str] = os.getenv('FOODLES_CSRF_TOKEN')
        
        # Configuration de la cantine par défaut
        self.canteen_id: int = int(os.getenv('FOODLES_CANTEEN_ID', '2051'))
        self.canteen_name: str = os.getenv('FOODLES_CANTEEN_NAME', 'Worldline Copernic')
        self.delivery_date: str = os.getenv('FOODLES_DELIVERY_DATE', '2026-01-30')
    
    def is_configured(self) -> bool:
        """Vérifie si les tokens sont configurés"""
        return self.session_id is not None and self.csrf_token is not None
    
    def set_credentials(self, session_id: str, csrf_token: str):
        """
        Définit manuellement les credentials
        
        Args:
            session_id: Le sessionid du cookie
            csrf_token: Le csrftoken du cookie
        """
        self.session_id = session_id
        self.csrf_token = csrf_token
    
    def get_credentials(self) -> tuple[str, str]:
        """
        Retourne les credentials
        
        Returns:
            Tuple (session_id, csrf_token)
        """
        if not self.is_configured():
            raise ValueError(
                "Les credentials ne sont pas configurés. "
                "Utilisez set_credentials() ou définissez les variables d'environnement "
                "FOODLES_SESSION_ID et FOODLES_CSRF_TOKEN"
            )
        return self.session_id, self.csrf_token


# Instance globale de configuration
config = FoodlesConfig()
