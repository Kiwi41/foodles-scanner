#!/usr/bin/env python3
"""
Scanner Ultra-Automatique avec Playwright
Trouve automatiquement le sélecteur de cantine et change automatiquement
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class UltraAutoScanner:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = ['Copernic', 'Amazone', 'Hangar']
        self.captured_data = {}
    
    async def scan_fully_auto(self):
        """Scan 100% automatique avec détection intelligente"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║          🚀 SCAN ULTRA-AUTOMATIQUE AVEC DÉTECTION IA                   ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print()
        print("🤖 Détection automatique du sélecteur de cantine...")
        print("🔄 Changement automatique entre cantines...")
        print("📊 Capture automatique des données...")
        print()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Visible pour debug
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Capturer les réponses API
            current_fridge = {'data': None, 'canteen': None}
            
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            canteen_info = data.get('canteen', {})
                            canteen_name = canteen_info.get('name', '')
                            current_fridge['data'] = data
                            current_fridge['canteen'] = canteen_name
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Charger l'app
            print("🌐 Chargement de app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='networkidle')
            await asyncio.sleep(3)
            
            # Capturer la première cantine (celle par défaut)
            if current_fridge['data']:
                first_cantine = self.extract_cantine_name(current_fridge['canteen'])
                if first_cantine:
                    print(f"\n✅ [1/3] {first_cantine} capturé (cantine par défaut)")
                    self.captured_data[first_cantine] = current_fridge['data']
                    self.save_quick(first_cantine, current_fridge['data'])
            
            # Chercher le sélecteur de cantine
            print("\n🔍 Recherche du sélecteur de cantine...")
            selector_info = await self.find_canteen_selector(page)
            
            if not selector_info:
                print("❌ Impossible de trouver le sélecteur automatiquement")
                print("📋 Passe en mode semi-automatique...")
                await browser.close()
                return await self.fallback_guided_mode()
            
            print(f"✅ Sélecteur trouvé: {selector_info['type']}")
            
            # Changer vers les autres cantines
            for cantine_name in self.cantines:
                if cantine_name in self.captured_data:
                    continue  # Déjà capturée
                
                print(f"\n🔄 Changement vers {cantine_name}...")
                current_fridge['data'] = None
                
                success = await self.switch_to_cantine(page, cantine_name, selector_info)
                
                if success:
                    # Attendre la nouvelle requête API
                    for _ in range(20):
                        if current_fridge['data']:
                            break
                        await asyncio.sleep(0.5)
                    
                    if current_fridge['data']:
                        print(f"✅ [{len(self.captured_data) + 1}/3] {cantine_name} capturé!")
                        self.captured_data[cantine_name] = current_fridge['data']
                        self.save_quick(cantine_name, current_fridge['data'])
                    else:
                        print(f"⚠️  Données non reçues pour {cantine_name}")
                else:
                    print(f"⚠️  Impossible de changer vers {cantine_name}")
            
            await asyncio.sleep(2)
            await browser.close()
        
        # Résumé
        print("\n" + "="*70)
        print(f"🎉 Scan terminé: {len(self.captured_data)}/3 cantines capturées")
        print("="*70)
        
        self.show_summary()
        return len(self.captured_data)
    
    async def find_canteen_selector(self, page):
        """Trouve intelligemment le sélecteur de cantine"""
        # Stratégies de recherche
        strategies = [
            # Stratégie 1: Chercher texte "Copernic", "Amazone", etc.
            {'type': 'text', 'patterns': ['Copernic', 'Amazone', 'Hangar', 'Worldline']},
            
            # Stratégie 2: Dropdown / Select
            {'type': 'dropdown', 'selectors': [
                'select[name*="cantine"]', 'select[name*="canteen"]',
                'select[id*="cantine"]', 'select[id*="canteen"]',
                '[role="combobox"]', '[aria-label*="cantine"]'
            ]},
            
            # Stratégie 3: Boutons / Menu
            {'type': 'menu', 'selectors': [
                'button:has-text("Copernic")', 'button:has-text("Amazone")',
                '[data-testid*="canteen"]', '[class*="canteen"]'
            ]}
        ]
        
        for strategy in strategies:
            if strategy['type'] == 'text':
                for pattern in strategy['patterns']:
                    try:
                        elements = await page.locator(f'text="{pattern}"').all()
                        if elements:
                            return {'type': 'text', 'pattern': pattern}
                    except:
                        continue
            
            elif strategy['type'] in ['dropdown', 'menu']:
                for selector in strategy['selectors']:
                    try:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            return {'type': strategy['type'], 'selector': selector}
                    except:
                        continue
        
        return None
    
    async def switch_to_cantine(self, page, cantine_name, selector_info):
        """Change vers une cantine spécifique"""
        try:
            if selector_info['type'] == 'text':
                # Cliquer sur le texte
                await page.click(f'text="{cantine_name}"', timeout=5000)
                await asyncio.sleep(2)
                return True
            
            elif selector_info['type'] == 'dropdown':
                # Sélectionner dans le dropdown
                await page.select_option(selector_info['selector'], label=cantine_name, timeout=5000)
                await asyncio.sleep(2)
                return True
            
            elif selector_info['type'] == 'menu':
                # Ouvrir le menu puis cliquer
                await page.click(selector_info['selector'], timeout=5000)
                await asyncio.sleep(1)
                await page.click(f'text="{cantine_name}"', timeout=5000)
                await asyncio.sleep(2)
                return True
        
        except Exception as e:
            print(f"   Erreur: {e}")
            return False
        
        return False
    
    def extract_cantine_name(self, canteen_full_name):
        """Extrait le nom court de la cantine"""
        for name in self.cantines:
            if name.lower() in canteen_full_name.lower():
                return name
        return None
    
    def save_quick(self, nom, data):
        """Sauvegarde rapide"""
        filename = f"{self.data_dir}/cantine_{nom}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Stats rapides
        categories = data.get('categories', [])
        total_produits = sum(len(cat.get('items', [])) for cat in categories)
        total_unites = sum(item.get('quantity', 0) for cat in categories for item in cat.get('items', []))
        total_dlc = sum(1 for cat in categories for item in cat.get('items', []) if item.get('has_near_expiration_sale', False))
        
        print(f"   📊 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC")
    
    def show_summary(self):
        """Affiche le résumé"""
        if not self.captured_data:
            return
        
        print("\n📊 RÉSUMÉ:")
        for nom, data in self.captured_data.items():
            categories = data.get('categories', [])
            total_produits = sum(len(cat.get('items', [])) for cat in categories)
            total_dlc = sum(1 for cat in categories for item in cat.get('items', []) if item.get('has_near_expiration_sale', False))
            print(f"   🏢 {nom}: {total_produits} produits, {total_dlc} DLC")
        
        print("\n✅ Lance: python compare_cantines.py pour le rapport détaillé\n")
    
    async def fallback_guided_mode(self):
        """Mode de secours semi-automatique"""
        print("\n🔄 Lancement du mode guidé...")
        # Importer et lancer le scanner guidé
        from smart_scan_cantines import SmartCantineScanner
        scanner = SmartCantineScanner()
        return await scanner.scan_with_guidance()

async def main():
    scanner = UltraAutoScanner()
    count = await scanner.scan_fully_auto()
    
    if count == 3:
        print("🎉 Toutes les cantines ont été scannées avec succès!")
    elif count > 0:
        print(f"⚠️  {count}/3 cantines capturées")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt du scan")
