#!/usr/bin/env python3
"""
Automation Playwright pour découvrir les vraies APIs en simulant des interactions.
Ce script ouvre le navigateur et enregistre TOUTES les requêtes pendant les actions.
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
from pathlib import Path

def capture_real_interactions():
    """Capture les requêtes pendant une vraie interaction utilisateur"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║   🎬 CAPTURE DES APIs RÉELLES PAR INTERACTION AUTOMATISÉE            ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print("""
Ce script va:
  1. Ouvrir Chrome avec votre session Foodles
  2. Naviguer sur le frigo
  3. SIMULER un clic sur un produit
  4. Capturer TOUTES les requêtes déclenchées
  5. Sauvegarder les vraies APIs découvertes
    """)
    
    # Configuration des cookies avec TOUS les paramètres nécessaires
    cookies = [
        {
            'name': 'sessionid',
            'value': 'jflffcai4qqen1dqvmznt4gxfzu2nb14',
            'domain': 'app.foodles.co',
            'path': '/',
            'httpOnly': True,
            'secure': True,
            'sameSite': 'Lax'
        },
        {
            'name': 'csrftoken',
            'value': 'hCykn22T0BFnO5COVjV7nftJmaH8mcjZ',
            'domain': 'app.foodles.co',
            'path': '/',
            'httpOnly': False,
            'secure': True,
            'sameSite': 'Lax'
        },
        {
            'name': 'isloggedin',
            'value': '1',
            'domain': 'app.foodles.co',
            'path': '/',
            'httpOnly': False,
            'secure': False,
            'sameSite': 'Lax'
        }
    ]
    
    # Stockage des requêtes
    all_requests = []
    api_calls = []
    
    def on_request(request):
        """Callback pour chaque requête"""
        url = request.url
        method = request.method
        
        # Filtrer les ressources statiques
        if any(ext in url for ext in ['.js', '.css', '.woff', '.ttf', '.png', '.jpg', '.svg', '.ico']):
            return
        
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'method': method,
            'headers': dict(request.headers),
            'post_data': request.post_data if request.method == 'POST' else None
        }
        
        all_requests.append(request_data)
        
        # Identifier les appels API intéressants
        if any(keyword in url.lower() for keyword in ['api', 'product', 'cart', 'order', 'canteen']):
            if 'datadog' not in url and 'segment' not in url and 'intercom' not in url:
                api_calls.append(request_data)
                print(f"   🎯 API capturée: {method} {url}")
    
    def on_response(response):
        """Callback pour chaque réponse"""
        url = response.url
        
        # Filtrer
        if any(ext in url for ext in ['.js', '.css', '.woff', '.ttf', '.png', '.jpg', '.svg', '.ico']):
            return
        
        if any(keyword in url.lower() for keyword in ['api', 'product', 'cart', 'order']):
            if 'datadog' not in url and 'segment' not in url and 'intercom' not in url:
                status = response.status
                print(f"   ✅ {status} {url}")
                
                # Essayer de récupérer le corps de la réponse
                try:
                    body = response.text()
                    if body and len(body) < 50000:  # Limiter la taille
                        # Ajouter au dernier request correspondant
                        for req in reversed(api_calls):
                            if req['url'] == url:
                                req['response_status'] = status
                                req['response_body'] = body
                                break
                except:
                    pass
    
    with sync_playwright() as p:
        print("🚀 Lancement de Chrome...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Ajouter les cookies
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        # Activer les callbacks
        page.on("request", on_request)
        page.on("response", on_response)
        
        print("\n📍 Navigation vers le frigo...")
        page.goto("https://app.foodles.co/canteen/fridge")
        page.wait_for_load_state("networkidle")
        
        print("\n⏳ Attente du chargement initial (3 secondes)...")
        page.wait_for_timeout(3000)
        
        # Vérifier l'authentification
        print("\n🔐 Vérification de l'authentification...")
        current_url = page.url
        if '/login' in current_url or '/landing' in current_url:
            print("\n⚠️  ❌ VOUS N'ÊTES PAS AUTHENTIFIÉ !")
            print("\n   La page a redirigé vers:", current_url)
            print("\n   🔧 SOLUTION:")
            print("      1. Laissez le navigateur OUVERT")
            print("      2. Connectez-vous MANUELLEMENT")
            print("      3. Naviguez sur le site normalement")
            print("      4. Le script continuera à capturer automatiquement\n")
            input("   ⏸️  Appuyez sur ENTRÉE une fois connecté...")
            page.goto("https://app.foodles.co/canteen/fridge")
            page.wait_for_load_state("networkidle")
        else:
            print("   ✅ Authentification OK!")
        
        # Essayer de cliquer sur un produit
        print("\n🖱️  Recherche d'un produit à cliquer...")
        try:
            # Plusieurs sélecteurs possibles pour un produit
            selectors = [
                '[data-testid="product-card"]',
                '[class*="product"]',
                'a[href*="/product/"]',
                'button[class*="product"]',
                '[role="button"]'
            ]
            
            product_found = False
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   ✅ Produit trouvé avec: {selector}")
                        print("   🖱️  Clic sur le produit...")
                        element.click()
                        product_found = True
                        break
                except:
                    continue
            
            if product_found:
                print("   ⏳ Attente des requêtes API (5 secondes)...")
                page.wait_for_timeout(5000)
            else:
                print("   ⚠️  Aucun produit cliquable trouvé, on continue quand même...")
        
        except Exception as e:
            print(f"   ⚠️  Erreur lors du clic: {e}")
        
        # Essayer de voir le panier
        print("\n🛒 Recherche du panier...")
        try:
            cart_selectors = [
                '[data-testid="cart"]',
                '[aria-label*="cart"]',
                '[class*="cart"]',
                'a[href*="/cart"]'
            ]
            
            for selector in cart_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   ✅ Panier trouvé: {selector}")
                        element.click()
                        page.wait_for_timeout(3000)
                        break
                except:
                    continue
        except Exception as e:
            print(f"   ⚠️  Impossible d'accéder au panier: {e}")
        
        print("\n⏳ Capture finale (2 secondes)...")
        page.wait_for_timeout(2000)
        
        print("\n🔒 Fermeture du navigateur...")
        browser.close()
    
    # Sauvegarder les résultats
    print("\n💾 Sauvegarde des résultats...")
    
    output_dir = Path("interaction_capture")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder toutes les requêtes
    with open(output_dir / f"all_requests_{timestamp}.json", 'w') as f:
        json.dump(all_requests, f, indent=2)
    
    # Sauvegarder les API calls
    with open(output_dir / f"api_calls_{timestamp}.json", 'w') as f:
        json.dump(api_calls, f, indent=2)
    
    # Rapport
    report = {
        'timestamp': timestamp,
        'total_requests': len(all_requests),
        'api_calls': len(api_calls),
        'unique_urls': list(set(req['url'] for req in api_calls))
    }
    
    with open(output_dir / f"report_{timestamp}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Résultats sauvegardés dans: {output_dir}/")
    print(f"   • all_requests_{timestamp}.json ({len(all_requests)} requêtes)")
    print(f"   • api_calls_{timestamp}.json ({len(api_calls)} appels API)")
    print(f"   • report_{timestamp}.json")
    
    # Afficher le résumé
    print(f"\n\n╔════════════════════════════════════════════════════════════════════════╗")
    print(f"║     📊 RÉSULTATS DE LA CAPTURE                                       ║")
    print(f"╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"Total requêtes capturées: {len(all_requests)}")
    print(f"Appels API identifiés: {len(api_calls)}")
    
    if api_calls:
        print(f"\n🎯 APIS DÉCOUVERTES:\n")
        
        unique_apis = {}
        for call in api_calls:
            key = f"{call['method']} {call['url']}"
            if key not in unique_apis:
                unique_apis[key] = {
                    'method': call['method'],
                    'url': call['url'],
                    'count': 0,
                    'has_response': 'response_body' in call
                }
            unique_apis[key]['count'] += 1
        
        for i, (key, info) in enumerate(unique_apis.items(), 1):
            print(f"{i}. {info['method']} {info['url']}")
            print(f"   Appelé {info['count']} fois")
            if info['has_response']:
                print(f"   ✅ Réponse capturée")
    
    else:
        print("\n⚠️  Aucune API spécifique détectée")
        print("\nCela confirme que Foodles utilise uniquement Server-Side Rendering.")


if __name__ == "__main__":
    capture_real_interactions()
