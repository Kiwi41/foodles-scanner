#!/usr/bin/env python3
"""
Scanner 100% automatique - Scanne les 3 cantines via API directe
Pas besoin de navigateur, tout en ligne de commande
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class FullAutoScanner:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        self.data_dir = 'cantines_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.cantines = [
            {'id': 2051, 'nom': 'Copernic', 'nom_complet': 'Worldline Copernic', 'adresse': '3 rue Copernic, 41000 Blois'},
            {'id': 2052, 'nom': 'Amazone', 'nom_complet': 'Worldline Amazone', 'adresse': '5 rue Copernic, 41000 Blois'},
            {'id': 2053, 'nom': 'Hangar', 'nom_complet': 'Worldline Hangar', 'adresse': '11 rue Copernic, 41000 Blois'}
        ]
        
        self.headers = {
            'Cookie': f'sessionid={self.sessionid}; csrftoken={self.csrftoken}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Referer': 'https://app.foodles.co/',
            'Accept': 'application/json'
        }
        
        self.results = {}
    
    def scan_all(self):
        """Scanne automatiquement toutes les cantines"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║          🚀 SCAN 100% AUTOMATIQUE - TOUTES LES CANTINES               ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print()
        print("🤖 Mode: Scan automatique via API directe (sans navigateur)")
        print()
        
        success_count = 0
        
        for i, cantine in enumerate(self.cantines, 1):
            print(f"{'='*70}")
            print(f"🏢 [{i}/3] Scan de {cantine['nom_complet']}")
            print(f"{'='*70}")
            
            data = self.scan_cantine(cantine)
            
            if data:
                self.results[cantine['nom']] = {
                    'data': data,
                    'info': cantine
                }
                self.analyze_and_save(cantine, data)
                success_count += 1
                print()
            else:
                print(f"❌ Échec pour {cantine['nom']}\n")
        
        print(f"{'='*70}")
        print(f"✅ Scan terminé: {success_count}/3 cantines capturées")
        print(f"{'='*70}\n")
        
        if success_count >= 2:
            self.generate_comparison()
        
        return success_count
    
    def scan_cantine(self, cantine):
        """Scanne une cantine spécifique via l'API"""
        # Méthode 1: Endpoint spécifique à la cantine
        url = f'https://api.foodles.co/api/fridge/canteen/{cantine["id"]}/'
        
        try:
            print(f"📡 Appel API: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'categories' in data:
                    print(f"✅ Données récupérées (code 200)")
                    return data
                else:
                    print(f"⚠️  Réponse reçue mais format inattendu")
                    return None
            
            elif response.status_code == 403:
                print(f"🔒 Accès refusé (403) - Tentative méthode alternative...")
                return self.scan_cantine_alternative(cantine)
            
            elif response.status_code == 404:
                print(f"❌ Endpoint non trouvé (404) - Tentative méthode alternative...")
                return self.scan_cantine_alternative(cantine)
            
            else:
                print(f"❌ Erreur {response.status_code}")
                return self.scan_cantine_alternative(cantine)
        
        except Exception as e:
            print(f"❌ Erreur réseau: {e}")
            return None
    
    def scan_cantine_alternative(self, cantine):
        """Méthode alternative: endpoint fridge général avec header"""
        urls = [
            'https://api.foodles.co/api/fridge/',
            f'https://api.foodles.co/api/fridge/?canteen={cantine["id"]}',
            f'https://api.foodles.co/api/fridge/?store={cantine["id"]}'
        ]
        
        for url in urls:
            try:
                print(f"🔄 Tentative alternative: {url}")
                
                # Essayer avec un header X-Canteen
                headers = self.headers.copy()
                headers['X-Canteen-ID'] = str(cantine['id'])
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'categories' in data:
                        # Vérifier si c'est bien la bonne cantine
                        canteen_info = data.get('canteen', {})
                        if canteen_info.get('id') == cantine['id'] or cantine['nom'] in canteen_info.get('name', ''):
                            print(f"✅ Données récupérées via méthode alternative")
                            return data
            except:
                continue
        
        return None
    
    def analyze_and_save(self, cantine, data):
        """Analyse et sauvegarde les données"""
        categories = data.get('categories', [])
        
        total_produits = 0
        total_unites = 0
        produits_dlc = []
        total_vegetarien = 0
        prix_list = []
        
        for cat in categories:
            items = cat.get('items', [])
            for item in items:
                total_produits += 1
                quantity = item.get('quantity', 0)
                total_unites += quantity
                prix = item.get('price', 0)
                if prix:
                    prix_list.append(prix)
                
                # Végétarien
                filter_reasons = item.get('filter_reasons', {})
                excluded_diets = filter_reasons.get('excluded_diets', [])
                if not excluded_diets or (len(excluded_diets) == 1 and 'PESCATARIAN' in excluded_diets):
                    total_vegetarien += 1
                
                # DLC
                if item.get('has_near_expiration_sale', False):
                    produits_dlc.append({
                        'nom': item.get('name', 'N/A'),
                        'category': cat.get('name', 'N/A'),
                        'quantity': quantity,
                        'price': prix
                    })
        
        # Statistiques
        prix_moyen = sum(prix_list) / len(prix_list) if prix_list else 0
        pct_veg = (total_vegetarien / total_produits * 100) if total_produits > 0 else 0
        
        print(f"📊 Résultats:")
        print(f"   • {total_produits} produits | {total_unites} unités")
        print(f"   • Prix moyen: {prix_moyen:.2f}€")
        print(f"   • 🌱 {total_vegetarien}/{total_produits} végétariens ({pct_veg:.1f}%)")
        
        if produits_dlc:
            print(f"   • 🔥 {len(produits_dlc)} produits en DLC courte:")
            for p in produits_dlc[:5]:  # Afficher max 5
                print(f"      - {p['nom']} ({p['quantity']}x, {p['price']:.2f}€)")
            if len(produits_dlc) > 5:
                print(f"      ... et {len(produits_dlc) - 5} autres")
        else:
            print(f"   • ✅ Aucun produit en DLC courte")
        
        # Sauvegarder
        filename = f"{self.data_dir}/cantine_{cantine['nom']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegardé: {filename}")
    
    def generate_comparison(self):
        """Génère un rapport comparatif"""
        print("\n" + "="*70)
        print("📊 RAPPORT COMPARATIF AUTOMATIQUE")
        print("="*70 + "\n")
        
        total_produits_all = 0
        total_unites_all = 0
        total_dlc_all = 0
        
        for nom, result in self.results.items():
            data = result['data']
            info = result['info']
            categories = data.get('categories', [])
            
            total_produits = 0
            total_unites = 0
            total_dlc = 0
            total_veg = 0
            prix_list = []
            
            for cat in categories:
                items = cat.get('items', [])
                for item in items:
                    total_produits += 1
                    total_unites += item.get('quantity', 0)
                    if item.get('price'):
                        prix_list.append(item.get('price'))
                    if item.get('has_near_expiration_sale', False):
                        total_dlc += 1
                    
                    filter_reasons = item.get('filter_reasons', {})
                    excluded_diets = filter_reasons.get('excluded_diets', [])
                    if not excluded_diets or (len(excluded_diets) == 1 and 'PESCATARIAN' in excluded_diets):
                        total_veg += 1
            
            total_produits_all += total_produits
            total_unites_all += total_unites
            total_dlc_all += total_dlc
            
            prix_moyen = sum(prix_list) / len(prix_list) if prix_list else 0
            pct_veg = (total_veg / total_produits * 100) if total_produits > 0 else 0
            
            print(f"🏢 {info['nom_complet']}")
            print(f"   📍 {info['adresse']}")
            print(f"   📦 {total_produits} produits | {total_unites} unités")
            print(f"   💰 Prix moyen: {prix_moyen:.2f}€")
            print(f"   🌱 {total_veg}/{total_produits} végétariens ({pct_veg:.1f}%)")
            print(f"   🔥 {total_dlc} produits en DLC courte")
            print()
        
        print("="*70)
        print(f"📈 TOTAL RÉSEAU WORLDLINE:")
        print(f"   • {total_produits_all} produits")
        print(f"   • {total_unites_all} unités en stock")
        print(f"   • {total_dlc_all} produits en DLC courte")
        print("="*70)
        print("\n✅ Pour un rapport détaillé: python compare_cantines.py")
        print()

def main():
    print()
    scanner = FullAutoScanner()
    count = scanner.scan_all()
    
    if count == 0:
        print("❌ Aucune cantine n'a pu être scannée")
        print("   Vérifie que tes cookies sont valides dans le .env")
    elif count < 3:
        print(f"⚠️  Seulement {count}/3 cantines scannées")
        print("   Les cookies actuels ne donnent peut-être pas accès à toutes")
    else:
        print("🎉 Scan complet de toutes les cantines Worldline!")
    
    print()

if __name__ == '__main__':
    main()
