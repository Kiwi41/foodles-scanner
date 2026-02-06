#!/usr/bin/env python3
"""
Capture 100% automatique - version simplifiée
Navigation directe vers /canteen/select puis clic sur chaque cantine
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class SimpleAutoCapture:
    def __init__(self):
        self.sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
        self.csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'
        
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.captured = {}
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        self.current_data = None
    
    async def run(self):
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       🤖 CAPTURE 100% AUTOMATIQUE                                      ║")
        print("╚════════════════════════════════════════════════════════════════════════╝\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=800,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1400, 'height': 900},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Intercepter l'API
            async def handle_response(response):
                # Logger toutes les requêtes API pour debug
                if '/api/' in response.url:
                    print(f"   🌐 API: {response.url.split('?')[0]} [{response.status}]")
                
                # Essayer différents endpoints qui pourraient contenir les données
                if response.status == 200:
                    try:
                        # Endpoint fridge classique
                        if '/api/fridge/' in response.url:
                            data = await response.json()
                            if 'categories' in data:
                                self.current_data = data
                                print(f"   📡 Données depuis /api/fridge/")
                        
                        # Endpoint client qui peut contenir les données du frigo
                        elif '/api/client/' in response.url or '/api/async/client/' in response.url:
                            data = await response.json()
                            # Vérifier si les données du frigo sont là
                            if 'categories' in data:
                                self.current_data = data
                                print(f"   📡 Données depuis {response.url.split('/')[-2]}/")
                            elif isinstance(data, dict):
                                # Chercher dans les sous-objets
                                for key, value in data.items():
                                    if isinstance(value, dict) and 'categories' in value:
                                        self.current_data = value
                                        print(f"   📡 Données depuis {response.url.split('/')[-2]}/ (clé: {key})")
                                        break
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Étape 0: Charger la page d'accueil d'abord (comme le script manuel)
            print("🌐 Chargement de app.foodles.co (page d'accueil)...")
            await page.goto('https://app.foodles.co/', wait_until='domcontentloaded')
            await asyncio.sleep(4)
            
            print("   ✅ Page d'accueil chargée\n")
            
            # Capturer chaque cantine
            for cantine_name in self.cantines:
                print(f"{'='*70}")
                print(f"🔄 {cantine_name}")
                print(f"{'='*70}")
                
                self.current_data = None
                
                # Naviguer vers la page de sélection
                print(f"   🌐 Navigation vers /canteen/select...")
                await page.goto('https://app.foodles.co/canteen/select', wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # Chercher la cantine
                print(f"   🔍 Recherche de {cantine_name}...")
                
                clicked = False
                
                # Essayer plusieurs sélecteurs - priorité aux éléments cliquables
                selectors = [
                    f'a:has-text("{cantine_name}")',
                    f'button:has-text("{cantine_name}")',
                    f'a:has-text("Worldline {cantine_name}")',
                    f'[role="button"]:has-text("{cantine_name}")',
                ]
                
                for selector in selectors:
                    try:
                        elements = await page.locator(selector).all()
                        for elem in elements:
                            if await elem.is_visible():
                                text = await elem.text_content()
                                if text and cantine_name.lower() in text.lower():
                                    print(f"   🎯 Trouvé: {selector}")
                                    print(f"   📝 Texte: '{text.strip()[:50]}'")
                                    
                                    # Réinitialiser les données avant le clic
                                    self.current_data = None
                                    
                                    # Cliquer
                                    await elem.click()
                                    print(f"   👆 Clic effectué")
                                    clicked = True
                                    break
                        if clicked:
                            break
                    except:
                        continue
                
                if not clicked:
                    print(f"   ❌ Non trouvée avec sélecteurs cliquables")
                    print(f"   🔍 Recherche de tous les liens sur la page...")
                    
                    # Afficher tous les liens pour debug
                    all_links = await page.locator('a').all()
                    print(f"   📊 {len(all_links)} liens trouvés")
                    
                    for link in all_links[:10]:
                        try:
                            if await link.is_visible():
                                link_text = await link.text_content()
                                href = await link.get_attribute('href')
                                if link_text:
                                    print(f"      • '{link_text.strip()[:30]}' → {href}")
                        except:
                            pass
                    
                    await page.screenshot(path=f'debug_{cantine_name}.png')
                    continue
                
                # Attendre la redirection
                print(f"   ⏳ Attente redirection...")
                await asyncio.sleep(4)
                
                # Vérifier l'URL actuelle
                current_url = page.url
                print(f"   📍 URL: {current_url}")
                
                # Si on n'est pas sur fridge, y aller explicitement
                if 'fridge' not in current_url:
                    print(f"   🌐 Navigation vers /canteen/fridge...")
                    await page.goto('https://app.foodles.co/canteen/fridge', wait_until='domcontentloaded')
                    await asyncio.sleep(3)
                
                # Interagir avec la page pour déclencher le chargement
                print(f"   🖱️  Interaction avec la page...")
                try:
                    # Scroller un peu
                    await page.evaluate('window.scrollBy(0, 100)')
                    await asyncio.sleep(1)
                    # Cliquer sur un filtre ou bouton quelconque pour forcer le chargement
                    all_button = page.locator('button:has-text("All")')
                    if await all_button.count() > 0:
                        await all_button.first.click()
                        print(f"   👆 Clic sur 'All'")
                        await asyncio.sleep(2)
                except:
                    pass
                
                # Attendre l'appel API
                print(f"   ⏳ Attente API (max 10s)...")
                
                for i in range(20):
                    if self.current_data:
                        print(f"   ✅ API reçue après {i*0.5:.1f}s")
                        break
                    await asyncio.sleep(0.5)
                
                if self.current_data:
                    self.save_data(cantine_name, self.current_data)
                    print(f"✅ [{len(self.captured)}/3] {cantine_name} capturé!\n")
                else:
                    print(f"⚠️  Pas de données\n")
                
                await asyncio.sleep(1)
            
            print(f"\n{'='*70}")
            print(f"🎉 TERMINÉ: {len(self.captured)}/3 cantines")
            print(f"{'='*70}\n")
            
            await asyncio.sleep(2)
            await browser.close()
        
        return len(self.captured)
    
    def save_data(self, name, data):
        self.captured[name] = data
        
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{self.data_dir}/cantine_{name}_{date_str}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        categories = data.get('categories', [])
        total_produits = sum(len(cat.get('items', []) or cat.get('products', [])) for cat in categories)
        total_unites = sum(
            item.get('quantity', 0)
            for cat in categories
            for item in (cat.get('items', []) or cat.get('products', []))
        )
        total_dlc = sum(
            1 for cat in categories
            for item in (cat.get('items', []) or cat.get('products', []))
            if item.get('has_near_expiration_sale', False)
        )
        
        print(f"   📊 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC")
        print(f"   💾 {filename}")

async def main():
    capture = SimpleAutoCapture()
    count = await capture.run()
    
    if count == 3:
        print("✅ Succès total!")
        print("📊 Lance: python scripts/generate_report.py")
    elif count > 0:
        print(f"⚠️  {count}/3 cantines capturées")
    else:
        print("❌ Échec")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt")
