#!/usr/bin/env python3
"""
Version simplifiée: ouvre le navigateur et laisse l'utilisateur cliquer manuellement
Capture automatiquement les données quand l'API est appelée
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class ManualClickCapture:
    def __init__(self):
        # Utiliser des cookies récents
        self.sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
        self.csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'
        
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.captured = {}
        self.target_cantines = ['Copernic', 'Amazone', 'Hangar']
    
    async def capture_with_manual_clicks(self):
        """Ouvre le navigateur et laisse l'utilisateur cliquer"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║       📸 CAPTURE ASSISTÉE - CLICS MANUELS                              ║")
        print("╚════════════════════════════════════════════════════════════════════════╝\n")
        print("📋 Instructions:")
        print("   1. Un navigateur va s'ouvrir sur app.foodles.co")
        print("   2. Cliquez sur chaque cantine dans l'ordre:")
        print("      • Copernic")
        print("      • Amazone  ")
        print("      • Hangar")
        print("   3. Attendez 2-3 secondes après chaque clic")
        print("   4. Les données seront capturées automatiquement\n")
        
        input("Appuyez sur ENTRÉE pour démarrer...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=100)
            
            context = await browser.new_context(
                viewport={'width': 1400, 'height': 900}
            )
            
            # Injecter les cookies
            await context.add_cookies([
                {'name': 'sessionid', 'value': self.sessionid, 'domain': '.foodles.co', 'path': '/'},
                {'name': 'csrftoken', 'value': self.csrftoken, 'domain': '.foodles.co', 'path': '/'}
            ])
            
            page = await context.new_page()
            
            # Intercepter les API calls
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            # Essayer d'extraire le nom de la cantine
                            canteen_info = data.get('canteen', {})
                            if isinstance(canteen_info, dict):
                                canteen_name = canteen_info.get('name', '')
                            else:
                                canteen_name = str(canteen_info)
                            
                            # Extraire le nom court
                            detected = None
                            for target in self.target_cantines:
                                if target.lower() in canteen_name.lower():
                                    detected = target
                                    break
                            
                            if not detected:
                                # Si on ne trouve pas, utiliser le hash pour déterminer
                                categories_count = len(data.get('categories', []))
                                print(f"\\n📡 API reçue: {categories_count} catégories")
                                
                                # Demander à l'utilisateur
                                print(f"❓ Quelle cantine venez-vous de sélectionner?")
                                for i, name in enumerate(self.target_cantines):
                                    if name not in self.captured:
                                        print(f"   {i+1}. {name}")
                                
                                # Prendre la première non capturée
                                for name in self.target_cantines:
                                    if name not in self.captured:
                                        detected = name
                                        break
                            
                            if detected and detected not in self.captured:
                                self.save_data(detected, data)
                                print(f"✅ [{len(self.captured)}/3] {detected} capturé!")
                                
                                if len(self.captured) == 3:
                                    print(f"\\n🎉 Toutes les cantines capturées!")
                                elif len(self.captured) < 3:
                                    remaining = [c for c in self.target_cantines if c not in self.captured]
                                    print(f"\\n➡️  Cliquez maintenant sur: {remaining[0]}")
                    except Exception as e:
                        print(f"Erreur: {e}")
            
            page.on('response', handle_response)
            
            print("\\n🌐 Chargement de app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='domcontentloaded')
            print("✅ Page chargée!")
            print(f"\\n➡️  Cliquez sur la première cantine: {self.target_cantines[0]}\\n")
            
            # Attendre que toutes les cantines soient capturées
            timeout = 180  # 3 minutes max
            for _ in range(timeout):
                if len(self.captured) == 3:
                    break
                await asyncio.sleep(1)
            
            if len(self.captured) == 3:
                print(f"\\n{'='*70}")
                print(f"🎉 CAPTURE TERMINÉE: {len(self.captured)}/3 cantines")
                print(f"{'='*70}\\n")
                await asyncio.sleep(2)
            else:
                print(f"\\n⏱️  Timeout atteint - {len(self.captured)}/3 cantines capturées")
                print(f"⏸️  Le navigateur reste ouvert 10 secondes...")
                await asyncio.sleep(10)
            
            await browser.close()
        
        return len(self.captured)
    
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
    capture = ManualClickCapture()
    count = await capture.capture_with_manual_clicks()
    
    if count == 3:
        print("\\n✅ Toutes les cantines capturées!")
        print("📊 Lance maintenant: python scripts/generate_report.py")
    elif count > 0:
        print(f"\\n⚠️  {count}/3 cantines capturées")
    else:
        print("\\n❌ Aucune capture réussie")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n\\n⏹️  Arrêt")
