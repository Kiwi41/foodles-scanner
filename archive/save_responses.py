"""
Sauvegarde et analyse détaillée des réponses de l'API Foodles
"""
from foodles_api import FoodlesAPI
from rsc_parser import RSCParser, parse_rsc_response
from dotenv import load_dotenv
import json
import os
from datetime import datetime


class ResponseSaver:
    """Classe pour sauvegarder et analyser les réponses de l'API"""
    
    def __init__(self, output_dir: str = "api_responses"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_response(self, endpoint_name: str, response_data: dict, parsed_data: dict = None):
        """
        Sauvegarde une réponse API avec analyse
        
        Args:
            endpoint_name: Nom de l'endpoint (pour le fichier)
            response_data: Données brutes de la réponse
            parsed_data: Données parsées (optionnel)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{endpoint_name}_{timestamp}"
        
        # Sauvegarder le contenu brut
        if 'raw_content' in response_data:
            raw_file = os.path.join(self.output_dir, f"{filename}_raw.txt")
            with open(raw_file, 'w', encoding='utf-8') as f:
                f.write(response_data['raw_content'])
            print(f"📄 Contenu brut sauvegardé: {raw_file}")
        
        # Sauvegarder la réponse complète
        response_file = os.path.join(self.output_dir, f"{filename}_response.json")
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        print(f"📦 Réponse complète sauvegardée: {response_file}")
        
        # Sauvegarder l'analyse parsée
        if parsed_data:
            parsed_file = os.path.join(self.output_dir, f"{filename}_parsed.json")
            with open(parsed_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
            print(f"🔍 Analyse parsée sauvegardée: {parsed_file}")
    
    def analyze_and_save(self, endpoint_name: str, response_data: dict):
        """
        Analyse et sauvegarde une réponse complète
        
        Args:
            endpoint_name: Nom de l'endpoint
            response_data: Données de la réponse
        """
        print(f"\n{'='*60}")
        print(f"📊 Analyse de: {endpoint_name}")
        print(f"{'='*60}")
        
        # Parser si c'est du RSC
        parsed_data = None
        if 'raw_content' in response_data:
            parsed_data = parse_rsc_response(response_data)
            
            # Afficher les statistiques
            summary = parsed_data['summary']
            print(f"📈 Statistiques:")
            print(f"   - Lignes: {summary['total_lines']}")
            print(f"   - Fragments: {summary['fragments_count']}")
            print(f"   - Modules: {summary['modules_count']}")
            print(f"   - Entrées de données: {summary['data_entries']}")
            print(f"   - Objets JSON: {len(parsed_data['all_json_objects'])}")
            
            # Recherche de contenu intéressant
            parser = RSCParser(response_data['raw_content'])
            keywords = [
                'product', 'price', 'name', 'title', 'description',
                'category', 'available', 'stock', 'menu', 'order',
                'cart', 'user', 'canteen', 'delivery', 'meal'
            ]
            
            print(f"\n🔍 Recherche de mots-clés:")
            found_keywords = {}
            for keyword in keywords:
                results = parser.search_in_content(keyword)
                if results:
                    found_keywords[keyword] = len(results)
                    print(f"   - '{keyword}': {len(results)} occurrences")
            
            # Extraire des exemples de contenu
            if parsed_data['all_json_objects']:
                print(f"\n📋 Exemples d'objets JSON:")
                for i, obj in enumerate(parsed_data['all_json_objects'][:5], 1):
                    print(f"   {i}. {json.dumps(obj, ensure_ascii=False)[:100]}...")
        
        # Sauvegarder tout
        self.save_response(endpoint_name, response_data, parsed_data)
        
        return parsed_data


def main():
    """Fonction principale pour sauvegarder et analyser les réponses"""
    load_dotenv()
    
    # Configuration
    session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
    csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    
    # Créer le client API et le saver
    api = FoodlesAPI(session_id, csrf_token)
    saver = ResponseSaver()
    
    # Configurer les paramètres de livraison
    api.set_delivery_settings(
        canteen_id=2051,
        canteen_name="Worldline Copernic",
        delivery_date="2026-01-30"
    )
    
    print("🚀 DÉMARRAGE DE L'ANALYSE COMPLÈTE")
    print("=" * 60)
    
    # Tester et sauvegarder le frigo
    try:
        print("\n📦 Récupération du frigo...")
        fridge_data = api.get_fridge()
        saver.analyze_and_save("fridge", fridge_data)
    except Exception as e:
        print(f"❌ Erreur frigo: {e}")
    
    # Tester d'autres endpoints
    endpoints_to_test = [
        ("canteen", "/canteen", {"_rsc": "1d46b"}),
        ("home", "/", {"_rsc": "1d46b"}),
        ("account", "/account", {"_rsc": "1d46b"}),
    ]
    
    for name, endpoint, params in endpoints_to_test:
        try:
            print(f"\n🔍 Test de {name} ({endpoint})...")
            response = api.make_request(endpoint, params=params)
            saver.analyze_and_save(name, response)
        except Exception as e:
            print(f"❌ Erreur {name}: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"✅ Analyse terminée!")
    print(f"📁 Fichiers sauvegardés dans: {saver.output_dir}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
