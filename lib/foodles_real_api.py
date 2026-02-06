#!/usr/bin/env python3
"""
Client API Foodles COMPLET basé sur les vraies APIs découvertes.
Utilise https://api.foodles.co/api/ (pas le format RSC).
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime


class FoodlesRealAPI:
    """Client pour les vraies APIs Foodles"""
    
    BASE_URL = "https://api.foodles.co/api"
    
    def __init__(self, session_id: str = None, csrf_token: str = None):
        """
        Initialise le client API
        
        Args:
            session_id: Cookie sessionid (optionnel si on veut se connecter)
            csrf_token: Cookie csrftoken (optionnel)
        """
        self.session = requests.Session()
        
        # Headers par défaut
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://app.foodles.co/',
            'Origin': 'https://app.foodles.co',
        })
        
        # Cookies d'authentification
        if session_id:
            self.session.cookies.set('sessionid', session_id, domain='api.foodles.co')
            self.session.cookies.set('sessionid', session_id, domain='app.foodles.co')
        
        if csrf_token:
            self.session.cookies.set('csrftoken', csrf_token, domain='api.foodles.co')
            self.session.cookies.set('csrftoken', csrf_token, domain='app.foodles.co')
            self.session.headers['X-CSRFToken'] = csrf_token
        
        self.client_id = None
    
    # ==================== AUTHENTIFICATION ====================
    
    def get_login_type(self, email: str) -> Dict[str, Any]:
        """
        Vérifie le type de connexion pour un email
        
        Args:
            email: Adresse email
            
        Returns:
            Dict avec les infos de connexion (type, etc.)
        """
        response = self.session.get(
            f"{self.BASE_URL}/auth/login-type/",
            params={'email': email}
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Connexion avec email/password
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Dict avec les infos utilisateur
        """
        response = self.session.post(
            f"{self.BASE_URL}/auth/login/",
            json={
                'email': email,
                'password': password
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Récupérer les cookies
        if 'sessionid' in self.session.cookies:
            print("✅ Connexion réussie!")
        
        return data
    
    # ==================== UTILISATEUR ====================
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        Récupère les informations de l'utilisateur connecté
        
        Returns:
            Dict avec les infos utilisateur
        """
        response = self.session.get(f"{self.BASE_URL}/async/client/current/")
        response.raise_for_status()
        data = response.json()
        
        # Sauvegarder l'ID client
        if 'id' in data:
            self.client_id = data['id']
        
        return data
    
    def update_user(self, **fields) -> Dict[str, Any]:
        """
        Met à jour les informations de l'utilisateur
        
        Args:
            **fields: Champs à mettre à jour (first_name, last_name, etc.)
            
        Returns:
            Dict avec les infos mises à jour
        """
        if not self.client_id:
            user = self.get_current_user()
            self.client_id = user['id']
        
        response = self.session.patch(
            f"{self.BASE_URL}/client/v2/{self.client_id}/",
            json=fields
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== PAIEMENTS ====================
    
    def get_meal_voucher_cards(self) -> List[Dict[str, Any]]:
        """
        Récupère les cartes tickets restaurant
        
        Returns:
            Liste des cartes
        """
        response = self.session.get(f"{self.BASE_URL}/payments/meal-voucher-card/")
        response.raise_for_status()
        return response.json()
    
    # ==================== ENTREPRISES ====================
    
    def get_companies(self, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
        """
        Liste des entreprises
        
        Args:
            page: Numéro de page
            page_size: Taille de page
            
        Returns:
            Dict avec results, count, etc.
        """
        response = self.session.get(
            f"{self.BASE_URL}/company/",
            params={'page': page, 'ps': page_size}
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== FRIGO ====================
    
    def get_fridge(self) -> Dict[str, Any]:
        """
        Récupère les informations du frigo
        
        Returns:
            Dict avec les infos du frigo
        """
        response = self.session.get(f"{self.BASE_URL}/fridge/")
        response.raise_for_status()
        return response.json()
    
    # ==================== CANTINE / MENU ====================
    
    def get_store_menu(self, store_id: int, date: str = None) -> Dict[str, Any]:
        """
        Récupère le menu d'une cantine pour une date
        
        Args:
            store_id: ID de la cantine (ex: 2051)
            date: Date au format YYYY-MM-DD (défaut: aujourd'hui)
            
        Returns:
            Dict avec le menu
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.session.get(
            f"{self.BASE_URL}/ondemand/stores/{store_id}/menu/",
            params={'when': date}
        )
        response.raise_for_status()
        return response.json()
    
    def get_store_cart(self, store_id: int, date: str = None) -> Dict[str, Any]:
        """
        Récupère le panier pour une cantine
        
        Args:
            store_id: ID de la cantine
            date: Date au format YYYY-MM-DD
            
        Returns:
            Dict avec le panier
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.session.get(
            f"{self.BASE_URL}/ondemand/stores/{store_id}/cart/",
            params={'when': date}
        )
        response.raise_for_status()
        return response.json()
    
    def get_store_opening(self, store_id: int) -> Dict[str, Any]:
        """
        Récupère les horaires d'ouverture d'une cantine
        
        Args:
            store_id: ID de la cantine
            
        Returns:
            Dict avec les horaires
        """
        response = self.session.get(
            f"{self.BASE_URL}/ondemand/stores/{store_id}/opening/"
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== HELPERS ====================
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        try:
            self.get_current_user()
            return True
        except:
            return False


# ==================== EXEMPLES D'UTILISATION ====================

def main():
    """Exemples d'utilisation"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🍽️  CLIENT API FOODLES - EXEMPLES D'UTILISATION                  ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Initialiser avec des cookies existants
    api = FoodlesRealAPI(
        session_id="jflffcai4qqen1dqvmznt4gxfzu2nb14",
        csrf_token="hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    )
    
    # Ou se connecter avec email/password
    # api = FoodlesRealAPI()
    # api.login("votre@email.com", "votrepassword")
    
    print("1️⃣  Informations utilisateur")
    print("-" * 80)
    try:
        user = api.get_current_user()
        print(f"   ✅ Connecté en tant que: {user.get('first_name')} {user.get('last_name')}")
        print(f"   📧 Email: {user.get('email')}")
        print(f"   🆔 ID Client: {user.get('id')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print(f"\n2️⃣  Cartes tickets restaurant")
    print("-" * 80)
    try:
        cards = api.get_meal_voucher_cards()
        if cards:
            for card in cards:
                print(f"   💳 {card.get('brand')}: {card.get('balance')}€")
        else:
            print("   ℹ️  Aucune carte enregistrée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print(f"\n3️⃣  Informations frigo")
    print("-" * 80)
    try:
        fridge = api.get_fridge()
        print(f"   ✅ Frigo récupéré:")
        print(f"   📦 Données: {len(str(fridge))} caractères")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print(f"\n4️⃣  Horaires cantine (ID: 2051)")
    print("-" * 80)
    try:
        opening = api.get_store_opening(2051)
        print(f"   ✅ Horaires récupérés:")
        print(f"   🕐 Ouvert: {opening.get('is_open', 'inconnu')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print(f"\n5️⃣  Menu du jour (ID: 2051)")
    print("-" * 80)
    try:
        menu = api.get_store_menu(2051)
        print(f"   ✅ Menu récupéré")
        if 'items' in menu:
            print(f"   🍽️  {len(menu['items'])} produits disponibles")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"   ⚠️  Menu non disponible (403 Forbidden)")
            print(f"   ℹ️  La cantine pourrait être fermée ou le service indisponible")
        else:
            print(f"   ❌ Erreur: {e}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Tests terminés!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
