#!/usr/bin/env python3
"""
Script d'automatisation complète du scan des 3 cantines Worldline
Utilise Playwright pour changer automatiquement de cantine et capturer les données
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class AutoCantineScanner:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = [
            {'id': 2051, 'nom': 'Copernic', 'nom_complet': 'Worldline Copernic'},
            {'id': 2052, 'nom': 'Amazone', 'nom_complet': 'Worldline Amazone'},
            {'id': 2053, 'nom': 'Hangar', 'nom_complet': 'Worldline Hangar'}
        ]
        
        self.all_data = {}
    
    async def scan_all_cantines(self):
        """Lance le scan automatique de toutes les cantines"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║          🤖 SCAN AUTOMATIQUE DES CANTINES WORLDLINE                    ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print()
        
        async with async_playwright() as p:
            # Lancer le navigateur en mode non-headless pour voir ce qui se passe
            browser = await p.chromium.launch(
                headless=False,
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
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
            
            # Intercepter les requêtes API
            fridge_data = {}
            
            async def handle_response(response):
                if '/api/fridge/' in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            fridge_data['current'] = data
                            print(f"   ✅ Données capturées!")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # Aller sur l'app
            print("🌐 Connexion à app.foodles.co...")
            await page.goto('https://app.foodles.co/', wait_until='networkidle')
            await asyncio.sleep(2)
            
            # Scanner chaque cantine
            for i, cantine in enumerate(self.cantines, 1):
                print(f"\n{'='*70}")
                print(f"🏢 [{i}/3] Scan de {cantine['nom_complet']}")
                print(f"{'='*70}")
                
                if i > 1:  # Pas besoin de changer pour la première
                    await self.change_cantine(page, cantine['nom'])
                    await asyncio.sleep(3)  # Attendre le rechargement
                
                # Forcer le rechargement du frigo
                fridge_data['current'] = None
                print(f"📦 Chargement des données du frigo...")
                
                # Aller sur la page frigo pour déclencher l'API
                await page.goto('https://app.foodles.co/', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Attendre que les données soient capturées
                for attempt in range(10):
                    if fridge_data.get('current'):
                        break
                    await asyncio.sleep(0.5)
                
                if fridge_data.get('current'):
                    data = fridge_data['current']
                    self.all_data[cantine['nom']] = data
                    
                    # Analyser et sauvegarder
                    self.analyze_and_save(cantine, data)
                else:
                    print(f"   ❌ Échec de la capture pour {cantine['nom']}")
            
            print(f"\n{'='*70}")
            print("🎉 Scan terminé!")
            print(f"{'='*70}")
            
            await browser.close()
        
        # Générer le rapport comparatif
        self.generate_comparison_report()
    
    async def change_cantine(self, page, nom_cantine):
        """Change de cantine via l'interface"""
        print(f"🔄 Changement vers {nom_cantine}...")
        
        try:
            # Méthode 1: Cliquer sur le sélecteur de cantine (à adapter selon l'interface)
            # Cette partie nécessite d'inspecter l'interface Foodles pour trouver les bons sélecteurs
            
            # Essayer de trouver le menu de sélection de cantine
            # Option 1: Bouton/menu profil
            try:
                await page.click('button[aria-label*="profil"], button[aria-label*="menu"], [data-testid="profile-button"]', timeout=5000)
                await asyncio.sleep(1)
            except:
                pass
            
            # Option 2: Chercher directement le nom de la cantine
            try:
                # Chercher un élément contenant le nom de la cantine
                cantine_selector = f'text="{nom_cantine}"'
                await page.click(cantine_selector, timeout=5000)
                await asyncio.sleep(1)
                print(f"   ✅ Cantine changée vers {nom_cantine}")
                return True
            except:
                pass
            
            # Option 3: Si l'URL contient l'ID de la cantine
            try:
                await page.goto(f'https://app.foodles.co/?canteen={nom_cantine}', wait_until='networkidle')
                print(f"   ✅ Cantine changée via URL")
                return True
            except:
                pass
            
            print(f"   ⚠️  Impossible de changer automatiquement - changement manuel requis")
            print(f"   👉 Change manuellement vers {nom_cantine} dans le navigateur")
            
            # Attendre que l'utilisateur change manuellement
            await asyncio.sleep(10)
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur lors du changement: {e}")
            return False
    
    def analyze_and_save(self, cantine, data):
        """Analyse et sauvegarde les données d'une cantine"""
        categories = data.get('categories', [])
        
        total_produits = 0
        total_unites = 0
        produits_dlc = []
        
        for cat in categories:
            items = cat.get('items', [])
            for item in items:
                total_produits += 1
                total_unites += item.get('quantity', 0)
                
                if item.get('has_near_expiration_sale', False):
                    produits_dlc.append({
                        'nom': item.get('name', 'N/A'),
                        'category': cat.get('name', 'N/A'),
                        'quantity': item.get('quantity', 0)
                    })
        
        print(f"   📊 {total_produits} produits | {total_unites} unités")
        if produits_dlc:
            print(f"   🔥 {len(produits_dlc)} produits en DLC courte:")
            for p in produits_dlc:
                print(f"      • {p['nom']} ({p['category']}) - {p['quantity']}x")
        else:
            print(f"   ✅ Aucun produit en DLC courte")
        
        # Sauvegarder
        filename = f"{self.data_dir}/cantine_{cantine['nom']}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Sauvegardé: {filename}")
    
    def generate_comparison_report(self):
        """Génère un rapport comparatif de toutes les cantines"""
        if len(self.all_data) < 2:
            return
        
        print(f"\n{'='*70}")
        print("📊 RAPPORT COMPARATIF")
        print(f"{'='*70}\n")
        
        for nom, data in self.all_data.items():
            categories = data.get('categories', [])
            
            total_produits = 0
            total_unites = 0
            total_dlc = 0
            
            for cat in categories:
                items = cat.get('items', [])
                for item in items:
                    total_produits += 1
                    total_unites += item.get('quantity', 0)
                    if item.get('has_near_expiration_sale', False):
                        total_dlc += 1
            
            print(f"🏢 {nom}")
            print(f"   📦 {total_produits} produits | {total_unites} unités | 🔥 {total_dlc} DLC")
        
        print(f"\n{'='*70}")
        print("✅ Pour un rapport détaillé, lance: python compare_cantines.py")
        print(f"{'='*70}\n")

async def main():
    scanner = AutoCantineScanner()
    await scanner.scan_all_cantines()

if __name__ == '__main__':
    asyncio.run(main())
