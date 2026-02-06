#!/usr/bin/env python3
"""
Script automatique de capture des cantines avec Playwright
Ouvre le navigateur, permet de changer de cantine, et capture automatiquement les données
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class AutoCantineCapture:
    def __init__(self):
        self.cantines = [
            {'id': 2051, 'nom': 'Worldline Copernic'},
            {'id': 2052, 'nom': 'Worldline Amazone'},
            {'id': 2053, 'nom': 'Worldline Hangar'}
        ]
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.captured_data = {}
    
    async def capture_cantine(self, page, canteen_name):
        """Capture les données de la cantine actuellement sélectionnée"""
        print(f"\n{'='*70}")
        print(f"📦 CAPTURE EN COURS: {canteen_name}")
        print(f"{'='*70}\n")
        
        try:
            # Attendre que la page du frigo soit chargée
            print("⏳ Attente du chargement de la page frigo...")
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Récupérer les cookies
            cookies = await page.context.cookies()
            sessionid = None
            csrftoken = None
            
            for cookie in cookies:
                if cookie['name'] == 'sessionid':
                    sessionid = cookie['value']
                elif cookie['name'] == 'csrftoken':
                    csrftoken = cookie['value']
            
            print(f"🔑 Cookies récupérés:")
            print(f"   sessionid: {sessionid[:20]}..." if sessionid else "   sessionid: NON TROUVÉ")
            print(f"   csrftoken: {csrftoken[:20]}..." if csrftoken else "   csrftoken: NON TROUVÉ")
            
            # Intercepter les requêtes API
            api_data = None
            
            async def handle_response(response):
                nonlocal api_data
                if 'api.foodles.co/api/fridge' in response.url:
                    try:
                        data = await response.json()
                        api_data = data
                        print(f"✅ Données frigo interceptées: {response.url}")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Forcer un rechargement pour capturer les données
            print("\n🔄 Rechargement de la page pour capturer les données API...")
            await page.reload()
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Attendre un peu pour être sûr d'avoir capturé les données
            await asyncio.sleep(2)
            
            if api_data:
                print(f"✅ Données capturées avec succès!")
                
                # Analyser les données
                categories = api_data.get('categories', [])
                total_products = 0
                total_stock = 0
                dlc_products = []
                
                for cat in categories:
                    products = cat.get('products', [])
                    total_products += len(products)
                    for p in products:
                        qty = p.get('quantity', 0)
                        total_stock += qty
                        
                        # Vérifier les produits en DLC courte
                        if p.get('has_near_expiration_sale', False):
                            dlc_products.append({
                                'name': p.get('name'),
                                'category': cat.get('name'),
                                'quantity': qty
                            })
                
                print(f"\n📊 Résumé:")
                print(f"   • Produits: {total_products}")
                print(f"   • Stock total: {total_stock} unités")
                print(f"   • Produits en DLC courte: {len(dlc_products)}")
                
                if dlc_products:
                    print(f"\n🔥 PRODUITS EN DLC COURTE:")
                    for p in dlc_products:
                        print(f"   • {p['name']} ({p['category']}) - {p['quantity']}x")
                
                # Sauvegarder les données
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Trouver l'ID de cantine correspondant
                canteen_id = None
                for c in self.cantines:
                    if c['nom'] == canteen_name:
                        canteen_id = c['id']
                        break
                
                if canteen_id:
                    filename = f"{self.data_dir}/cantine_{canteen_id}_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(api_data, f, indent=2, ensure_ascii=False)
                    print(f"\n💾 Données sauvegardées: {filename}")
                    
                    self.captured_data[canteen_name] = {
                        'data': api_data,
                        'total_products': total_products,
                        'total_stock': total_stock,
                        'dlc_products': len(dlc_products),
                        'cookies': {'sessionid': sessionid, 'csrftoken': csrftoken}
                    }
                    
                    return True
            else:
                print("⚠️  Aucune donnée API capturée")
                return False
        
        except Exception as e:
            print(f"❌ Erreur lors de la capture: {str(e)}")
            return False
    
    async def run(self):
        """Lance le processus de capture automatique"""
        print("""
