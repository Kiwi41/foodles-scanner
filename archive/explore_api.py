"""
Explorateur d'API Foodles - Teste différents endpoints
"""
from foodles_api import FoodlesAPI
from config import config
from rsc_parser import parse_rsc_response, RSCParser
from dotenv import load_dotenv
import json
from datetime import datetime


class FoodlesExplorer:
    """Explorateur pour découvrir les endpoints de l'API Foodles"""
    
    def __init__(self, api: FoodlesAPI):
        self.api = api
        self.results = []
    
    def test_endpoint(self, endpoint: str, params: dict = None, method: str = "GET") -> dict:
        """
        Teste un endpoint et retourne les résultats
        
        Args:
            endpoint: L'endpoint à tester
            params: Paramètres optionnels
            method: Méthode HTTP
            
        Returns:
            Résultats du test
        """
        try:
            print(f"\n🔍 Test: {method} {endpoint}")
            if params:
                print(f"   Params: {params}")
            
            response = self.api.make_request(endpoint, method=method, params=params)
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'params': params,
                'status': 'success',
                'status_code': response.get('status_code', 200),
                'has_content': 'raw_content' in response or bool(response),
                'timestamp': datetime.now().isoformat()
            }
            
            # Analyser si c'est du contenu RSC
            if 'raw_content' in response:
                parser = RSCParser(response['raw_content'])
                result['summary'] = parser.get_summary()
                result['json_objects_count'] = len(parser.extract_all_json_objects())
            
            print(f"   ✅ Succès - Status: {result['status_code']}")
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                'endpoint': endpoint,
                'method': method,
                'params': params,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"   ❌ Erreur: {str(e)}")
            self.results.append(result)
            return result
    
    def explore_common_endpoints(self):
        """Explore les endpoints communs d'une application e-commerce"""
        print("=" * 60)
        print("🚀 EXPLORATION DES ENDPOINTS FOODLES")
        print("=" * 60)
        
        endpoints = [
            # Pages principales
            ("/canteen/fridge", {"_rsc": "1d46b"}),
            ("/canteen", {"_rsc": "1d46b"}),
            ("/", {"_rsc": "1d46b"}),
            
            # API endpoints possibles
            ("/api/products", None),
            ("/api/menu", None),
            ("/api/cart", None),
            ("/api/orders", None),
            ("/api/user", None),
            ("/api/canteen", None),
            ("/api/canteens", None),
            
            # Pages utilisateur
            ("/account", {"_rsc": "1d46b"}),
            ("/profile", {"_rsc": "1d46b"}),
            ("/orders", {"_rsc": "1d46b"}),
            ("/order-history", {"_rsc": "1d46b"}),
            
            # Pages canteen
            ("/canteen/products", {"_rsc": "1d46b"}),
            ("/canteen/meals", {"_rsc": "1d46b"}),
            ("/canteen/delivery", {"_rsc": "1d46b"}),
        ]
        
        for endpoint, params in endpoints:
            self.test_endpoint(endpoint, params)
        
        return self.results
    
    def save_results(self, filename: str = "api_exploration.json"):
        """Sauvegarde les résultats de l'exploration"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'exploration_date': datetime.now().isoformat(),
                'total_endpoints': len(self.results),
                'successful': len([r for r in self.results if r['status'] == 'success']),
                'failed': len([r for r in self.results if r['status'] == 'error']),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Résultats sauvegardés dans: {filename}")
    
    def print_summary(self):
        """Affiche un résumé de l'exploration"""
        successful = [r for r in self.results if r['status'] == 'success']
        failed = [r for r in self.results if r['status'] == 'error']
        
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'EXPLORATION")
        print("=" * 60)
        print(f"Total d'endpoints testés: {len(self.results)}")
        print(f"✅ Succès: {len(successful)}")
        print(f"❌ Échecs: {len(failed)}")
        
        if successful:
            print(f"\n🎯 Endpoints fonctionnels:")
            for r in successful:
                params_str = f" (params: {r['params']})" if r['params'] else ""
                print(f"   - {r['endpoint']}{params_str}")


def main():
    # Charger la configuration
    load_dotenv()
    
    # Créer le client API
    session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
    csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    api = FoodlesAPI(session_id, csrf_token)
    
    # Configurer les paramètres de livraison
    api.set_delivery_settings(
        canteen_id=2051,
        canteen_name="Worldline Copernic",
        delivery_date="2026-01-30"
    )
    
    # Explorer l'API
    explorer = FoodlesExplorer(api)
    explorer.explore_common_endpoints()
    
    # Afficher et sauvegarder les résultats
    explorer.print_summary()
    explorer.save_results()


if __name__ == "__main__":
    main()
