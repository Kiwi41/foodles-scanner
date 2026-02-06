"""
Debug - Affiche le contenu brut complet
"""
from foodles_api import FoodlesAPI

# Configuration
session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"

api = FoodlesAPI(session_id, csrf_token)
api.set_delivery_settings(2051, "Worldline Copernic", "2026-01-30")

print("Récupération du frigo...")
fridge = api.get_fridge()

if 'raw_content' in fridge:
    content = fridge['raw_content']
    print(f"Longueur totale: {len(content)} caractères")
    print(f"Nombre de lignes: {content.count(chr(10))}")
    
    # Sauvegarder le contenu complet
    with open('fridge_full_content.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Contenu sauvegardé dans fridge_full_content.txt")
    
    # Afficher un extrait avec les produits
    if 'Boulettes' in content or 'Coca' in content or 'Yaourt' in content:
        print("\n✅ Des produits sont présents dans le contenu!")
        
        # Trouver et afficher un extrait avec un produit
        idx = content.find('Boulettes')
        if idx == -1:
            idx = content.find('Coca')
        if idx == -1:
            idx = content.find('Yaourt')
        
        if idx != -1:
            print(f"\nExtrait autour du produit (position {idx}):")
            print(content[max(0, idx-200):idx+500])
    else:
        print("\n❌ Pas de produits trouvés dans le contenu")
        print("\nPremiers 2000 caractères:")
        print(content[:2000])