╔════════════════════════════════════════════════════════════════════════╗
║          🤖 CAPTURE AUTOMATIQUE DES CANTINES WORLDLINE                ║
╚════════════════════════════════════════════════════════════════════════╝

Ce script va:
  1. Ouvrir le navigateur sur app.foodles.co
  2. Attendre que tu te connectes (si nécessaire)
  3. Capturer automatiquement les données de la cantine actuelle
  4. Te demander de changer de cantine
  5. Répéter pour chaque cantine

⚠️  INSTRUCTIONS:
  • Connecte-toi à Foodles si nécessaire
  • Attends que le frigo soit affiché
  • Suis les instructions dans le terminal

Appuie sur ENTRÉE pour commencer...""")
        
        input()
        
        async with async_playwright() as p:
            print("\n🚀 Lancement du navigateur...")
            
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            print("🌐 Ouverture de app.foodles.co...")
            await page.goto('https://app.foodles.co/fridge')
            
            print("\n" + "="*70)
            print("👤 CONNEXION")
            print("="*70)
            print("\n1. Si tu n'es pas connecté, connecte-toi maintenant")
            print("2. Attends que la page du frigo soit complètement chargée")
            print("3. Appuie sur ENTRÉE quand c'est prêt")
            
            input("\n▶ Appuie sur ENTRÉE quand tu es connecté et le frigo est affiché...")
            
            # Première capture (cantine actuelle)
            print("\n🔍 Détection de la cantine actuelle...")
            
            # Essayer de détecter le nom de la cantine
            try:
                await page.wait_for_selector('text=/Worldline/', timeout=5000)
            except:
                pass
            
            print("\n📸 Capture de la cantine actuelle...")
            await self.capture_cantine(page, "Cantine 1")
            
            # Proposer de capturer les autres cantines
            for i in range(2):
                print(f"\n{'='*70}")
                print(f"🔄 CHANGEMENT DE CANTINE ({i+2}/3)")
                print("="*70)
                print(f"\n1. Change de cantine dans l'interface Foodles:")
                print(f"   • Clique sur ton profil (en haut à droite)")
                print(f"   • Sélectionne une autre cantine")
                print(f"   • Attends que le frigo se recharge")
                print(f"\n2. Appuie sur ENTRÉE quand c'est prêt")
                print(f"\n   OU tape 'q' pour terminer")
                
                choice = input("\n▶ Appuie sur ENTRÉE pour continuer (ou 'q' pour quitter): ").strip().lower()
                
                if choice == 'q':
                    print("\n👋 Arrêt de la capture")
                    break
                
                print(f"\n📸 Capture de la cantine {i+2}...")
                await self.capture_cantine(page, f"Cantine {i+2}")
            
            print("\n" + "="*70)
            print("✅ CAPTURE TERMINÉE")
            print("="*70)
            
            await browser.close()
            
            # Générer un rapport
            self.generate_report()
    
    def generate_report(self):
        """Génère un rapport récapitulatif"""
        print(f"\n{'='*70}")
        print("📊 RAPPORT DE CAPTURE")
        print(f"{'='*70}\n")
        
        if not self.captured_data:
            print("❌ Aucune donnée capturée")
            return
        
        for name, info in self.captured_data.items():
            print(f"🏢 {name}")
            print(f"   • Produits: {info['total_products']}")
            print(f"   • Stock: {info['total_stock']} unités")
            print(f"   • Produits DLC courte: {info['dlc_products']}")
            print()
        
        # Sauvegarder un rapport consolidé
        report_file = f"{self.data_dir}/rapport_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'date': datetime.now().isoformat(),
            'cantines': {}
        }
        
        for name, info in self.captured_data.items():
            report_data['cantines'][name] = {
                'total_products': info['total_products'],
                'total_stock': info['total_stock'],
                'dlc_products': info['dlc_products']
            }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Rapport sauvegardé: {report_file}")
        print(f"\n💡 Pour générer une comparaison complète, lance:")
        print(f"   python compare_cantines.py")


async def main():
    capture = AutoCantineCapture()
    await capture.run()


if __name__ == "__main__":
    asyncio.run(main())
