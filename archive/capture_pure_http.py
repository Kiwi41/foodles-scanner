#!/usr/bin/env python3
"""
Capture 100% en HTTP pur - SANS navigateur!
"""

import requests
import json
from datetime import datetime
import time

sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'

headers = {
    'Cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
    'User-Agent': 'Mozilla/5.0',
    'X-CSRFToken': csrftoken,
    'Content-Type': 'application/json',
}

cantines = {
    'Copernic': 2051,
    'Amazone': 2052,
    'Hangar': 2053
}

print("╔════════════════════════════════════════════════════════════════════════╗")
print("║       ⚡ CAPTURE 100% HTTP - SANS NAVIGATEUR                           ║")
print("╚════════════════════════════════════════════════════════════════════════╝\n")

captured = 0

for nom, canteen_id in cantines.items():
    print(f"{'='*70}")
    print(f"🔄 {nom} (ID: {canteen_id})")
    print(f"{'='*70}")
    
    # Changer de cantine
    print(f"   🔄 Changement de cantine...")
    try:
        r = requests.patch(
            'https://api.foodles.co/api/client/',
            json={'canteen': canteen_id},
            headers=headers,
            timeout=10
        )
        print(f"   📡 PATCH → {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ⚠️  Échec du changement (on récupère quand même)")
        
        time.sleep(1)
        
        # Récupérer les données du frigo
        print(f"   📦 Récupération du frigo...")
        r = requests.get('https://api.foodles.co/api/fridge/', headers=headers, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            
            # Sauvegarder
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f'cantines_data/cantine_{nom}_{date_str}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Stats
            categories = data.get('categories', [])
            nb_produits = sum(len(cat.get('products', [])) for cat in categories)
            nb_unites = sum(p.get('quantity', 0) for cat in categories for p in cat.get('products', []))
            nb_dlc = sum(1 for cat in categories for p in cat.get('products', []) if p.get('has_near_expiration_sale', False))
            
            print(f"   📊 {nb_produits} produits | {nb_unites} unités | 🔥 {nb_dlc} DLC")
            print(f"   💾 {filename}")
            print(f"✅ [{captured+1}/3] {nom} capturé!\n")
            captured += 1
        else:
            print(f"   ❌ Erreur HTTP {r.status_code}\n")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")
    
    time.sleep(1)

print(f"{'='*70}")
print(f"🎉 TERMINÉ: {captured}/3 cantines")
print(f"{'='*70}\n")

if captured == 3:
    print("✅ SUCCÈS TOTAL - SANS NAVIGATEUR!")
    print("📊 Lance: python scripts/generate_report.py")
