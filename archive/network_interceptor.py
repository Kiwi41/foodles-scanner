"""
Intercepteur de trafic réseau avec Playwright
Capture toutes les requêtes API réelles de Foodles
"""
from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import os


class NetworkInterceptor:
    """Intercepte et analyse le trafic réseau de Foodles"""
    
    def __init__(self):
        self.requests = []
        self.responses = []
        self.api_calls = []
        
    def on_request(self, request):
        """Callback appelé pour chaque requête"""
        req_data = {
            'timestamp': datetime.now().isoformat(),
            'url': request.url,
            'method': request.method,
            'headers': dict(request.headers),
            'post_data': request.post_data if request.method == 'POST' else None
        }
        
        # Filtrer les requêtes intéressantes (API, données)
        if any(keyword in request.url.lower() for keyword in ['api', 'product', 'menu', 'cart', 'order', 'canteen']):
            print(f"📡 {request.method} {request.url}")
            self.api_calls.append(req_data)
        
        self.requests.append(req_data)
    
    def on_response(self, response):
        """Callback appelé pour chaque réponse"""
        try:
            # Ne capturer que les réponses intéressantes
            if response.status == 200 and any(keyword in response.url.lower() for keyword in ['api', 'product', 'menu', 'cart', 'order', 'canteen']):
                resp_data = {
                    'timestamp': datetime.now().isoformat(),
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers),
                }
                
                # Essayer de récupérer le body
                try:
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type:
                        body = response.json()
                        resp_data['body'] = body
                        print(f"✅ {response.status} {response.url} - JSON capturé")
                    elif 'text' in content_type or 'html' in content_type:
                        body = response.text()
                        resp_data['body'] = body[:1000]  # Limiter la taille
                        print(f"✅ {response.status} {response.url} - Texte capturé")
                except Exception as e:
                    resp_data['body_error'] = str(e)
                    print(f"⚠️  {response.status} {response.url} - Erreur body: {e}")
                
                self.responses.append(resp_data)
        except Exception as e:
            print(f"❌ Erreur réponse: {e}")
    
    def capture_foodles_traffic(self, email: str = None, password: str = None):
        """
        Capture le trafic réseau de Foodles
        
        Args:
            email: Email de connexion (optionnel si déjà connecté)
            password: Mot de passe (optionnel)
        """
        print("🚀 Démarrage de l'interception réseau Foodles")
        print("=" * 80)
        
        with sync_playwright() as p:
            # Lancer le navigateur
            browser = p.chromium.launch(headless=False)  # headless=False pour voir ce qui se passe
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Créer une nouvelle page
            page = context.new_page()
            
            # Activer les listeners réseau
            page.on('request', self.on_request)
            page.on('response', self.on_response)
            
            try:
                # Aller sur Foodles
                print("\n📍 Navigation vers app.foodles.co...")
                page.goto('https://app.foodles.co/canteen/fridge', wait_until='networkidle')
                
                # Attendre un peu pour capturer les requêtes initiales
                print("⏳ Attente de chargement initial (5 secondes)...")
                page.wait_for_timeout(5000)
                
                # Si on a des credentials, se connecter
                if email and password:
                    print(f"\n🔐 Tentative de connexion avec {email}...")
                    # Chercher le bouton de connexion
                    try:
                        login_button = page.locator('text=Se connecter').first
                        if login_button.is_visible():
                            login_button.click()
                            page.wait_for_timeout(2000)
                            
                            # Remplir le formulaire
                            page.fill('input[type="email"]', email)
                            page.fill('input[type="password"]', password)
                            page.click('button[type="submit"]')
                            page.wait_for_timeout(5000)
                            print("✅ Connexion effectuée")
                    except Exception as e:
                        print(f"⚠️  Déjà connecté ou erreur login: {e}")
                
                # Explorer différentes pages
                pages_to_visit = [
                    ('Frigo', '/canteen/fridge'),
                    ('Cantine', '/canteen'),
                    ('Menu', '/canteen/menu'),
                    ('Compte', '/account'),
                ]
                
                for page_name, url in pages_to_visit:
                    try:
                        print(f"\n📄 Visite de: {page_name} ({url})")
                        page.goto(f'https://app.foodles.co{url}', wait_until='networkidle')
                        page.wait_for_timeout(3000)
                        
                        # Scroll pour déclencher le lazy loading
                        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                        page.wait_for_timeout(2000)
                        
                    except Exception as e:
                        print(f"⚠️  Erreur sur {page_name}: {e}")
                
                # Interagir avec la page du frigo
                print("\n🖱️  Tentative d'interaction avec le frigo...")
                try:
                    page.goto('https://app.foodles.co/canteen/fridge', wait_until='networkidle')
                    page.wait_for_timeout(2000)
                    
                    # Chercher des produits et cliquer dessus
                    products = page.locator('[data-testid*="product"], .product, article').all()
                    if products:
                        print(f"✅ {len(products)} produits détectés, clic sur le premier...")
                        products[0].click()
                        page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"⚠️  Erreur interaction: {e}")
                
                print("\n⏳ Attente finale (5 secondes) pour capturer les dernières requêtes...")
                page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"❌ Erreur lors de la navigation: {e}")
            
            finally:
                print("\n🔒 Fermeture du navigateur...")
                browser.close()
        
        print("\n✅ Capture terminée!")
        return self.get_summary()
    
    def get_summary(self):
        """Retourne un résumé de la capture"""
        return {
            'total_requests': len(self.requests),
            'total_responses': len(self.responses),
            'api_calls': len(self.api_calls),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, output_dir: str = 'network_capture'):
        """Sauvegarde tous les résultats capturés"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sauvegarder toutes les requêtes
        requests_file = f"{output_dir}/requests_{timestamp}.json"
        with open(requests_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, indent=2, ensure_ascii=False)
        print(f"📄 Requêtes sauvegardées: {requests_file}")
        
        # Sauvegarder toutes les réponses
        responses_file = f"{output_dir}/responses_{timestamp}.json"
        with open(responses_file, 'w', encoding='utf-8') as f:
            json.dump(self.responses, f, indent=2, ensure_ascii=False)
        print(f"📄 Réponses sauvegardées: {responses_file}")
        
        # Sauvegarder uniquement les appels API
        api_file = f"{output_dir}/api_calls_{timestamp}.json"
        with open(api_file, 'w', encoding='utf-8') as f:
            json.dump(self.api_calls, f, indent=2, ensure_ascii=False)
        print(f"📄 Appels API sauvegardés: {api_file}")
        
        # Créer un rapport
        report = {
            'summary': self.get_summary(),
            'unique_endpoints': list(set([r['url'] for r in self.api_calls])),
            'methods_used': list(set([r['method'] for r in self.api_calls])),
            'response_urls': list(set([r['url'] for r in self.responses]))
        }
        
        report_file = f"{output_dir}/report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 Rapport sauvegardé: {report_file}")
        
        return report


def main():
    """Fonction principale"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🕵️  INTERCEPTEUR DE TRAFIC RÉSEAU FOODLES                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print("Ce script va:")
    print("  1. Ouvrir un navigateur Chrome")
    print("  2. Naviguer sur app.foodles.co")
    print("  3. Capturer TOUTES les requêtes réseau")
    print("  4. Sauvegarder les appels API trouvés")
    print()
    print("⚠️  IMPORTANT:")
    print("  - Le navigateur s'ouvrira en mode visible")
    print("  - Connectez-vous manuellement si besoin")
    print("  - Le script capturera automatiquement le trafic")
    print()
    
    input("▶️  Appuyez sur Entrée pour démarrer...")
    
    # Créer l'intercepteur
    interceptor = NetworkInterceptor()
    
    # Note: Vous pouvez fournir email/password ici si vous voulez automatiser
    # interceptor.capture_foodles_traffic(email='votre@email.com', password='votrepass')
    
    # Capturer le trafic (sans auto-login)
    summary = interceptor.capture_foodles_traffic()
    
    # Afficher le résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA CAPTURE")
    print("=" * 80)
    print(f"Total requêtes: {summary['total_requests']}")
    print(f"Total réponses: {summary['total_responses']}")
    print(f"Appels API capturés: {summary['api_calls']}")
    
    # Sauvegarder
    print("\n💾 Sauvegarde des résultats...")
    report = interceptor.save_results()
    
    print("\n" + "=" * 80)
    print("✅ CAPTURE TERMINÉE!")
    print("=" * 80)
    print(f"\n📁 Fichiers générés dans: network_capture/")
    print(f"\n🎯 Endpoints API uniques trouvés: {len(report['unique_endpoints'])}")
    if report['unique_endpoints']:
        print("\nEndpoints capturés:")
        for endpoint in report['unique_endpoints'][:10]:
            print(f"  - {endpoint}")
        if len(report['unique_endpoints']) > 10:
            print(f"  ... et {len(report['unique_endpoints']) - 10} autres")


if __name__ == "__main__":
    main()
