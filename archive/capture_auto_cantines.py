#!/usr/bin/env python3
"""
Capture automatique intelligente - Change vraiment de cantine via l'interface
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class SmartCantineCapture:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.data_dir = os.path.join(project_root, 'cantines_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        self.captured = {}
    
    async def capture_all_auto(self):
        """Capture automatique en changeant de cantine via l'interface"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       🤖 CAPTURE AUTOMATIQUE INTELLIGENTE DES 3 CANTINES              ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print()
        print("🎯 Stratégie: Changer de cantine via l'interface comme un utilisateur")
        print()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Injecter les cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Intercepter les API calls
            current_data = {'data': None, 'canteen': None}
            
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            current_data['data'] = data
                            canteen_info = data.get('canteen', {})
                            current_data['canteen'] = canteen_info.get('name', '')
                    except:
                        pass
            
            page.on('response', handle_response)
            
            print("🌐 Connexion à app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='domcontentloaded')
            await asyncio.sleep(3)
            
            # Capturer la première cantine (par défaut)
            if current_data['data']:
                first_name = self.extract_name(current_data['canteen'])
                if first_name:
                    print(f"✅ [{len(self.captured)+1}/3] {first_name} capturé (défaut)")
                    self.save_data(first_name, current_data['data'])
            
            # Pour chaque cantine restante
            for cantine in self.cantines:
                if cantine in self.captured:
                    continue
                
                print(f"\n🔄 Changement vers {cantine}...")
                current_data['data'] = None
                
                success = await self.change_cantine_ui(page, cantine)
                
                if success:
                    # Attendre que les données soient chargées
                    for _ in range(20):
                        if current_data['data']:
                            break
                        await asyncio.sleep(0.5)
                    
                    if current_data['data']:
                        print(f"✅ [{len(self.captured)+1}/3] {cantine} capturé!")
                        self.save_data(cantine, current_data['data'])
                    else:
                        print(f"⚠️  Données non reçues pour {cantine}")
                else:
                    print(f"⚠️  Échec changement vers {cantine}")
            
            print(f"\n{'='*70}")
            print(f"🎉 Capture terminée: {len(self.captured)}/3 cantines")
            print(f"{'='*70}")
            
            await asyncio.sleep(2)
            await browser.close()
        
        return len(self.captured)
    
    async def change_cantine_ui(self, page, cantine_name):
        """Change de cantine via l'interface utilisateur"""
        try:
            # Stratégie 1: Chercher un bouton/dropdown avec le nom actuel de cantine
            selectors = [
                f'button:has-text("{cantine_name}")',
                f'[role="button"]:has-text("{cantine_name}")',
                f'text="{cantine_name}"',
                # Sélecteurs génériques de menu
                'button[aria-label*="cantine"]',
                'button[aria-label*="site"]',
                '[data-testid*="canteen"]',
                '[data-testid*="site"]',
                # Dropdown/Select
                'select',
                '[role="combobox"]'
            ]
            
            # Essayer de trouver et cliquer sur l'élément
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"   🔍 Trouvé sélecteur: {selector}")
                        element = elements[0]
                        await element.click(timeout=2000)
                        await asyncio.sleep(1)
                        
                        # Maintenant chercher l'option avec le nom de la cantine
                        try:
                            await page.click(f'text="{cantine_name}"', timeout=2000)
                            await asyncio.sleep(2)
                            print(f"   ✅ Cliqué sur {cantine_name}")
                            return True
                        except:
                            pass
                except:
                    continue
            
            # Stratégie 2: Chercher directement le texte de la cantine
            try:
                await page.click(f'text="{cantine_name}"', timeout=5000)
                await asyncio.sleep(2)
                print(f"   ✅ Changement direct vers {cantine_name}")
                return True
            except:
                pass
            
            print(f"   ❌ Impossible de trouver le sélecteur de cantine")
            print(f"   💡 Suggestion: Change manuellement vers {cantine_name}")
            print(f"   ⏳ Attente 10 secondes pour changement manuel...")
            await asyncio.sleep(10)
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def extract_name(self, full_name):
        """Extrait le nom court de la cantine"""
        for name in self.cantines:
            if name.lower() in full_name.lower():
                return name
        return None
    
    def save_data(self, name, data):
        """Sauvegarde les données d'une cantine"""
        self.captured[name] = data
        
        filename = f"{self.data_dir}/cantine_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Stats rapides
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
    capture = SmartCantineCapture()
    count = await capture.capture_all_auto()
    
    if count == 3:
        print("\n🎉 Toutes les cantines capturées avec succès!")
        print("📊 Lance: ./scripts/auto_report.sh")
    elif count > 0:
        print(f"\n⚠️  {count}/3 cantines capturées")
        print("💡 Relance le script ou capture manuellement les manquantes")
    else:
        print("\n❌ Aucune capture réussie")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt du scan")
