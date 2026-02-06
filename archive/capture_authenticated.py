#!/usr/bin/env python3
"""
Script amélioré pour capturer les vraies APIs avec authentification vérifiée.
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
from pathlib import Path

def capture_with_auth():
    """Capture les APIs avec vérification d'authentification"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║   🔐 CAPTURE DES APIs AVEC AUTHENTIFICATION VÉRIFIÉE                ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Cookies d'authentification CORRECTS
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
        """Callback pour capturer les requêtes"""
        url = request.url
        method = request.method
        
        # Filtrer les ressources statiques
        if any(ext in url for ext in ['.js', '.css', '.woff', '.ttf', '.png', '.jpg', '.svg', '.ico', '.webp']):
            return
        
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'method': method,
            'headers': dict(request.headers),
            'post_data': request.post_data if method == 'POST' else None
        }
        
        all_requests.append(request_data)
        
        # API calls intéressants
        if 'foodles' in url.lower() and not any(x in url for x in ['datadog', 'segment', 'intercom', 'analytics']):
            if any(keyword in url.lower() for keyword in ['api', 'product', 'cart', 'order', 'canteen', 'fridge']):
                api_calls.append(request_data)
                print(f"   📡 {method} {url[:100]}")
    
    def on_response(response):
        """Callback pour capturer les réponses"""
        url = response.url
        status = response.status
        
        if 'foodles' in url.lower() and not any(x in url for x in ['datadog', 'segment', 'intercom']):
            if any(keyword in url.lower() for keyword in ['api', 'product', 'cart', 'order']):
                print(f"   ✅ {status} {url[:100]}")
                
                # Ajouter la réponse au request correspondant
                try:
                    body = response.text()
                    if body and len(body) < 100000:
                        for req in reversed(api_calls):
                            if req['url'] == url:
                                req['response_status'] = status
                                req['response_body'] = body[:10000]  # Limiter la taille
                                break
                except:
                    pass
    
    with sync_playwright() as p:
        print("🚀 Lancement de Chrome...")
        browser = p.chromium.launch(headless=False)
        
        # Créer le contexte avec les cookies
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Ajouter les cookies AVANT d'ouvrir la page
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.on('request', on_request)
        page.on('response', on_response)
        
        print("\n📍 Navigation vers Foodles...")
        page.goto('https://app.foodles.co/canteen/fridge')
        page.wait_for_load_state('networkidle')
        
        print("\n🔐 Vérification de l'authentification...")
        current_url = page.url
        
        if '/login' in current_url or '/landing' in current_url:
            print(f"\n❌ VOUS N'ÊTES PAS AUTHENTIFIÉ!")
            print(f"   URL actuelle: {current_url}")
            print("\n💡 SOLUTION:")
            print("   1. Le navigateur reste OUVERT")
            print("   2. Connectez-vous MANUELLEMENT")
            print("   3. Allez sur le frigo: https://app.foodles.co/canteen/fridge")
            print("   4. La capture continue automatiquement\n")
            
            input("⏸️  Appuyez sur ENTRÉE une fois connecté et sur /canteen/fridge...")
            
            # Recharger la page
            page.goto('https://app.foodles.co/canteen/fridge')
            page.wait_for_load_state('networkidle')
            print("\n✅ Reprise de la capture!\n")
        else:
            print("✅ Authentification OK! Vous êtes connecté.\n")
        
        # Capturer les requêtes
        print("⏳ Attente initiale (5 secondes)...")
        page.wait_for_timeout(5000)
        
        # Visiter différentes pages
        pages = [
            ('Frigo', '/canteen/fridge'),
            ('Cantine', '/canteen'),
            ('Menu', '/canteen/menu'),
        ]
        
        for page_name, url in pages:
            print(f"\n📄 Visite de: {page_name} ({url})")
            try:
                page.goto(f'https://app.foodles.co{url}')
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(3000)
                
                # Scroll
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"   ⚠️  Erreur: {e}")
        
        # Essayer de cliquer sur un produit
        print("\n🖱️  Tentative d'interaction avec le frigo...")
        try:
            page.goto('https://app.foodles.co/canteen/fridge')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            
            # Chercher un produit cliquable
            selectors = [
                'a[href*="product"]',
                '[data-testid*="product"]',
                'button[class*="product"]',
                'div[class*="ProductCard"]',
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element and element.is_visible():
                        print(f"   ✅ Produit trouvé: {selector}")
                        element.click()
                        page.wait_for_timeout(5000)
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                print("   ⚠️  Aucun produit cliquable détecté (normal si format RSC)")
        except Exception as e:
            print(f"   ⚠️  Erreur d'interaction: {e}")
        
        print("\n⏳ Attente finale (5 secondes) pour capturer les dernières requêtes...")
        page.wait_for_timeout(5000)
        
        print("\n🔒 Fermeture du navigateur...")
        browser.close()
    
    # Sauvegarder les résultats
    print("\n💾 Sauvegarde des résultats...")
    
    output_dir = Path("interaction_capture")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(output_dir / f"all_requests_{timestamp}.json", 'w') as f:
        json.dump(all_requests, f, indent=2)
    
    with open(output_dir / f"api_calls_{timestamp}.json", 'w') as f:
        json.dump(api_calls, f, indent=2)
    
    # Résumé
    print("\n\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     📊 RÉSULTATS DE LA CAPTURE                                       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"Total requêtes capturées: {len(all_requests)}")
    print(f"Appels API identifiés: {len(api_calls)}")
    print(f"\n📁 Résultats dans: {output_dir}/")
    
    if api_calls:
        print(f"\n🎯 APIs DÉCOUVERTES:\n")
        
        unique = {}
        for call in api_calls:
            key = f"{call['method']} {call['url']}"
            if key not in unique:
                unique[key] = {
                    'method': call['method'],
                    'url': call['url'],
                    'count': 0,
                    'has_response': 'response_body' in call
                }
            unique[key]['count'] += 1
        
        for i, (key, info) in enumerate(unique.items(), 1):
            print(f"{i}. {info['method']} {info['url'][:120]}")
            if info['count'] > 1:
                print(f"   Appelé {info['count']} fois")
            if info['has_response']:
                print(f"   ✅ Réponse capturée")
    else:
        print("\n⚠️  Aucune API REST trouvée")
        print("\nCela confirme que Foodles utilise Server-Side Rendering (Next.js RSC)")
        print("Les données sont intégrées directement dans le HTML, pas via APIs séparées.")

if __name__ == "__main__":
    capture_with_auth()
