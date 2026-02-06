"""
Client API pour interagir avec Foodles
"""
import requests
from typing import Dict, Optional, Any
import json


class FoodlesAPI:
    """Client pour interagir avec l'API Foodles"""
    
    BASE_URL = "https://app.foodles.co"
    
    def __init__(self, session_id: str, csrf_token: str):
        """
        Initialiser le client API Foodles
        
        Args:
            session_id: Le sessionid du cookie
            csrf_token: Le csrftoken du cookie
        """
        self.session_id = session_id
        self.csrf_token = csrf_token
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configure la session avec les headers et cookies nécessaires"""
        # Headers de base
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'rsc': '1',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        })
        
        # Cookies
        self.session.cookies.set('sessionid', self.session_id)
        self.session.cookies.set('csrftoken', self.csrf_token)
        self.session.cookies.set('isloggedin', '1')
    
    def get_fridge(self, rsc_param: str = "1d46b") -> Dict[str, Any]:
        """
        Récupère les données du frigo
        
        Args:
            rsc_param: Paramètre RSC (peut varier selon les requêtes)
            
        Returns:
            Les données du frigo
        """
        url = f"{self.BASE_URL}/canteen/fridge"
        params = {'_rsc': rsc_param}
        
        headers = {
            'referer': f'{self.BASE_URL}/canteen/fridge',
            'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(home)%22%2C%7B%22children%22%3A%5B%22canteen%22%2C%7B%22children%22%3A%5B%22fridge%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2Cnull%2C%22refetch%22%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D',
            'priority': 'u=1, i'
        }
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def set_delivery_settings(self, canteen_id: int, canteen_name: str, delivery_date: str):
        """
        Configure les paramètres de livraison
        
        Args:
            canteen_id: ID de la cantine
            canteen_name: Nom de la cantine
            delivery_date: Date de livraison (format: YYYY-MM-DD)
        """
        self.session.cookies.set('foodles-delivery-canteen', 
                                f'{{"id":{canteen_id},"name":"{canteen_name}"}}')
        self.session.cookies.set('foodles-delivery-date', delivery_date)
    
    def get_canteen_menu(self, rsc_param: str = "1d46b") -> Dict[str, Any]:
        """
        Récupère le menu de la cantine
        
        Args:
            rsc_param: Paramètre RSC
            
        Returns:
            Les données du menu
        """
        url = f"{self.BASE_URL}/canteen/menu"
        params = {'_rsc': rsc_param}
        
        headers = {
            'referer': f'{self.BASE_URL}/canteen/menu',
            'next-router-state-tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22(home)%22%2C%7B%22children%22%3A%5B%22canteen%22%2C%7B%22children%22%3A%5B%22menu%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2Cnull%2C%22refetch%22%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D%7D%2Cnull%2Cnull%5D'
        }
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def get_cart(self, rsc_param: str = "1d46b") -> Dict[str, Any]:
        """
        Récupère le panier
        
        Args:
            rsc_param: Paramètre RSC
            
        Returns:
            Les données du panier
        """
        url = f"{self.BASE_URL}/cart"
        params = {'_rsc': rsc_param}
        
        headers = {
            'referer': f'{self.BASE_URL}/cart'
        }
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return self._parse_response(response)
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse la réponse de l'API
        
        Args:
            response: Réponse HTTP
            
        Returns:
            Les données parsées
        """
        # L'API Foodles utilise un format spécial avec RSC (React Server Components)
        # Pour l'instant, on retourne le contenu brut
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            return response.json()
        else:
            # Format RSC - contenu texte spécial
            return {
                'raw_content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
    
    def make_request(self, endpoint: str, method: str = "GET", 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None,
                     headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Effectue une requête personnalisée à l'API
        
        Args:
            endpoint: L'endpoint de l'API (ex: /canteen/fridge)
            method: Méthode HTTP (GET, POST, etc.)
            params: Paramètres de query string
            data: Données à envoyer (pour POST/PUT)
            headers: Headers additionnels
            
        Returns:
            La réponse de l'API
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=request_headers
        )
        response.raise_for_status()
        
        return self._parse_response(response)
