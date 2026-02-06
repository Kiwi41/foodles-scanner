#!/usr/bin/env python3
"""
Script de comparaison des cantines Worldline
Permet de basculer entre les cantines et générer un bilan comparatif
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

class CantineComparator:
    def __init__(self):
        self.sessionid = os.getenv('FOODLES_SESSIONID')
        self.csrftoken = os.getenv('FOODLES_CSRFTOKEN')
        self.headers = {
            'Cookie': f'sessionid={self.sessionid}; csrftoken={self.csrftoken}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Referer': 'https://app.foodles.co/'
        }
        
        self.cantines = [
            {'id': 2051, 'nom': 'Worldline Copernic', 'adresse': '3 rue Copernic, 41000 Blois'},
            {'id': 2052, 'nom': 'Worldline Amazone', 'adresse': '5 rue Copernic, 41000 Blois'},
            {'id': 2053, 'nom': 'Worldline Hangar', 'adresse': '11 rue Copernic, 41000 Blois'}
        ]
        
        # Chemin relatif au script parent
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.data_dir = os.path.join(project_root, 'cantines_data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_cantine_data(self, canteen_id, nom):
        """Récupère les données d'une cantine"""
        print(f"\n🔄 Récupération des données de {nom}...")
        
        # Chercher d'abord les fichiers locaux existants
        import glob
        
        # Recherche par ID numérique
        pattern_id = f"{self.data_dir}/cantine_{canteen_id}_*.json"
        files_id = glob.glob(pattern_id)
        
        # Recherche par nom (pour Amazone, Hangar, etc.)
        nom_short = nom.split()[-1]  # Prend le dernier mot (Copernic, Amazone, Hangar)
        pattern_name = f"{self.data_dir}/cantine_{nom_short}_*.json"
        files_name = glob.glob(pattern_name)
        
        # Prendre le fichier le plus récent
        all_files = files_id + files_name
        if all_files:
            latest_file = max(all_files, key=os.path.getmtime)
            print(f"✅ Utilisation des données locales: {os.path.basename(latest_file)}")
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Utiliser fridge_raw_data.json si c'est Copernic (2051)
        if canteen_id == 2051 and os.path.exists('fridge_raw_data.json'):
            print(f"✅ Utilisation de fridge_raw_data.json")
            with open('fridge_raw_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Si pas de fichier local, faire l'appel API
        url = f'https://api.foodles.co/api/fridge/canteen/{canteen_id}/'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Sauvegarder les données brutes
                filename = f"{self.data_dir}/cantine_{canteen_id}_{datetime.now().strftime('%Y%m%d')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Données récupérées et sauvegardées dans {filename}")
                return data
            
            elif response.status_code == 403:
                print(f"🔒 Accès refusé - Cette cantine n'est pas associée à ton compte")
                print(f"   Tu es actuellement sur une autre cantine")
                return None
            
            else:
                print(f"❌ Erreur {response.status_code}")
                return None
        
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return None
    
    def analyze_cantine(self, data, nom):
        """Analyse les données d'une cantine"""
        if not data:
            return None
        
        categories = data.get('categories', [])
        
        analysis = {
            'nom': nom,
            'total_produits': 0,
            'total_stock': 0,
            'categories': {},
            'produits': [],
            'prix_moyen': 0,
            'prix_min': float('inf'),
            'prix_max': 0,
            'vegetarien_count': 0,
            'by_category': {}
        }
        
        for cat in categories:
            cat_name = cat.get('name', 'N/A')
            products = cat.get('products', [])
            
            cat_stock = 0
            cat_products = []
            
            for p in products:
                # Extraire les infos
                quantity = p.get('quantity', 0)
                price = p.get('price', {})
                if isinstance(price, dict):
                    price_val = price.get('amount', 0) / 100
                else:
                    price_val = price / 100
                
                # Vérifier si végétarien
                filter_reasons = p.get('filter_reasons', {})
                excluded_diets = filter_reasons.get('excluded_diets', []) if filter_reasons else []
                is_vegetarian = 'VEGETARIAN' not in excluded_diets
                
                product_info = {
                    'name': p.get('name', 'Sans nom'),
                    'quantity': quantity,
                    'price': price_val,
                    'category': cat_name,
                    'nutriscore': p.get('nutriscore', 'N/A'),
                    'vegetarian': is_vegetarian
                }
                
                cat_products.append(product_info)
                analysis['produits'].append(product_info)
                
                # Stats
                analysis['total_stock'] += quantity
                if price_val > 0:
                    analysis['prix_min'] = min(analysis['prix_min'], price_val)
                    analysis['prix_max'] = max(analysis['prix_max'], price_val)
                
                if is_vegetarian:
                    analysis['vegetarien_count'] += 1
            
            analysis['total_produits'] += len(products)
            analysis['by_category'][cat_name] = {
                'count': len(products),
                'stock': sum(p['quantity'] for p in cat_products),
                'products': cat_products
            }
        
        # Prix moyen
        prices = [p['price'] for p in analysis['produits'] if p['price'] > 0]
        analysis['prix_moyen'] = sum(prices) / len(prices) if prices else 0
        
        if analysis['prix_min'] == float('inf'):
            analysis['prix_min'] = 0
        
        return analysis
    
    def compare_all(self):
        """Compare toutes les cantines"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║              🏢 BILAN COMPARATIF DES CANTINES WORLDLINE               ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        
        analyses = []
        
        # Récupérer et analyser chaque cantine
        for cantine in self.cantines:
            data = self.fetch_cantine_data(cantine['id'], cantine['nom'])
            if data:
                analysis = self.analyze_cantine(data, cantine['nom'])
                if analysis:
                    analysis['adresse'] = cantine['adresse']
                    analyses.append(analysis)
        
        if not analyses:
            print("\n❌ Aucune donnée récupérée. Vérifie tes cookies et ta cantine active.")
            return
        
        # Générer le rapport comparatif
        self.generate_report(analyses)
    
    def generate_report(self, analyses):
        """Génère un rapport comparatif détaillé"""
        print("\n" + "="*70)
        print("📊 SYNTHÈSE COMPARATIVE")
        print("="*70 + "\n")
        
        # Vue d'ensemble
        for analysis in analyses:
            print(f"🏢 {analysis['nom']}")
            print(f"   📍 {analysis['adresse']}")
            print(f"   📦 {analysis['total_produits']} produits | {analysis['total_stock']} unités")
            print(f"   💰 Prix moyen: {analysis['prix_moyen']:.2f}€ ({analysis['prix_min']:.2f}€ - {analysis['prix_max']:.2f}€)")
            print(f"   🌱 {analysis['vegetarien_count']}/{analysis['total_produits']} végétariens ({analysis['vegetarien_count']/analysis['total_produits']*100:.1f}%)")
            print()
        
        # Comparaison par catégorie
        print("\n" + "="*70)
        print("📂 COMPARAISON PAR CATÉGORIE")
        print("="*70 + "\n")
        
        # Trouver toutes les catégories
        all_categories = set()
        for analysis in analyses:
            all_categories.update(analysis['by_category'].keys())
        
        for cat in sorted(all_categories):
            print(f"📂 {cat}")
            print("─" * 70)
            for analysis in analyses:
                cat_data = analysis['by_category'].get(cat, {'count': 0, 'stock': 0})
                print(f"   {analysis['nom'][:25]:<25}: {cat_data['count']:2d} produits | {cat_data['stock']:3d} unités")
            print()
        
        # Top produits
        print("\n" + "="*70)
        print("🏆 TOP 10 PRODUITS LES PLUS STOCKÉS")
        print("="*70 + "\n")
        
        all_products = []
        for analysis in analyses:
            for p in analysis['produits']:
                all_products.append({
                    **p,
                    'cantine': analysis['nom']
                })
        
        all_products.sort(key=lambda x: x['quantity'], reverse=True)
        
        for i, p in enumerate(all_products[:10], 1):
            veg_icon = "🌱" if p['vegetarian'] else "🥩"
            print(f"{i:2d}. {veg_icon} {p['name'][:40]:<40} | {p['quantity']:2d}x | {p['price']:.2f}€")
            print(f"    └─ {p['cantine']} - {p['category']}")
        
        # Sauvegarder le rapport
        report_file = f"{self.data_dir}/bilan_comparatif_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'cantines': analyses,
                'top_products': all_products[:50]
            }, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*70)
        print(f"💾 Rapport sauvegardé: {report_file}")
        print("="*70)
    
    def show_products_comparison(self, product_name):
        """Compare un produit spécifique entre les cantines"""
        print(f"\n🔍 Recherche de '{product_name}' dans les cantines...\n")
        
        found = False
        for cantine in self.cantines:
            filename = f"{self.data_dir}/cantine_{cantine['id']}_{datetime.now().strftime('%Y%m%d')}.json"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                categories = data.get('categories', [])
                for cat in categories:
                    for p in cat.get('products', []):
                        name = p.get('name', '')
                        if product_name.lower() in name.lower():
                            found = True
                            price = p.get('price', {})
                            if isinstance(price, dict):
                                price_val = price.get('amount', 0) / 100
                            else:
                                price_val = price / 100
                            
                            print(f"🏢 {cantine['nom']}")
                            print(f"   • {name}")
                            print(f"   📦 Stock: {p.get('quantity', 0)} unités")
                            print(f"   💰 Prix: {price_val:.2f}€")
                            print(f"   🏷️  Nutriscore: {p.get('nutriscore', 'N/A')}")
                            print()
        
        if not found:
            print(f"❌ Produit '{product_name}' non trouvé dans les cantines enregistrées")


def main():
    comparator = CantineComparator()
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║            🏢 COMPARATEUR DE CANTINES WORLDLINE                        ║
╚════════════════════════════════════════════════════════════════════════╝

Options:
  1. Comparer toutes les cantines (nécessite d'avoir accès à chacune)
  2. Rechercher un produit spécifique
  3. Afficher les données sauvegardées

⚠️  NOTE: Tu dois changer de cantine dans l'app Foodles pour capturer
   les données des autres sites. Procédure:
   1. Connecte-toi sur app.foodles.co
   2. Change de cantine dans ton profil
   3. Relance ce script pour capturer les données
   4. Répète pour chaque cantine

""")
    
    choice = input("Ton choix (1/2/3): ").strip()
    
    if choice == "1":
        comparator.compare_all()
    
    elif choice == "2":
        product = input("\nNom du produit à rechercher: ").strip()
        comparator.show_products_comparison(product)
    
    elif choice == "3":
        data_dir = comparator.data_dir
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            if files:
                print(f"\n📁 Fichiers disponibles dans {data_dir}:")
                for f in files:
                    print(f"   • {f}")
            else:
                print(f"\n❌ Aucun fichier trouvé dans {data_dir}")
        else:
            print(f"\n❌ Dossier {data_dir} introuvable")
    
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
