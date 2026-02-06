#!/usr/bin/env python3
"""
Capture des 3 cantines en changeant la cantine active puis en récupérant le frigo
"""

import requests
import json
from datetime import datetime
import time

# Nouveaux credentials valides
sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'

headers = {
    'Cookie': f'sessionid={sessionid}; csrftoken={csrftoken}',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Referer': 'https://app.foodles.co/',
    'X-CSRFToken': csrftoken,
    'Content-Type': 'application/json'
}

cantines = {
    'Copernic': 2051,
    'Amazone': 2052,
    'Hangar': 2053
}

print("🔄 Capture des données des 3 cantines...\n")

for nom, cantine_id in cantines.items():
    try:
        print(f"📡 {nom} (ID: {cantine_id})...")
        
        # Étape 1: Changer de cantine active
        print(f"   🔄 Changement de cantine...")
        change_response = requests.patch(
            'https://api.foodles.co/api/client/',
            headers=headers,
            json={'canteen': cantine_id},
            timeout=10
        )
        
        if change_response.status_code == 200:
            print(f"   ✅ Cantine changée")
        else:
            print(f"   ⚠️  Changement: statut {change_response.status_code}")
        
        # Petite pause pour que le serveur prenne en compte
        time.sleep(1)
        
        # Étape 2: Récupérer le frigo
        print(f"   📦 Récupération du frigo...")
        fridge_response = requests.get(
            'https://api.foodles.co/api/fridge/',
            headers=headers,
            timeout=10
        )
        
        if fridge_response.status_code == 200:
            data = fridge_response.json()
            
            # Sauvegarder
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f'cantines_data/cantine_{nom}_{date_str}.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Analyser
            categories = data.get('categories', [])
            nb_produits = sum(len(cat.get('products', [])) for cat in categories)
            nb_unites = sum(p.get('quantity', 0) for cat in categories for p in cat.get('products', []))
            
            print(f"   ✅ {nb_produits} produits, {nb_unites} unités → {filename}\n")
        else:
            print(f"   ❌ Erreur frigo: {fridge_response.status_code}\n")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")

print("✅ Capture terminée!")
