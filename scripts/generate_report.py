#!/usr/bin/env python3
"""
Scanner ultime - Utilise les fichiers déjà capturés pour générer un rapport complet
"""

import json
import os
import glob
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.data_dir = 'cantines_data'
        self.cantines_data = {}
    
    def load_latest_data(self):
        """Charge les données les plus récentes de chaque cantine"""
        print("📂 Chargement des données existantes...")
        
        cantines_map = {
            'Copernic': ['2051', 'Copernic'],
            'Amazone': ['2052', 'Amazone'],
            'Hangar': ['2053', 'Hangar']
        }
        
        for cantine_name, patterns_names in cantines_map.items():
            # Chercher les fichiers de cette cantine
            patterns = []
            for pattern_name in patterns_names:
                patterns.append(f"{self.data_dir}/cantine_{pattern_name}_*.json")
                patterns.append(f"{self.data_dir}/cantine_*{pattern_name}*.json")
            
            files = []
            for pattern in patterns:
                files.extend(glob.glob(pattern))
            
            if files:
                # Prendre le fichier le plus récent
                latest_file = max(files, key=os.path.getmtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cantines_data[cantine_name] = {
                        'data': data,
                        'file': latest_file
                    }
                print(f"   ✅ {cantine_name}: {os.path.basename(latest_file)}")
            else:
                print(f"   ❌ {cantine_name}: Aucun fichier trouvé")
        
        return len(self.cantines_data)
    
    def generate_full_report(self):
        """Génère un rapport complet et détaillé"""
        if not self.cantines_data:
            print("\n❌ Aucune donnée disponible")
            return
        
        print("\n" + "="*80)
        print("📊 RAPPORT COMPLET DES CANTINES WORLDLINE")
        print("="*80 + "\n")
        
        all_stats = {}
        
        for cantine_name, info in self.cantines_data.items():
            data = info['data']
            categories = data.get('categories', [])
            
            stats = {
                'total_produits': 0,
                'total_unites': 0,
                'produits_dlc': [],
                'total_vegetarien': 0,
                'prix_list': [],
                'categories': {}
            }
            
            for cat in categories:
                cat_name = cat.get('name', 'Unknown')
                # Support both 'items' and 'products' formats
                items = cat.get('items', []) or cat.get('products', [])
                
                stats['categories'][cat_name] = {
                    'produits': len(items),
                    'unites': sum(item.get('quantity', 0) for item in items)
                }
                
                for item in items:
                    stats['total_produits'] += 1
                    quantity = item.get('quantity', 0)
                    stats['total_unites'] += quantity
                    prix = item.get('price', 0)
                    # Handle price as dict or number
                    if isinstance(prix, dict):
                        prix = prix.get('amount', 0)
                    if prix and isinstance(prix, (int, float)):
                        stats['prix_list'].append(prix)
                    
                    # Végétarien
                    filter_reasons = item.get('filter_reasons', {}) or {}
                    excluded_diets = filter_reasons.get('excluded_diets', []) if isinstance(filter_reasons, dict) else []
                    if not excluded_diets or (len(excluded_diets) == 1 and 'PESCATARIAN' in excluded_diets):
                        stats['total_vegetarien'] += 1
                    
                    # DLC
                    if item.get('has_near_expiration_sale', False):
                        stats['produits_dlc'].append({
                            'nom': item.get('name', 'N/A'),
                            'category': cat_name,
                            'quantity': quantity,
                            'price': prix
                        })
            
            all_stats[cantine_name] = stats
        
        # Afficher les résultats
        for cantine_name, stats in all_stats.items():
            if stats['total_produits'] == 0:
                print(f"🏢 WORLDLINE {cantine_name.upper()}")
                print(f"{'─'*80}")
                print(f"⚠️  Données vides ou format invalide")
                print(f"\n{'='*80}\n")
                continue
            
            prix_moyen = sum(stats['prix_list']) / len(stats['prix_list']) if stats['prix_list'] else 0
            prix_min = min(stats['prix_list']) if stats['prix_list'] else 0
            prix_max = max(stats['prix_list']) if stats['prix_list'] else 0
            pct_veg = (stats['total_vegetarien'] / stats['total_produits'] * 100) if stats['total_produits'] > 0 else 0
            
            print(f"🏢 WORLDLINE {cantine_name.upper()}")
            print(f"{'─'*80}")
            print(f"📦 Produits: {stats['total_produits']}")
            print(f"📊 Stock total: {stats['total_unites']} unités")
            if prix_moyen > 0:
                print(f"💰 Prix moyen: {prix_moyen:.2f}€ ({prix_min:.2f}€ - {prix_max:.2f}€)")
            print(f"🌱 Végétariens: {stats['total_vegetarien']}/{stats['total_produits']} ({pct_veg:.1f}%)")
            print(f"🔥 DLC courte: {len(stats['produits_dlc'])} produits")
            
            # Détail par catégorie
            print(f"\n📂 Par catégorie:")
            for cat_name, cat_stats in sorted(stats['categories'].items()):
                print(f"   • {cat_name}: {cat_stats['produits']} produits, {cat_stats['unites']} unités")
            
            # Produits DLC
            if stats['produits_dlc']:
                print(f"\n🔥 Produits en DLC courte:")
                for p in stats['produits_dlc']:
                    print(f"   • {p['nom']}")
                    prix_str = f"{p['price']:.2f}€" if isinstance(p['price'], (int, float)) and p['price'] > 0 else "N/A"
                    print(f"     └─ {p['category']} | {p['quantity']}x | {prix_str}")
            else:
                print(f"\n✅ Aucun produit en DLC courte")
            
            print(f"\n{'='*80}\n")
        
        # Comparaison globale
        print("📈 COMPARAISON GLOBALE")
        print(f"{'─'*80}")
        
        total_all_produits = sum(s['total_produits'] for s in all_stats.values())
        total_all_unites = sum(s['total_unites'] for s in all_stats.values())
        total_all_dlc = sum(len(s['produits_dlc']) for s in all_stats.values())
        
        print(f"\n🏆 Classement par variété (nombre de produits):")
        sorted_by_products = sorted(all_stats.items(), key=lambda x: x[1]['total_produits'], reverse=True)
        for i, (name, stats) in enumerate(sorted_by_products, 1):
            print(f"   {i}. {name}: {stats['total_produits']} produits")
        
        print(f"\n📦 Classement par stock (unités disponibles):")
        sorted_by_stock = sorted(all_stats.items(), key=lambda x: x[1]['total_unites'], reverse=True)
        for i, (name, stats) in enumerate(sorted_by_stock, 1):
            print(f"   {i}. {name}: {stats['total_unites']} unités")
        
        print(f"\n🔥 Classement par DLC courte:")
        sorted_by_dlc = sorted(all_stats.items(), key=lambda x: len(x[1]['produits_dlc']), reverse=True)
        for i, (name, stats) in enumerate(sorted_by_dlc, 1):
            print(f"   {i}. {name}: {len(stats['produits_dlc'])} produits")
        
        print(f"\n{'='*80}")
        print(f"📊 TOTAL RÉSEAU WORLDLINE")
        print(f"{'='*80}")
        print(f"   • {len(all_stats)} cantines scannées")
        print(f"   • {total_all_produits} produits différents")
        print(f"   • {total_all_unites} unités en stock")
        print(f"   • {total_all_dlc} produits en DLC courte")
        print(f"{'='*80}\n")

def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║            📊 GÉNÉRATEUR DE RAPPORT AUTOMATIQUE                        ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print()
    
    generator = ReportGenerator()
    count = generator.load_latest_data()
    
    if count == 0:
        print("\n❌ Aucune donnée trouvée dans cantines_data/")
        print("   Lance d'abord: python capture_manual_cantine.py")
    else:
        generator.generate_full_report()
        
        if count < 3:
            print(f"💡 Tu as {count}/3 cantines. Pour capturer les manquantes:")
            print("   python capture_manual_cantine.py")

if __name__ == '__main__':
    main()
