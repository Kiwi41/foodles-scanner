#!/usr/bin/env python3
"""
Capture interactive des 3 cantines avec Playwright
Version améliorée qui teste tous les sélecteurs possibles
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class InteractiveCantineCapture:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.data_dir = os.path.join(project_root, 'cantines_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        self.captured = {}
    
    async def capture_all(self):
        """Capture avec interaction utilisateur guidée"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       🤖 CAPTURE INTERACTIVE DES 3 CANTINES                            ║")
        print("╚════════════════════════════════════════════════════════════════════════╝\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            
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
                            canteen_name = canteen_info.get('name', '') if isinstance(canteen_info, dict) else str(canteen_info)
                            current_data['canteen'] = canteen_name
                            print(f"   📡 API reçue: {len(data.get('categories', []))} catégories")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            print("🌐 Connexion à app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='domcontentloaded', timeout=30000)
            print("   ⏳ Attente du chargement complet...")
            await asyncio.sleep(5)
            
            # Capturer la cantine par défaut
            if current_data['data']:
                first_name = self.extract_name(current_data['canteen'])
                if first_name:
                    print(f"✅ [{len(self.captured)+1}/3] {first_name} capturé (cantine par défaut)\n")
                    self.save_data(first_name, current_data['data'])
            
            # Pour les cantines restantes
            for cantine in self.cantines:
                if cantine in self.captured:
                    continue
                
                print(f"\n{'='*70}")
                print(f"🔄 CHANGEMENT VERS: {cantine}")
                print(f"{'='*70}")
                
                current_data['data'] = None
                
                # Essayer différentes stratégies
                success = await self.find_and_click_canteen(page, cantine)
                
                if success:
                    # Attendre les données
                    print(f"   ⏳ Attente des données (15s max)...")
                    for i in range(30):
                        if current_data['data']:
                            print(f"      ✓ Données reçues après {i*0.5:.1f}s")
                            break
                        await asyncio.sleep(0.5)
                    
                    if current_data['data']:
                        # Utiliser le nom de la cantine ciblée directement
                        print(f"✅ [{len(self.captured)+1}/3] {cantine} capturé!\n")
                        self.save_data(cantine, current_data['data'])
                    else:
                        print(f"⚠️  Pas de données reçues pour {cantine}")
            
            print(f"\n{'='*70}")
            print(f"🎉 CAPTURE TERMINÉE: {len(self.captured)}/3 cantines")
            print(f"{'='*70}\n")
            
            if len(self.captured) < 3:
                print("⏸️  Le navigateur reste ouvert 30 secondes pour inspection...")
                await asyncio.sleep(30)
            else:
                await asyncio.sleep(3)
            
            await browser.close()
        
        return len(self.captured)
    
    async def find_and_click_canteen(self, page, cantine_name):
        """Trouve et clique sur le sélecteur de cantine avec plusieurs stratégies"""
        
        # Stratégie 1: Chercher tous les textes contenant le nom des cantines
        print(f"   🔍 Recherche d'éléments contenant 'Worldline', 'Copernic', 'Amazone' ou 'Hangar'...")
        
        selectors_to_try = [
            # Textes spécifiques
            f'text="{cantine_name}"',
            f'text="Worldline {cantine_name}"',
            f'text=/.*{cantine_name}.*/i',
            
            # Boutons
            f'button:has-text("{cantine_name}")',
            'button:has-text("Worldline")',
            'button[aria-label*="site"]',
            'button[aria-label*="cantine"]',
            'button[aria-label*="location"]',
            
            # Liens et autres éléments cliquables
            f'a:has-text("{cantine_name}")',
            f'div[role="button"]:has-text("{cantine_name}")',
            f'[role="button"]',
            
            # Headers et menus
            'header button',
            'nav button',
            '[class*="header"] button',
            '[class*="nav"] button',
            '[class*="menu"] button',
            '[class*="select"] button',
            
            # Dropdowns
            'select',
            '[role="combobox"]',
            '[aria-haspopup="listbox"]',
            '[aria-haspopup="menu"]',
        ]
        
        for i, selector in enumerate(selectors_to_try):
            try:
                elements = await page.locator(selector).all()
                if elements:
                    print(f"   ✓ [{i+1}] Trouvé {len(elements)} élément(s) avec: {selector}")
                    
                    # Essayer de cliquer sur le premier
                    try:
                        element = elements[0]
                        
                        # Vérifier si l'élément est visible
                        is_visible = await element.is_visible()
                        if not is_visible:
                            print(f"      ⚠️  Élément invisible, test suivant...")
                            continue
                        
                        # Obtenir le texte de l'élément
                        text = await element.text_content()
                        print(f"      📝 Texte: '{text[:50]}...'")
                        
                        # Cliquer
                        await element.click(timeout=3000)
                        print(f"      👆 Cliqué sur l'élément")
                        await asyncio.sleep(2)
                        
                        # Maintenant chercher l'option de la cantine dans le menu ouvert
                        try:
                            # Essayer différents sélecteurs pour trouver l'option
                            option_selectors = [
                                f'text="{cantine_name}"',
                                f'text="Worldline {cantine_name}"',
                                f'li:has-text("{cantine_name}")',
                                f'[role="option"]:has-text("{cantine_name}")',
                                f'[role="menuitem"]:has-text("{cantine_name}")',
                            ]
                            
                            for opt_sel in option_selectors:
                                try:
                                    option = page.locator(opt_sel)
                                    if await option.count() > 0:
                                        print(f"      🎯 Option trouvée: {opt_sel}")
                                        await option.first.click(timeout=2000)
                                        print(f"      ✅ Cliqué sur {cantine_name}")
                                        await asyncio.sleep(3)
                                        return True
                                except:
                                    continue
                        except:
                            pass
                        
                    except Exception as e:
                        print(f"      ❌ Erreur clic: {str(e)[:50]}")
                        continue
            except:
                continue
        
        # Stratégie 2: Afficher tous les boutons visibles pour debug
        print(f"\n   🔍 DEBUG: Liste de tous les boutons visibles...")
        try:
            all_buttons = await page.locator('button').all()
            print(f"   📊 {len(all_buttons)} boutons trouvés")
            for i, btn in enumerate(all_buttons[:10]):  # Limiter à 10
                try:
                    if await btn.is_visible():
                        text = await btn.text_content()
                        if text and text.strip():
                            print(f"      • Bouton {i+1}: '{text.strip()[:40]}'")
                except:
                    pass
        except:
            pass
        
        print(f"\n   ❌ Impossible de trouver le sélecteur automatiquement")
        print(f"   💡 Veuillez cliquer MANUELLEMENT sur {cantine_name} dans le navigateur")
        print(f"   ⏳ Attente 15 secondes...")
        await asyncio.sleep(15)
        return True
    
    def extract_name(self, full_name):
        """Extrait le nom court de la cantine"""
        for name in self.cantines:
            if name.lower() in full_name.lower():
                return name
        return None
    
    def save_data(self, name, data):
        """Sauvegarde les données d'une cantine"""
        self.captured[name] = data
        
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{self.data_dir}/cantine_{name}_{date_str}.json"
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
    capture = InteractiveCantineCapture()
    count = await capture.capture_all()
    
    if count == 3:
        print("\n✅ Toutes les cantines capturées!")
        print("📊 Lance maintenant: python scripts/generate_report.py")
    elif count > 0:
        print(f"\n⚠️  {count}/3 cantines capturées")
    else:
        print("\n❌ Aucune capture réussie")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt")
