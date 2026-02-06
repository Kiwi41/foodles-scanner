#!/usr/bin/env python3
"""
Script pour explorer le problème 403 sur les endpoints menu/cart.
Teste différentes configurations et headers.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from foodles_real_api import FoodlesRealAPI
from datetime import datetime
import time

def test_endpoint(api, method, endpoint, payload=None, description=""):
    """Teste un endpoint avec différentes configurations"""
    print(f"\n{'='*80}")
    print(f"🧪 Test: {description}")
    print(f"   URL: {endpoint}")
    print(f"   Méthode: {method}")
    
    try:
        base_url = "https://api.foodles.co/api"
        if method == 'GET':
            response = api.session.get(f"{base_url}{endpoint}")
        elif method == 'POST':
            response = api.session.post(f"{base_url}{endpoint}", json=payload)
        
        print(f"   ✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📦 Réponse JSON: {len(str(data))} caractères")
                return True, data
            except:
                print(f"   📦 Réponse texte: {len(response.text)} caractères")
                return True, response.text
        elif response.status_code == 403:
            print(f"   ❌ 403 Forbidden")
            print(f"   📄 Réponse: {response.text[:200]}")
            return False, None
        else:
            print(f"   ⚠️  Autre status")
            print(f"   📄 Réponse: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"   💥 Erreur: {e}")
        return False, None

def main():
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🔍 EXPLORATION DES ENDPOINTS BLOQUÉS (403)                         ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    api = FoodlesRealAPI()
    
    # Vérifier l'authentification d'abord
    print("🔐 Test d'authentification...")
    try:
        user = api.get_current_user()
        print(f"✅ Authentifié en tant que: {user.get('email', 'N/A')}")
        print(f"   Client ID: {user.get('id')}")
        store_id = user.get('canteen', {}).get('id', 2051)
        print(f"   Store ID: {store_id}\n")
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        print("💡 Vérifiez vos cookies dans .env\n")
        return
    
    store_id = 2051  # Worldline Copernic
    
    # Test 1: Menu endpoint
    print("\n" + "="*80)
    print("📍 ENDPOINT: /api/ondemand/stores/{id}/menu/")
    print("="*80)
    
    test_endpoint(
        api, 'GET', 
        f'/ondemand/stores/{store_id}/menu/',
        description="Menu standard"
    )
    
    # Test avec différents query params
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/menu/?date={datetime.now().strftime("%Y-%m-%d")}',
        description="Menu avec date du jour"
    )
    
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/menu/?time=12:00',
        description="Menu avec heure"
    )
    
    # Test 2: Cart endpoint
    print("\n" + "="*80)
    print("📍 ENDPOINT: /api/ondemand/stores/{id}/cart/")
    print("="*80)
    
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/cart/',
        description="Panier GET"
    )
    
    test_endpoint(
        api, 'POST',
        f'/ondemand/stores/{store_id}/cart/',
        payload={'product_id': 10400, 'quantity': 1},
        description="Panier POST - Ajout produit"
    )
    
    # Test 3: Opening endpoint (celui-ci marche normalement)
    print("\n" + "="*80)
    print("📍 ENDPOINT: /api/ondemand/stores/{id}/opening/")
    print("="*80)
    
    success, data = test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/opening/',
        description="Horaires d'ouverture"
    )
    
    if success and data:
        print(f"\n   📊 Analyse des horaires:")
        if isinstance(data, dict):
            print(f"   • Clés: {list(data.keys())}")
            if 'is_open' in data:
                print(f"   • Ouvert maintenant: {data['is_open']}")
            if 'next_opening' in data:
                print(f"   • Prochaine ouverture: {data.get('next_opening')}")
            if 'opening_hours' in data:
                print(f"   • Horaires: {data.get('opening_hours')}")
    
    # Test 4: Autres endpoints découverts
    print("\n" + "="*80)
    print("📍 AUTRES ENDPOINTS")
    print("="*80)
    
    test_endpoint(
        api, 'GET',
        '/async/client/current/',
        description="Info client (devrait marcher)"
    )
    
    test_endpoint(
        api, 'GET',
        '/fridge/',
        description="Frigo (devrait marcher)"
    )
    
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/',
        description="Détails du store"
    )
    
    # Test 5: Endpoints possibles non testés
    print("\n" + "="*80)
    print("📍 ENDPOINTS HYPOTHÉTIQUES")
    print("="*80)
    
    test_endpoint(
        api, 'GET',
        '/orders/',
        description="Liste des commandes"
    )
    
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/products/',
        description="Liste des produits du store"
    )
    
    test_endpoint(
        api, 'GET',
        f'/ondemand/stores/{store_id}/categories/',
        description="Catégories du store"
    )
    
    # Résumé
    print("\n" + "="*80)
    print("📋 RÉSUMÉ & RECOMMANDATIONS")
    print("="*80)
    print("""
💡 Hypothèses sur les 403:
   1. Endpoints menu/cart nécessitent peut-être une activation
   2. Peuvent être limités à certaines plages horaires
   3. Peuvent nécessiter des permissions spéciales
   4. Le store peut être en mode 'frigo uniquement'
   
🔧 Solutions à explorer:
   1. Vérifier si store supporte ondemand (vs fridge only)
   2. Tester pendant les horaires d'ouverture du restaurant
   3. Analyser les headers de la vraie app mobile/web
   4. Utiliser playwright pour capturer une vraie commande
   
✅ Fonctionnalités disponibles:
   • Consultation du frigo (/fridge/)
   • Info client (/async/client/current/)
   • Horaires (/ondemand/stores/{id}/opening/)
   • Carte tickets resto (/payments/meal-voucher-card/)
    """)

if __name__ == "__main__":
    main()
