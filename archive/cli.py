"""
CLI interactif pour l'API Foodles
"""
from foodles_api import FoodlesAPI
from rsc_parser import RSCParser, parse_rsc_response
from config import config
from dotenv import load_dotenv
import json
import sys


class FoodlesCLI:
    """Interface en ligne de commande pour Foodles"""
    
    def __init__(self, api: FoodlesAPI):
        self.api = api
        self.running = True
    
    def print_menu(self):
        """Affiche le menu principal"""
        print("\n" + "=" * 60)
        print("🍽️  FOODLES API - MENU PRINCIPAL")
        print("=" * 60)
        print("1. 📦 Consulter le frigo")
        print("2. 🔍 Explorer un endpoint personnalisé")
        print("3. 🛒 Voir le panier")
        print("4. 🏢 Changer de cantine")
        print("5. 📅 Changer la date de livraison")
        print("6. 🔎 Rechercher dans le contenu")
        print("7. 💾 Sauvegarder une réponse")
        print("8. 📊 Voir les statistiques")
        print("0. ❌ Quitter")
        print("=" * 60)
    
    def get_fridge(self):
        """Récupère et affiche les données du frigo"""
        try:
            print("\n⏳ Récupération du frigo...")
            fridge_data = self.api.get_fridge()
            
            if 'raw_content' in fridge_data:
                parsed = parse_rsc_response(fridge_data)
                
                print(f"\n✅ Frigo récupéré!")
                print(f"📊 Résumé:")
                print(f"   - Lignes: {parsed['summary']['total_lines']}")
                print(f"   - Modules: {parsed['summary']['modules_count']}")
                print(f"   - Objets JSON: {len(parsed['all_json_objects'])}")
                
                if parsed['all_json_objects']:
                    print(f"\n📋 Premiers objets:")
                    for i, obj in enumerate(parsed['all_json_objects'][:3], 1):
                        print(f"   {i}. {json.dumps(obj, ensure_ascii=False)[:80]}...")
                
                # Demander si l'utilisateur veut voir plus
                choice = input("\n👀 Voir le contenu complet? (o/n): ").lower()
                if choice == 'o':
                    print("\n" + fridge_data['raw_content'][:1000] + "...")
            else:
                print(f"\n✅ Réponse: {json.dumps(fridge_data, indent=2, ensure_ascii=False)}")
        
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    def custom_endpoint(self):
        """Permet de tester un endpoint personnalisé"""
        print("\n🔍 Endpoint personnalisé")
        endpoint = input("Endpoint (ex: /canteen/fridge): ").strip()
        
        if not endpoint:
            print("❌ Endpoint vide!")
            return
        
        # Demander les paramètres
        use_rsc = input("Ajouter le paramètre _rsc? (o/n): ").lower()
        params = {"_rsc": "1d46b"} if use_rsc == 'o' else None
        
        try:
            print(f"\n⏳ Requête vers {endpoint}...")
            response = self.api.make_request(endpoint, params=params)
            
            print(f"\n✅ Succès!")
            if 'raw_content' in response:
                print(f"📄 Contenu (premiers 500 caractères):")
                print(response['raw_content'][:500] + "...")
            else:
                print(json.dumps(response, indent=2, ensure_ascii=False)[:500])
        
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    def change_canteen(self):
        """Change les paramètres de la cantine"""
        print("\n🏢 Changer de cantine")
        canteen_id = input("ID de la cantine (ex: 2051): ").strip()
        canteen_name = input("Nom de la cantine (ex: Worldline Copernic): ").strip()
        
        if canteen_id and canteen_name:
            try:
                self.api.set_delivery_settings(
                    canteen_id=int(canteen_id),
                    canteen_name=canteen_name,
                    delivery_date=config.delivery_date
                )
                print(f"✅ Cantine changée: {canteen_name} (ID: {canteen_id})")
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def change_date(self):
        """Change la date de livraison"""
        print("\n📅 Changer la date de livraison")
        date = input("Date (YYYY-MM-DD, ex: 2026-01-30): ").strip()
        
        if date:
            config.delivery_date = date
            self.api.set_delivery_settings(
                canteen_id=config.canteen_id,
                canteen_name=config.canteen_name,
                delivery_date=date
            )
            print(f"✅ Date changée: {date}")
    
    def search_content(self):
        """Recherche dans le contenu RSC"""
        print("\n🔎 Rechercher dans le contenu")
        keyword = input("Mot-clé à rechercher: ").strip()
        
        if not keyword:
            print("❌ Mot-clé vide!")
            return
        
        try:
            print(f"\n⏳ Récupération du frigo...")
            fridge_data = self.api.get_fridge()
            
            if 'raw_content' in fridge_data:
                parser = RSCParser(fridge_data['raw_content'])
                results = parser.search_in_content(keyword)
                
                print(f"\n🔍 Résultats pour '{keyword}': {len(results)} occurrences")
                for i, result in enumerate(results[:10], 1):
                    print(f"\n{i}. {result[:150]}...")
            else:
                print("❌ Pas de contenu RSC à rechercher")
        
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    def save_response(self):
        """Sauvegarde une réponse dans un fichier"""
        print("\n💾 Sauvegarder une réponse")
        filename = input("Nom du fichier (ex: fridge_response.json): ").strip()
        
        if not filename:
            print("❌ Nom de fichier vide!")
            return
        
        try:
            print(f"\n⏳ Récupération du frigo...")
            fridge_data = self.api.get_fridge()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(fridge_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Sauvegardé dans: {filename}")
        
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    def show_stats(self):
        """Affiche des statistiques sur l'API"""
        print("\n📊 Statistiques")
        print(f"🏢 Cantine: {config.canteen_name} (ID: {config.canteen_id})")
        print(f"📅 Date de livraison: {config.delivery_date}")
        print(f"🔐 Session ID: {self.api.session_id[:20]}...")
        print(f"🔑 CSRF Token: {self.api.csrf_token[:20]}...")
    
    def run(self):
        """Lance l'interface CLI"""
        print("\n🎉 Bienvenue dans Foodles CLI!")
        
        while self.running:
            self.print_menu()
            choice = input("\n👉 Votre choix: ").strip()
            
            if choice == '1':
                self.get_fridge()
            elif choice == '2':
                self.custom_endpoint()
            elif choice == '3':
                print("\n🛒 Fonction panier en développement...")
            elif choice == '4':
                self.change_canteen()
            elif choice == '5':
                self.change_date()
            elif choice == '6':
                self.search_content()
            elif choice == '7':
                self.save_response()
            elif choice == '8':
                self.show_stats()
            elif choice == '0':
                print("\n👋 Au revoir!")
                self.running = False
            else:
                print("\n❌ Choix invalide!")
            
            if self.running and choice != '0':
                input("\n⏎ Appuyez sur Entrée pour continuer...")


def main():
    """Point d'entrée du CLI"""
    load_dotenv()
    
    # Configuration
    session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
    csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    
    # Créer le client API
    api = FoodlesAPI(session_id, csrf_token)
    api.set_delivery_settings(
        canteen_id=2051,
        canteen_name="Worldline Copernic",
        delivery_date="2026-01-30"
    )
    
    # Lancer le CLI
    cli = FoodlesCLI(api)
    cli.run()


if __name__ == "__main__":
    main()
