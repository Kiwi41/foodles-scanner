#!/usr/bin/env python3
"""
Affiche un tableau de synthèse des produits en DLC courte
"""

import json
import os
from datetime import datetime

def load_cantines_data():
    """Charge les données des 3 cantines"""
    cantines = ['Copernic', 'Amazone', 'Hangar']
    products_dlc = []
    date_str = datetime.now().strftime('%Y%m%d')
    
    for cantine in cantines:
        filename = f"cantines_data/cantine_{cantine}_{date_str}.json"
        if not os.path.exists(filename):
            print(f"⚠️  Fichier non trouvé: {filename}")
            continue
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for category in data.get('categories', []):
                items = category.get('items', []) or category.get('products', [])
                for item in items:
                    if item.get('has_near_expiration_sale', False):
                        price = item.get('price', {})
                        if isinstance(price, dict):
                            price_val = price.get('amount', 0)
                        else:
                            price_val = price
                        
                        products_dlc.append({
                            'cantine': cantine,
                            'nom': item.get('name', 'N/A'),
                            'categorie': category.get('name', 'N/A'),
                            'prix': price_val / 100 if price_val else 0,
                            'quantite': item.get('quantity', 0),
                            'vegetarien': '🌱' if item.get('is_vegetarian', False) else ''
                        })
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {cantine}: {e}")
    
    return products_dlc, cantines

def display_table(products_dlc, cantines):
    """Affiche le tableau des produits en DLC"""
    if not products_dlc:
        print("✅ Aucun produit en DLC courte trouvé!")
        return
    
    print("╔" + "═" * 98 + "╗")
    print("║" + " " * 25 + f"🔥 PRODUITS EN DLC COURTE - {datetime.now().strftime('%d/%m/%Y')}" + " " * 28 + "║")
    print("╠" + "═" * 98 + "╣")
    print("║ CANTINE    │ PRODUIT" + " " * 32 + "│ CATÉGORIE" + " " * 9 + "│ PRIX   │ QTÉ │ 🌱 ║")
    print("╠" + "═" * 98 + "╣")
    
    for p in sorted(products_dlc, key=lambda x: (x['cantine'], x['prix'])):
        cantine = p['cantine'][:10].ljust(10)
        nom = p['nom'][:39].ljust(39)
        cat = p['categorie'][:18].ljust(18)
        prix = f"{p['prix']:.2f}€".rjust(6)
        qte = str(p['quantite']).rjust(3)
        veg = p['vegetarien'].center(2)
        
        print(f"║ {cantine} │ {nom} │ {cat} │ {prix} │ {qte} │ {veg} ║")
    
    print("╚" + "═" * 98 + "╝")
    
    # Statistiques
    print(f"\n📊 Total: {len(products_dlc)} produits en DLC courte")
    
    print("\n📍 Par cantine:")
    for cantine in cantines:
        count = sum(1 for p in products_dlc if p['cantine'] == cantine)
        total_units = sum(p['quantite'] for p in products_dlc if p['cantine'] == cantine)
        total_value = sum(p['prix'] * p['quantite'] for p in products_dlc if p['cantine'] == cantine)
        if count > 0:
            print(f"   • {cantine}: {count} produits, {total_units} unités, {total_value:.2f}€ de valeur")
    
    total_value = sum(p['prix'] * p['quantite'] for p in products_dlc)
    total_vege = sum(1 for p in products_dlc if p['vegetarien'])
    print(f"\n💰 Valeur totale en DLC: {total_value:.2f}€")
    print(f"🌱 Produits végétariens: {total_vege}/{len(products_dlc)}")
    
    # Meilleures affaires
    if products_dlc:
        cheapest = min(products_dlc, key=lambda x: x['prix'])
        print(f"\n💡 Meilleure affaire: {cheapest['nom']} à {cheapest['prix']:.2f}€ ({cheapest['cantine']})")

def main():
    print("🔍 Chargement des données...\n")
    products_dlc, cantines = load_cantines_data()
    display_table(products_dlc, cantines)

if __name__ == '__main__':
    main()
