#!/usr/bin/env python3
"""Script de capture manuelle simple - copie juste les cookies depuis le navigateur"""

print("""
╔════════════════════════════════════════════════════════════════════════╗
║              📸 CAPTURE MANUELLE D'UNE CANTINE                         ║
╚════════════════════════════════════════════════════════════════════════╝

1. Va sur app.foodles.co et connecte-toi
2. Change de cantine si nécessaire (Amazone ou Hangar)
3. Ouvre DevTools (F12) → Application → Cookies → app.foodles.co
4. Copie les valeurs de sessionid et csrftoken
""")

sessionid = input("\n📋 Colle le sessionid: ").strip()
csrftoken = input("📋 Colle le csrftoken: ").strip()
cantine_nom = input("📋 Nom de la cantine (ex: Amazone): ").strip()

if not sessionid or not csrftoken:
    print("❌ Cookies manquants")
    exit(1)

import requests
import json
from datetime import datetime
import os

headers = {
    'Cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Referer': 'https://app.foodles.co/'
}

print(f"\n🔍 Capture de {cantine_nom}...\n")

# Récupérer les infos client
try:
    response = requests.get('https://api.foodles.co/api/client/', headers=headers, timeout=10)
    if response.status_code == 200:
        client = response.json()
        canteen_id = client.get('canteen')
        canteen_name = client.get('canteen_name')
        print(f"✅ Connecté sur: {canteen_name} (ID: {canteen_id})")
    else:
        print(f"⚠️  Impossible de vérifier la cantine (erreur {response.status_code})")
        canteen_id = None
except Exception as e:
    print(f"❌ Erreur: {e}")
    canteen_id = None

# Récupérer le frigo
print(f"\n📦 Récupération des données du frigo...")

try:
    response = requests.get('https://api.foodles.co/api/fridge/', headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        # Analyser
        categories = data.get('categories', [])
        total_products = 0
        total_stock = 0
        dlc_products = []
        
        for cat in categories:
            products = cat.get('products', [])
            total_products += len(products)
            for p in products:
                qty = p.get('quantity', 0)
                total_stock += qty
                
                if p.get('has_near_expiration_sale', False):
                    dlc_products.append({
                        'name': p.get('name'),
                        'category': cat.get('name'),
                        'quantity': qty
                    })
        
        print(f"\n✅ Capture réussie!")
        print(f"   • {total_products} produits")
        print(f"   • {total_stock} unités en stock")
        print(f"   • {len(dlc_products)} produits en DLC courte")
        
        if dlc_products:
            print(f"\n🔥 PRODUITS EN DLC COURTE:")
            for p in dlc_products:
                print(f"   • {p['name']} ({p['category']}) - {p['quantity']}x")
        
        # Sauvegarder
        os.makedirs('cantines_data', exist_ok=True)
        
        if canteen_id:
            filename = f"cantines_data/cantine_{canteen_id}_{datetime.now().strftime('%Y%m%d')}.json"
        else:
            filename = f"cantines_data/cantine_{cantine_nom}_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Données sauvegardées: {filename}")
        print(f"\n✅ C'est bon ! Lance maintenant:")
        print(f"   python compare_cantines.py")
        
    else:
        print(f"❌ Erreur {response.status_code}")
        print(response.text[:200])

except Exception as e:
    print(f"❌ Erreur: {e}")
