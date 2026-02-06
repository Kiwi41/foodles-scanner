#!/usr/bin/env python3
"""
Scanner intelligent - Détecte automatiquement comment changer de cantine
Version interactive qui apprend de l'interface Foodles
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class SmartCantineScanner:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = [
            {'id': 2051, 'nom': 'Copernic'},
            {'id': 2052, 'nom': 'Amazone'},
            {'id': 2053, 'nom': 'Hangar'}
        ]
        
        self.captured_data = {}
    
    async def scan_with_guidance(self):
        """Scan guidé - l'utilisateur change, le script capture"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║          🤖 SCAN GUIDÉ DES CANTINES (Semi-automatique)                ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print()
        print("📋 Mode: Tu changes de cantine, je capture automatiquement les données")
        print()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Injecter les cookies
            await context.add_cookies([
                {
                    'name': 'sessionid',
                    'value': self.sessionid,
                    'domain': '.foodles.co',
                    'path': '/'
                },
                {
                    'name': 'csrftoken',
                    'value': self.csrftoken,
                    'domain': '.foodles.co',
                    'path': '/'
                }
            ])
            
            page = await context.new_page()
            
            # Intercepter les réponses API
            captured_cantines = set()
            
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data and 'canteen' in data:
                            canteen_info = data.get('canteen', {})
                            canteen_name = canteen_info.get('name', 'Unknown')
                            
                            # Extraire le nom court (Copernic, Amazone, Hangar)
                            for c in self.cantines:
                                if c['nom'] in canteen_name or str(c['id']) in str(canteen_info.get('id', '')):
                                    nom = c['nom']
                                    if nom not in captured_cantines:
                                        captured_cantines.add(nom)
                                        self.captured_data[nom] = data
                                        self.save_cantine_data(nom, data)
                                        print(f"\n✅ [{len(captured_cantines)}/3] {nom} capturé!")
                                        
                                        if len(captured_cantines) == 3:
                                            print("\n🎉 Toutes les cantines ont été capturées!")
                                        else:
                                            remaining = [c['nom'] for c in self.cantines if c['nom'] not in captured_cantines]
                                            print(f"📋 Restant: {', '.join(remaining)}")
                                            print(f"👉 Change vers la cantine suivante dans le navigateur")
                                    break
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Aller sur l'app
            print("🌐 Ouverture de app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='networkidle')
            await asyncio.sleep(3)
            
            print("\n" + "="*70)
            print("📋 INSTRUCTIONS:")
            print("="*70)
            print("1. Le navigateur est ouvert avec ta session")
            print("2. Change de cantine via l'interface Foodles (profil/menu)")
            print("3. Je détecte automatiquement et capture les données")
            print("4. Répète pour chaque cantine (Copernic, Amazone, Hangar)")
            print("5. Ferme le navigateur quand c'est terminé")
            print("="*70 + "\n")
            
            # Attendre que l'utilisateur termine
            print("⏳ En attente... (Change de cantine dans le navigateur)")
            print("   Appuie sur Ctrl+C pour terminer\n")
            
            try:
                while len(captured_cantines) < 3:
                    await asyncio.sleep(1)
                
                # Toutes capturées, attendre un peu avant de fermer
                print("\n✅ Scan complet! Fermeture dans 5 secondes...")
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Arrêt demandé")
            
            await browser.close()
        
        # Générer le rapport
        if len(self.captured_data) >= 2:
            self.generate_summary()
        
        return len(self.captured_data)
    
    def save_cantine_data(self, nom, data):
        """Sauvegarde les données d'une cantine"""
        filename = f"{self.data_dir}/cantine_{nom}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Analyser rapidement
        categories = data.get('categories', [])
        total_produits = sum(len(cat.get('items', [])) for cat in categories)
        total_unites = sum(item.get('quantity', 0) for cat in categories for item in cat.get('items', []))
        total_dlc = sum(1 for cat in categories for item in cat.get('items', []) if item.get('has_near_expiration_sale', False))
        
        print(f"   📊 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC")
        print(f"   💾 {filename}")
    
    def generate_summary(self):
        """Génère un résumé comparatif"""
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES CANTINES CAPTURÉES")
        print("="*70 + "\n")
        
        for nom, data in self.captured_data.items():
            categories = data.get('categories', [])
            total_produits = sum(len(cat.get('items', [])) for cat in categories)
            total_unites = sum(item.get('quantity', 0) for cat in categories for item in cat.get('items', []))
            total_dlc = sum(1 for cat in categories for item in cat.get('items', []) if item.get('has_near_expiration_sale', False))
            
            print(f"🏢 {nom}")
            print(f"   📦 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC courte")
        
        print("\n" + "="*70)
        print("✅ Rapport détaillé: python compare_cantines.py")
        print("="*70 + "\n")

async def main():
    scanner = SmartCantineScanner()
    count = await scanner.scan_with_guidance()
    
    if count == 0:
        print("\n⚠️  Aucune donnée capturée")
    elif count < 3:
        print(f"\n⚠️  Seulement {count}/3 cantines capturées")
        print("   Relance le script pour capturer les cantines manquantes")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du scan")
