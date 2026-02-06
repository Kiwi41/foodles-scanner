"""
Exemple d'utilisation de l'API Foodles
"""
from foodles_api import FoodlesAPI
from config import config
from rsc_parser import RSCParser, parse_rsc_response
from dotenv import load_dotenv
import json


def main():
    # Charger les variables d'environnement depuis .env
    load_dotenv()
    
    # Option 1: Utiliser les variables d'environnement
    if config.is_configured():
        session_id, csrf_token = config.get_credentials()
    else:
        # Option 2: Définir manuellement les tokens
        # Récupérez ces valeurs depuis les cookies de votre navigateur
        session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
        csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
        config.set_credentials(session_id, csrf_token)
    
    # Créer le client API
    api = FoodlesAPI(session_id, csrf_token)
    
    # Configurer les paramètres de livraison (optionnel)
    api.set_delivery_settings(
        canteen_id=config.canteen_id,
        canteen_name=config.canteen_name,
        delivery_date=config.delivery_date
    )
    
    print("=== Récupération des données du frigo ===")
    try:
        fridge_data = api.get_fridge()
        print(f"Status: {fridge_data.get('status_code', 'N/A')}")
        
        # Parser le contenu RSC
        if 'raw_content' in fridge_data:
            print("\n--- Analyse du contenu RSC ---")
            parsed = parse_rsc_response(fridge_data)
            
            # Afficher le résumé
            print(f"Lignes totales: {parsed['summary']['total_lines']}")
            print(f"Fragments: {parsed['summary']['fragments_count']}")
            print(f"Modules: {parsed['summary']['modules_count']}")
            print(f"Entrées de données: {parsed['summary']['data_entries']}")
            
            # Afficher les produits trouvés
            if parsed['products']:
                print(f"\n📦 Produits trouvés: {len(parsed['products'])}")
                for i, product in enumerate(parsed['products'][:3], 1):
                    print(f"  {i}. {product.get('name', 'N/A')} - {product.get('price', 'N/A')}")
            
            # Afficher les objets JSON trouvés
            if parsed['all_json_objects']:
                print(f"\n📄 Objets JSON trouvés: {len(parsed['all_json_objects'])}")
                for i, obj in enumerate(parsed['all_json_objects'][:3], 1):
                    print(f"  {i}. Clés: {list(obj.keys())}")
            
            # Recherche de mots-clés intéressants
            parser = RSCParser(fridge_data['raw_content'])
            print("\n🔍 Recherche de mots-clés:")
            
            keywords = ['product', 'price', 'name', 'category', 'available']
            for keyword in keywords:
                results = parser.search_in_content(keyword)
                if results:
                    print(f"  - '{keyword}': {len(results)} occurrences")
        else:
            print(json.dumps(fridge_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la récupération du frigo: {e}")
    
    print("\n=== Récupération du menu ===")
    try:
        menu_data = api.get_canteen_menu()
        print(f"Status: {menu_data.get('status_code', 'N/A')}")
        
        if 'raw_content' in menu_data:
            content = menu_data['raw_content']
            print(f"Contenu (premiers 500 caractères): {content[:500]}...")
        else:
            print(json.dumps(menu_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la récupération du menu: {e}")
    
    print("\n=== Récupération du panier ===")
    try:
        cart_data = api.get_cart()
        print(f"Status: {cart_data.get('status_code', 'N/A')}")
        
        if 'raw_content' in cart_data:
            content = cart_data['raw_content']
            print(f"Contenu (premiers 500 caractères): {content[:500]}...")
        else:
            print(json.dumps(cart_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la récupération du panier: {e}")
    
    print("\n=== Requête personnalisée ===")
    try:
        # Exemple de requête personnalisée
        custom_data = api.make_request(
            endpoint="/canteen/fridge",
            method="GET",
            params={"_rsc": "1d46b"}
        )
        print(f"Requête personnalisée réussie!")
    except Exception as e:
        print(f"Erreur lors de la requête personnalisée: {e}")


if __name__ == "__main__":
    main()
