#!/usr/bin/env python3
"""
Script pour capturer les données en fin de journée quand les promos DLC sont actives.
Ce script ouvre le navigateur et attend que vous naviguiez pendant les heures de promo.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

def capture_promo_products():
    """Capture spécifique pour les produits en promo proche expiration"""
    
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║   🎯 CAPTURE DES PROMOS DLC - FIN DE JOURNÉE                         ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print("💡 OBJECTIF:")
    print("   Capturer les données quand les produits en promo DLC sont disponibles")
    print("   (généralement en fin de journée, avant la fermeture)\n")
    
    print("⏰ MEILLEUR MOMENT:")
    print("   • 17h-19h en semaine")
    print("   • Quelques heures avant la fermeture")
    print("   • Quand le frigo affiche des prix réduits\n")
    
    print("📋 CE QUI SERA CAPTURÉ:")
    print("   • Produits avec has_near_expiration_sale = true")
    print("   • Prix réduits")
    print("   • Potentiellement les DLC si exposées\n")
    
    input("⏸️  Appuyez sur ENTRÉE pour démarrer...")
    
    with sync_playwright() as p:
        print("\n🚀 Ouverture de Chrome...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Capturer toutes les requêtes
        api_calls = []
        promo_products = []
        
        def handle_response(response):
            try:
                url = response.url
                
                # Capturer toutes les requêtes API
                if 'api.foodles.co' in url or 'foodles.co/api' in url:
                    try:
                        body = response.json()
                        api_calls.append({
                            'url': url,
                            'method': response.request.method,
                            'status': response.status,
                            'timestamp': datetime.now().isoformat(),
                            'response': body
                        })
                        
                        # Analyser spécifiquement les produits avec promo
                        if 'fridge' in url and isinstance(body, dict):
                            if 'categories' in body:
                                for cat in body['categories']:
                                    for prod in cat.get('products', []):
                                        if prod.get('has_near_expiration_sale'):
                                            promo_products.append({
                                                'id': prod.get('id'),
                                                'name': prod.get('name'),
                                                'price': prod.get('price'),
                                                'category': cat.get('name'),
                                                'has_near_expiration_sale': True,
                                                'captured_at': datetime.now().isoformat()
                                            })
                                            print(f"   🎯 PROMO TROUVÉE: {prod.get('name', 'N/A')[:50]}")
                    except:
                        pass
            except:
                pass
        
        page = context.new_page()
        page.on("response", handle_response)
        
        print("🔗 Navigation vers Foodles...")
        page.goto("https://app.foodles.co/auth/login")
        
        print("\n" + "="*80)
        print("✋ À VOUS DE JOUER!")
        print("="*80)
        print("\n1️⃣  Connectez-vous sur Foodles")
        print("2️⃣  Naviguez vers le frigo")
        print("3️⃣  Vérifiez si des produits ont des prix réduits (promo DLC)")
        print("4️⃣  Cliquez sur ces produits pour voir les détails")
        print("5️⃣  Ajoutez au panier si possible")
        print("\n💡 Le script capture automatiquement toutes les données")
        print("   Fermez le navigateur quand vous avez terminé\n")
        
        # Attendre que l'utilisateur ferme le navigateur
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            # Sauvegarder les résultats
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Sauvegarder toutes les API calls
            api_file = f'manual_capture/promo_capture_{timestamp}.json'
            with open(api_file, 'w', encoding='utf-8') as f:
                json.dump(api_calls, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Sauvegardé: {api_file}")
            print(f"   📊 {len(api_calls)} appels API capturés")
            
            # Sauvegarder spécifiquement les produits promo
            if promo_products:
                promo_file = f'manual_capture/promo_products_{timestamp}.json'
                with open(promo_file, 'w', encoding='utf-8') as f:
                    json.dump(promo_products, f, indent=2, ensure_ascii=False)
                
                print(f"   🎯 {len(promo_products)} produits en promo DLC trouvés!")
                print(f"   💾 Sauvegardés dans: {promo_file}")
                
                # Afficher le résumé
                print("\n" + "="*80)
                print("🎊 PRODUITS EN PROMO CAPTURÉS:")
                print("="*80 + "\n")
                
                for p in promo_products:
                    print(f"   • {p['name'][:60]}")
                    price = p.get('price', {})
                    if isinstance(price, dict):
                        amount = price.get('amount', 0) / 100
                        print(f"     💰 Prix: {amount:.2f}€ (RÉDUIT)")
                    print(f"     📂 {p.get('category', 'N/A')}")
                    print()
            else:
                print("\n   ⚠️  Aucun produit en promo DLC trouvé")
                print("   💡 Essayez de capturer en fin de journée (17h-19h)")
            
            # Extraire et sauvegarder les cookies
            cookies = context.cookies()
            sessionid = None
            csrftoken = None
            
            for cookie in cookies:
                if cookie['name'] == 'sessionid':
                    sessionid = cookie['value']
                elif cookie['name'] == 'csrftoken':
                    csrftoken = cookie['value']
            
            if sessionid and csrftoken:
                env_content = f"""# Configuration Foodles - Capturé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
FOODLES_SESSIONID={sessionid}
FOODLES_CSRFTOKEN={csrftoken}
FOODLES_CANTEEN_ID=2051
FOODLES_CLIENT_ID=480960
"""
                with open('.env', 'w') as f:
                    f.write(env_content)
                print(f"\n   🔐 Cookies mis à jour dans .env")
            
            browser.close()
    
    print("\n" + "="*80)
    print("✅ CAPTURE TERMINÉE")
    print("="*80)
    
    if promo_products:
        print(f"\n🎉 Succès! {len(promo_products)} produits en promo DLC capturés")
        print("\n💡 PROCHAINES ÉTAPES:")
        print("   1. Analyser les données: python3 << 'EOF'")
        print("      import json")
        print(f"      with open('{promo_file}', 'r') as f:")
        print("          promos = json.load(f)")
        print("      for p in promos:")
        print("          print(f\"{p['name']}: {p['price']}\")")
        print("      EOF")
    else:
        print("\n💡 CONSEIL:")
        print("   Les promos DLC apparaissent généralement:")
        print("   • En fin de journée (17h-19h)")
        print("   • Pour les produits qui périment le jour même")
        print("   • Réessayez à ce moment-là!")

if __name__ == "__main__":
    try:
        capture_promo_products()
    except KeyboardInterrupt:
        print("\n\n❌ Capture annulée par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur: {e}")
        import traceback
        traceback.print_exc()
