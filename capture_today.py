#!/usr/bin/env python3
"""Capture rapide des 3 cantines"""

import os
import json
from datetime import datetime
from lib.foodles_real_api import FoodlesRealAPI

# Utiliser les credentials du .env
sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'

api = FoodlesRealAPI(session_id=sessionid, csrf_token=csrftoken)

cantines = {
    'Copernic': 2051,
    'Amazone': 2052,
    'Hangar': 2053
}

print("🔄 Capture des données des 3 cantines...\n")

for nom, cantine_id in cantines.items():
    try:
        print(f"📡 {nom} (ID: {cantine_id})...")
        data = api.get_store_menu(store_id=cantine_id)
        
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f'cantines_data/cantine_{nom}_{date_str}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        nb_produits = sum(len(cat.get('items', [])) for cat in data.get('categories', []))
        print(f"   ✅ {nb_produits} produits capturés → {filename}\n")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}\n")

print("✅ Capture terminée!")
