#!/usr/bin/env python3
"""
Test des nouveaux endpoints découverts dans le code JavaScript.
"""

import requests
from config import FoodlesConfig
import json

def test_endpoints():
    """Teste les endpoints découverts"""
    
    config = FoodlesConfig()
    config.set_credentials(
        "jflffcai4qqen1dqvmznt4gxfzu2nb14",
        "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    )
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://app.foodles.co/canteen/fridge',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    cookies = {
        'sessionid': config.session_id,
        'csrftoken': config.csrf_token,
        'isloggedin': '1'
    }
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🧪 TEST DES NOUVEAUX ENDPOINTS DÉCOUVERTS                        ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Liste des endpoints à tester
    endpoints = [
        ("GET", "https://api.foodles.co/api", "API Backend"),
        ("GET", "https://app.foodles.co/canteen/counter/cart", "Panier (Counter)"),
        ("GET", "https://app.foodles.co/canteen/counter", "Counter"),
        ("GET", "https://app.foodles.co/canteen/counter/closed", "Counter Closed"),
        ("GET", "https://app.foodles.co/canteen/qrcode", "QR Code"),
        ("GET", "https://app.foodles.co/canteen/select", "Sélection Cantine"),
        ("GET", "https://cdn.foodles.co", "CDN"),
    ]
    
    results = []
    
    for i, (method, url, description) in enumerate(endpoints, 1):
        print(f"\n{i}. Test: {description}")
        print(f"   URL: {url}")
        print(f"   Méthode: {method}")
        
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=10,
                    allow_redirects=False
                )
            else:
                response = requests.post(
                    url,
                    headers=headers,
                    cookies=cookies,
                    timeout=10,
                    allow_redirects=False
                )
            
            status = response.status_code
            content_type = response.headers.get('Content-Type', '')
            size = len(response.content)
            
            print(f"   Status: {status}")
            print(f"   Content-Type: {content_type}")
            print(f"   Taille: {size} octets")
            
            result = {
                'description': description,
                'url': url,
                'status': status,
                'content_type': content_type,
                'size': size,
                'success': 200 <= status < 300
            }
            
            # Afficher un aperçu si c'est du JSON
            if 'json' in content_type.lower():
                try:
                    data = response.json()
                    print(f"   ✅ JSON valide!")
                    if isinstance(data, dict):
                        print(f"      Clés: {list(data.keys())[:10]}")
                        result['preview'] = str(data)[:200]
                    elif isinstance(data, list):
                        print(f"      Liste de {len(data)} éléments")
                        if data:
                            print(f"      Premier élément: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                except:
                    pass
            
            # Pour les redirections
            if 300 <= status < 400:
                location = response.headers.get('Location', '')
                print(f"   🔄 Redirection vers: {location}")
                result['redirect'] = location
            
            # Pour les erreurs
            if status >= 400:
                print(f"   ❌ Erreur {status}")
                if size < 1000:
                    print(f"      Message: {response.text[:200]}")
            
            results.append(result)
            
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
            results.append({
                'description': description,
                'url': url,
                'status': 'timeout',
                'success': False
            })
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results.append({
                'description': description,
                'url': url,
                'status': 'error',
                'error': str(e),
                'success': False
            })
    
    # Résumé
    print(f"\n\n╔════════════════════════════════════════════════════════════════════════╗")
    print(f"║     📊 RÉSUMÉ DES TESTS                                              ║")
    print(f"╚════════════════════════════════════════════════════════════════════════╝\n")
    
    successful = [r for r in results if r.get('success')]
    print(f"✅ Endpoints fonctionnels: {len(successful)}/{len(results)}")
    
    if successful:
        print(f"\n🎯 ENDPOINTS ACCESSIBLES:\n")
        for r in successful:
            print(f"   • {r['description']}")
            print(f"     {r['url']}")
            print(f"     Status {r['status']}, {r['content_type']}, {r['size']} octets")
            if r.get('preview'):
                print(f"     Aperçu: {r['preview']}")
    
    # Tests supplémentaires sur l'API backend
    if any(r['url'] == 'https://api.foodles.co/api' and r.get('success') for r in results):
        print(f"\n\n🔍 L'API Backend est accessible ! Testons des endpoints spécifiques...")
        test_api_endpoints(headers, cookies)


def test_api_endpoints(headers, cookies):
    """Teste différents endpoints sur l'API backend"""
    
    base_url = "https://api.foodles.co/api"
    
    # Endpoints potentiels à tester
    api_endpoints = [
        "/products",
        "/products/fridge",
        "/cart",
        "/cart/items",
        "/orders",
        "/canteen/2051",
        "/canteen/2051/products",
        "/canteen/2051/fridge",
        "/user",
        "/user/cart",
        "/me",
        "/v1/products",
        "/v1/cart",
    ]
    
    print(f"\n   Testing {len(api_endpoints)} potential API endpoints...")
    
    found_endpoints = []
    
    for endpoint in api_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=5,
                allow_redirects=False
            )
            
            if response.status_code != 404:
                found_endpoints.append({
                    'endpoint': endpoint,
                    'status': response.status_code,
                    'content_type': response.headers.get('Content-Type', ''),
                    'size': len(response.content)
                })
                print(f"   ✅ {endpoint} → {response.status_code}")
        except:
            pass
    
    if found_endpoints:
        print(f"\n   🎉 {len(found_endpoints)} endpoints trouvés sur l'API backend!")
        for ep in found_endpoints:
            print(f"\n   • {ep['endpoint']}")
            print(f"     Status: {ep['status']}, Type: {ep['content_type']}, Taille: {ep['size']}")
    else:
        print(f"\n   ❌ Aucun endpoint standard trouvé sur l'API backend")


if __name__ == "__main__":
    test_endpoints()
