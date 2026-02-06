#!/usr/bin/env python3
"""
Script minimal pour capturer les APIs RÉELLES après connexion manuelle.
Pas de cookies prédéfinis - connexion 100% manuelle.
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
from pathlib import Path

def capture_manual_login():
    """Capture avec connexion manuelle de l'utilisateur"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║   🎯 CAPTURE DES VRAIES APIs - CONNEXION MANUELLE                   ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print("📋 INSTRUCTIONS:")
    print("   1. Le navigateur Chrome va s'ouvrir")
    print("   2. Connectez-vous MANUELLEMENT sur Foodles")
    print("   3. Naviguez normalement (frigo, produits, panier...)")
    print("   4. Toutes les APIs seront capturées automatiquement")
    print("   5. Fermez le navigateur quand vous avez fini\n")
    
    input("⏸️  Appuyez sur ENTRÉE pour démarrer...")
    
    # Stockage
    all_requests = []
    api_calls = []
    
    def on_request(request):
        """Capture toutes les requêtes"""
        url = request.url
        method = request.method
        
        # Ignorer les ressources statiques
        if any(ext in url for ext in ['.js', '.css', '.woff', '.ttf', '.png', '.jpg', '.svg', '.ico', '.webp', '.woff2']):
            return
        
        request_data = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'method': method,
            'headers': dict(request.headers),
            'resource_type': request.resource_type,
        }
        
        # Capturer le body POST
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                request_data['post_data'] = request.post_data
            except:
                pass
        
        all_requests.append(request_data)
        
        # Identifier les APIs Foodles
        if 'api.foodles.co' in url or ('app.foodles.co' in url and any(k in url for k in ['/api/', 'product', 'cart', 'order'])):
            api_calls.append(request_data)
            print(f"   📡 {method} {url}")
    
    def on_response(response):
        """Capture les réponses"""
        url = response.url
        status = response.status
        
        # Seulement les APIs Foodles
        if 'api.foodles.co' in url or ('app.foodles.co' in url and any(k in url for k in ['/api/', 'product', 'cart', 'order'])):
            print(f"   ✅ {status} {url}")
            
            # Essayer de capturer le body
            try:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    body = response.text()
                    if len(body) < 500000:  # Max 500KB
                        # Trouver la requête correspondante
                        for req in reversed(api_calls):
                            if req['url'] == url:
                                req['response'] = {
                                    'status': status,
                                    'headers': dict(response.headers),
                                    'body': body
                                }
                                break
            except Exception as e:
                pass
    
    with sync_playwright() as p:
        print("\n🚀 Ouverture de Chrome...")
        
        # Lancer avec un profil utilisateur pour garder la session
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # Activer la capture
        page.on('request', on_request)
        page.on('response', on_response)
        
        print("\n📍 Navigation vers Foodles...")
        page.goto('https://app.foodles.co')
        
        print("\n✋ À VOUS DE JOUER!")
        print("   • Connectez-vous")
        print("   • Naviguez sur le site")
        print("   • Cliquez sur des produits")
        print("   • Ajoutez au panier si possible")
        print("   • Les APIs sont capturées en temps réel")
        print("\n   Fermez le navigateur quand vous avez terminé.\n")
        
        # Attendre que l'utilisateur ferme le navigateur
        try:
            while True:
                page.wait_for_timeout(1000)
        except:
            pass
    
    print("\n\n💾 Sauvegarde des résultats...")
    
    # Créer le dossier de sortie
    output_dir = Path("manual_capture")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sauvegarder tout
    with open(output_dir / f"all_requests_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(all_requests, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / f"api_calls_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(api_calls, f, indent=2, ensure_ascii=False)
    
    # Rapport détaillé
    report = {
        'timestamp': timestamp,
        'total_requests': len(all_requests),
        'api_calls_count': len(api_calls),
        'unique_endpoints': []
    }
    
    # Grouper par endpoint unique
    endpoints = {}
    for call in api_calls:
        url = call['url']
        method = call['method']
        key = f"{method} {url}"
        
        if key not in endpoints:
            endpoints[key] = {
                'method': method,
                'url': url,
                'count': 0,
                'has_response': 'response' in call,
                'status_codes': []
            }
        
        endpoints[key]['count'] += 1
        if 'response' in call:
            status = call['response']['status']
            if status not in endpoints[key]['status_codes']:
                endpoints[key]['status_codes'].append(status)
    
    report['unique_endpoints'] = list(endpoints.values())
    
    with open(output_dir / f"report_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Affichage du résumé
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🎉 CAPTURE TERMINÉE !                                            ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"📊 STATISTIQUES:")
    print(f"   • Total requêtes: {len(all_requests)}")
    print(f"   • APIs Foodles: {len(api_calls)}")
    print(f"   • Endpoints uniques: {len(endpoints)}")
    
    print(f"\n📁 Fichiers sauvegardés dans: {output_dir}/")
    print(f"   • all_requests_{timestamp}.json")
    print(f"   • api_calls_{timestamp}.json")
    print(f"   • report_{timestamp}.json")
    
    if api_calls:
        print(f"\n🎯 ENDPOINTS API DÉCOUVERTS:\n")
        
        for i, (key, info) in enumerate(sorted(endpoints.items()), 1):
            print(f"{i}. {info['method']} {info['url']}")
            if info['count'] > 1:
                print(f"   → Appelé {info['count']} fois")
            if info['status_codes']:
                print(f"   → Status: {', '.join(map(str, info['status_codes']))}")
            if info['has_response']:
                print(f"   ✅ Réponse JSON capturée")
            print()
        
        # Analyser les endpoints découverts
        print("\n💡 ANALYSE:")
        
        api_endpoints = [e for e in endpoints.values() if 'api.foodles.co/api/' in e['url']]
        if api_endpoints:
            print(f"\n✅ API Backend trouvée ! ({len(api_endpoints)} endpoints)")
            print("   Ces APIs peuvent être utilisées directement dans notre client Python!")
        
        product_endpoints = [e for e in endpoints.values() if 'product' in e['url'].lower()]
        if product_endpoints:
            print(f"\n✅ APIs Produits trouvées ! ({len(product_endpoints)} endpoints)")
        
        cart_endpoints = [e for e in endpoints.values() if 'cart' in e['url'].lower() or 'panier' in e['url'].lower()]
        if cart_endpoints:
            print(f"\n✅ APIs Panier trouvées ! ({len(cart_endpoints)} endpoints)")
        
        order_endpoints = [e for e in endpoints.values() if 'order' in e['url'].lower() or 'commande' in e['url'].lower()]
        if order_endpoints:
            print(f"\n✅ APIs Commande trouvées ! ({len(order_endpoints)} endpoints)")
    
    else:
        print("\n⚠️  Aucune API capturée")
        print("   Assurez-vous d'avoir navigué sur le site après connexion")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        capture_manual_login()
    except KeyboardInterrupt:
        print("\n\n⚠️  Capture interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
