#!/usr/bin/env python3
"""
Capture 100% automatique - Version hybride
Utilise Playwright pour les clics + HTTP direct pour les données
"""

import asyncio
import json
import os
import requests
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class HybridAutoCapture:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.captured = {}
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        
        # Client HTTP pour récupérer les données
        self.session = requests.Session()
        self.session.headers.update({
            'Cookie': f'sessionid={self.sessionid}; csrftoken={self.csrftoken}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        })
    
    async def run(self):
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       🤖 CAPTURE 100% AUTOMATIQUE (méthode hybride)                   ║")
        print("╚════════════════════════════════════════════════════════════════════════╝\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            context = await browser.new_context()
            
            # Cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Capturer chaque cantine
            for cantine_name in self.cantines:
                print(f"{'='*70}")
                print(f"🔄 {cantine_name}")
                print(f"{'='*70}")
                
                # Aller sur la page de sélection
                print(f"   🌐 Navigation vers /canteen/select...")
                await page.goto('https://app.foodles.co/canteen/select', wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # Chercher et cliquer
                print(f"   🔍 Recherche de {cantine_name}...")
                
                clicked = False
                selectors = [
                    f'a:has-text("{cantine_name}")',
                    f'button:has-text("{cantine_name}")',
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
                                    await elem.click()
                                    print(f"   👆 Clic effectué")
                                    clicked = True
                                    break
                        if clicked:
                            break
                    except:
                        continue
                
                if not clicked:
                    print(f"   ❌ Non trouvée")
                    continue
                
                # Attendre la redirection
                print(f"   ⏳ Attente de la redirection...")
                await asyncio.sleep(4)
                
                # Maintenant récupérer les données via HTTP
                print(f"   📡 Récupération des données via HTTP...")
                try:
                    response = self.session.get('https://api.foodles.co/api/fridge/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'categories' in data:
                            self.save_data(cantine_name, data)
                            print(f"✅ [{len(self.captured)}/3] {cantine_name} capturé!\n")
                        else:
                            print(f"⚠️  Données invalides\n")
                    else:
                        print(f"⚠️  Erreur HTTP {response.status_code}\n")
                except Exception as e:
                    print(f"⚠️  Erreur: {e}\n")
                
                await asyncio.sleep(1)
            
            print(f"{'='*70}")
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
    capture = HybridAutoCapture()
    count = await capture.run()
    
    if count == 3:
        print("✅ SUCCÈS TOTAL!")
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
