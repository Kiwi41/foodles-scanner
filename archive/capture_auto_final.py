#!/usr/bin/env python3
"""
Capture 100% automatique des 3 cantines avec Playwright
Simule les clics utilisateur sur le sélecteur de cantines
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class AutoCapture:
    def __init__(self):
        self.sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
        self.csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'
        
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.captured = {}
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        self.current_data = None
    
    async def capture_all_auto(self):
        """Capture automatique complète"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       🤖 CAPTURE 100% AUTOMATIQUE                                      ║")
        print("╚════════════════════════════════════════════════════════════════════════╝\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=1000  # Ralentir pour voir ce qui se passe
            )
            
            context = await browser.new_context(
                viewport={'width': 1400, 'height': 900}
            )
            
            # Cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Intercepter les réponses API
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            self.current_data = data
                            nb_cats = len(data.get('categories', []))
                            print(f"   📡 API reçue: {nb_cats} catégories")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Charger d'abord la page principale pour initialiser la session
            print("🌐 Connexion à app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='domcontentloaded')
            await asyncio.sleep(2)
            
            # Capturer chaque cantine
            for cantine_name in self.cantines:
                print(f"\n{'='*70}")
                print(f"🔄 CAPTURE: {cantine_name}")
                print(f"{'='*70}")
                
                self.current_data = None
                
                # Aller directement sur la page de sélection
                print(f"   🌐 Navigation vers la page de sélection...")
                await page.goto('https://app.foodles.co/canteen/select', wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # Prendre un screenshot de la page de sélection
                await page.screenshot(path=f'debug_selection_{cantine_name}.png')
                print(f"   📸 Screenshot: debug_selection_{cantine_name}.png")
                
                # Chercher l'option de la cantine sur cette page
                # Essayer différents sélecteurs qui pourraient contenir le nom
                option_selectors = [
                    f'text=/.*{cantine_name}.*/i',
                    f'button:has-text("{cantine_name}")',
                    f'a:has-text("{cantine_name}")',
                    f'div:has-text("{cantine_name}")',
                    f'span:has-text("{cantine_name}")',
                    f'li:has-text("{cantine_name}")',
                    f'[role="option"]:has-text("{cantine_name}")',
                    f'[role="button"]:has-text("{cantine_name}")',
                ]
                
                clicked = False
                for opt_sel in option_selectors:
                    if clicked:
                        break
                    try:
                        option = page.locator(opt_sel)
                        count = await option.count()
                        if count > 0:
                            print(f"   🔍 Trouvé {count} élément(s) avec: {opt_sel}")
                            # Chercher celui qui contient exactement le nom
                            for i in range(count):
                                elem = option.nth(i)
                                if await elem.is_visible():
                                    text = await elem.text_content()
                                    text_clean = text.strip() if text else ""
                                    
                                    # Vérifier que c'est bien la bonne cantine (pas trop de texte)
                                    if cantine_name.lower() in text_clean.lower() and len(text_clean) < 30:
                                        print(f"   🎯 Élément trouvé: '{text_clean[:40]}'")
                                        
                                        # Cliquer et attendre la navigation retour
                                        await elem.click()
                                        print(f"   ✅ Cliqué sur {cantine_name}")
                                        
                                        # Attendre explicitement le retour à la page principale
                                        print(f"   ⏳ Attente du retour à la page principale...")
                                        await page.wait_for_url('https://app.foodles.co/', timeout=10000)
                                        print(f"   ✅ Retour à la page principale")
                                        
                                        clicked = True
                                        break
                    except Exception as e:
                        continue
                
                if not clicked:
                    print(f"   ❌ Option {cantine_name} non trouvée")
                    print(f"   💡 Vérifiez debug_selection_{cantine_name}.png")
                    continue
                
                # Attendre le chargement complet de la page
                print(f"   ⏳ Attente du chargement complet...")
                await asyncio.sleep(5)
                
                # Attendre l'appel API
                print(f"   ⏳ Attente de l'appel API...")
                for i in range(30):
                    if self.current_data:
                        print(f"   ✅ Données reçues après {i*0.5:.1f}s")
                        break
                    await asyncio.sleep(0.5)
                
                if self.current_data:
                    self.save_data(cantine_name, self.current_data)
                    print(f"✅ [{len(self.captured)}/3] {cantine_name} capturé!\n")
                else:
                    print(f"⚠️  Aucune donnée reçue pour {cantine_name}\n")
                
                # Petite pause avant la prochaine
                await asyncio.sleep(2)
            
            print(f"\n{'='*70}")
            print(f"🎉 CAPTURE TERMINÉE: {len(self.captured)}/3 cantines")
            print(f"{'='*70}\n")
            
            await asyncio.sleep(3)
            await browser.close()
        
        return len(self.captured)
    
    def save_data(self, name, data):
        """Sauvegarde les données"""
        self.captured[name] = data
        
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{self.data_dir}/cantine_{name}_{date_str}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Stats
        categories = data.get('categories', [])
        total_produits = sum(len(cat.get('items', []) or cat.get('products', [])) for cat in categories)
        total_unites = 0
        total_dlc = 0
        
        for cat in categories:
            items = cat.get('items', []) or cat.get('products', [])
            for item in items:
                total_unites += item.get('quantity', 0)
                if item.get('has_near_expiration_sale', False):
                    total_dlc += 1
        
        print(f"   📊 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC")
        print(f"   💾 {filename}")

async def main():
    capture = AutoCapture()
    count = await capture.capture_all_auto()
    
    if count == 3:
        print("\n✅ Toutes les cantines capturées!")
        print("📊 Lance: python scripts/generate_report.py")
    elif count > 0:
        print(f"\n⚠️  {count}/3 cantines capturées")
    else:
        print("\n❌ Échec de la capture automatique")
        print("💡 Utilisez: python scripts/capture_manual_clicks.py")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt")
