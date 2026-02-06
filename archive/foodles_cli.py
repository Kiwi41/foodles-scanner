#!/usr/bin/env python3
"""
CLI interactive pour Foodles avec autocomplétion et commandes avancées.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from foodles_complete import FoodlesClient
import json
from datetime import datetime

class FoodlesCLI:
    def __init__(self):
        self.client = FoodlesClient()
        self.products = []
        self.running = True
        
    def load_products(self):
        """Charge les produits"""
        print("⏳ Chargement des produits...")
        self.products = self.client.get_all_products()
        print(f"✅ {len(self.products)} produits chargés\n")
        
    def cmd_help(self, args):
        """Affiche l'aide"""
        print("""
╔════════════════════════════════════════════════════════════════════════╗
║                    🍽️  FOODLES CLI - AIDE                             ║
╚════════════════════════════════════════════════════════════════════════╝

📋 COMMANDES DISPONIBLES:

   list [categorie]          - Liste tous les produits (ou d'une catégorie)
   search <terme>            - Recherche des produits
   show <id>                 - Affiche les détails d'un produit
   stats                     - Affiche les statistiques
   categories                - Liste les catégories
   tags                      - Liste tous les tags
   filter tag <tag>          - Filtre par tag
   export [fichier]          - Exporte les produits en JSON
   refresh                   - Recharge les produits
   user                      - Info utilisateur
   opening                   - Horaires d'ouverture
   clear                     - Efface l'écran
   help                      - Affiche cette aide
   quit, exit                - Quitte le CLI

💡 EXEMPLES:

   > search poulet           - Recherche 'poulet'
   > list Plats              - Liste les plats
   > filter tag Végétarien   - Produits végétariens
   > show 10400              - Détails du produit 10400
   > stats                   - Statistiques complètes

════════════════════════════════════════════════════════════════════════
        """)
        
    def cmd_list(self, args):
        """Liste les produits"""
        if not self.products:
            self.load_products()
            
        if args:
            category = ' '.join(args)
            filtered = self.client.get_products_by_category(category)
            print(f"\n📂 Catégorie: {category} - {len(filtered)} produits\n")
            products = filtered
        else:
            print(f"\n📋 Tous les produits ({len(self.products)})\n")
            products = self.products
            
        for i, p in enumerate(products, 1):
            price = self._format_price(p)
            print(f"{i:3}. {p.get('name', 'Sans nom')[:60]}")
            print(f"     💰 {price} | 🆔 {p.get('id')} | 📂 {p.get('category', '?')}")
            if i % 10 == 0 and i < len(products):
                response = input("\n[ENTER] pour continuer, 'q' pour arrêter: ")
                if response.lower() == 'q':
                    break
                print()
        print()
        
    def cmd_search(self, args):
        """Recherche des produits"""
        if not args:
            print("❌ Usage: search <terme>")
            return
            
        query = ' '.join(args)
        results = self.client.search_products(query)
        
        print(f"\n🔍 Recherche: '{query}' - {len(results)} résultat(s)\n")
        
        for i, p in enumerate(results, 1):
            price = self._format_price(p)
            print(f"{i}. {p.get('name', 'Sans nom')}")
            print(f"   💰 {price} | 🆔 {p.get('id')} | 📂 {p.get('category', '?')}")
            if p.get('description'):
                desc = p['description'][:100]
                print(f"   📝 {desc}{'...' if len(p['description']) > 100 else ''}")
            print()
            
    def cmd_show(self, args):
        """Affiche les détails d'un produit"""
        if not args:
            print("❌ Usage: show <id>")
            return
            
        try:
            product_id = int(args[0])
            product = self.client.get_product_by_id(product_id)
            
            if not product:
                print(f"❌ Produit {product_id} non trouvé")
                return
                
            print("\n" + "="*80)
            print(f"📦 {product.get('name', 'Sans nom')}")
            print("="*80)
            print(f"\n🆔 ID: {product.get('id')}")
            print(f"📂 Catégorie: {product.get('category', '?')}")
            print(f"💰 Prix: {self._format_price(product)}")
            
            if product.get('description'):
                print(f"\n📝 Description:\n   {product['description']}")
                
            if product.get('tags'):
                print(f"\n🏷️  Tags: {', '.join(product['tags'])}")
                
            if product.get('image'):
                print(f"\n🖼️  Image: {product['image']}")
                
            print("\n" + "="*80 + "\n")
            
        except ValueError:
            print("❌ ID invalide (doit être un nombre)")
            
    def cmd_stats(self, args):
        """Affiche les statistiques"""
        print("\n⏳ Calcul des statistiques...\n")
        stats = self.client.get_statistics()
        
        print("="*80)
        print("📊 STATISTIQUES")
        print("="*80)
        
        print(f"\n📦 Total produits: {stats['total_products']}")
        
        if stats.get('by_category'):
            print(f"\n📂 Par catégorie:")
            for cat, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
                print(f"   • {cat}: {count} produits")
                
        if stats.get('price_range'):
            pr = stats['price_range']
            print(f"\n💰 Prix:")
            print(f"   • Min: {pr['min']:.2f}€")
            print(f"   • Max: {pr['max']:.2f}€")
            print(f"   • Moyen: {pr['avg']:.2f}€")
            
        if stats.get('top_tags'):
            print(f"\n🏷️  Top 15 tags:")
            for tag, count in stats['top_tags'][:15]:
                print(f"   • {tag}: {count}x")
                
        print("\n" + "="*80 + "\n")
        
    def cmd_categories(self, args):
        """Liste les catégories"""
        if not self.products:
            self.load_products()
            
        categories = {}
        for p in self.products:
            cat = p.get('category', 'Autre')
            categories[cat] = categories.get(cat, 0) + 1
            
        print("\n📂 CATÉGORIES\n")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"   • {cat}: {count} produits")
        print()
        
    def cmd_tags(self, args):
        """Liste tous les tags"""
        if not self.products:
            self.load_products()
            
        tags = {}
        for p in self.products:
            for tag in p.get('tags', []):
                tags[tag] = tags.get(tag, 0) + 1
                
        print("\n🏷️  TOUS LES TAGS\n")
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            print(f"   • {tag}: {count}x")
        print()
        
    def cmd_filter(self, args):
        """Filtre les produits"""
        if len(args) < 2:
            print("❌ Usage: filter tag <tag>")
            return
            
        filter_type = args[0].lower()
        value = ' '.join(args[1:])
        
        if filter_type == 'tag':
            results = self.client.get_products_by_tag(value)
            print(f"\n🏷️  Tag: '{value}' - {len(results)} produits\n")
            
            for i, p in enumerate(results, 1):
                price = self._format_price(p)
                print(f"{i}. {p.get('name', 'Sans nom')[:60]}")
                print(f"   💰 {price} | 🆔 {p.get('id')} | 📂 {p.get('category', '?')}")
            print()
        else:
            print(f"❌ Type de filtre '{filter_type}' non supporté")
            
    def cmd_export(self, args):
        """Exporte les produits"""
        filename = args[0] if args else 'export.json'
        
        if not self.products:
            self.load_products()
            
        self.client.export_products(filename)
        print(f"✅ {len(self.products)} produits exportés vers {filename}")
        
    def cmd_refresh(self, args):
        """Recharge les produits"""
        self.load_products()
        
    def cmd_user(self, args):
        """Info utilisateur"""
        print("\n⏳ Récupération des infos utilisateur...\n")
        try:
            user = self.client.api.get_current_user()
            
            print("="*80)
            print("👤 UTILISATEUR")
            print("="*80)
            print(f"\n🆔 ID Client: {user.get('id')}")
            print(f"📧 Email: {user.get('email', 'N/A')}")
            print(f"👤 Nom: {user.get('first_name', '')} {user.get('last_name', '')}")
            
            if user.get('canteen'):
                print(f"\n🏢 Cantine: {user['canteen'].get('name', 'N/A')}")
                print(f"   ID: {user['canteen'].get('id')}")
                
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
    def cmd_opening(self, args):
        """Horaires d'ouverture"""
        print("\n⏳ Récupération des horaires...\n")
        try:
            opening = self.client.api.get_store_opening(2051)
            
            print("="*80)
            print("🕐 HORAIRES D'OUVERTURE")
            print("="*80)
            
            if opening:
                print(json.dumps(opening, indent=2, ensure_ascii=False))
            else:
                print("❌ Pas d'informations disponibles")
                
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
    def cmd_clear(self, args):
        """Efface l'écran"""
        print("\033[2J\033[H", end="")
        
    def cmd_quit(self, args):
        """Quitte le CLI"""
        print("\n👋 Au revoir!\n")
        self.running = False
        
    def _format_price(self, product):
        """Formate le prix"""
        price = product.get('price', 0)
        if isinstance(price, dict):
            price = price.get('value', 0)
        if price == 0:
            return "?€"
        return f"{price:.2f}€"
        
    def run(self):
        """Lance le CLI"""
        print("╔════════════════════════════════════════════════════════════════════════╗")
        print("║              🍽️  FOODLES CLI INTERACTIF                               ║")
        print("╚════════════════════════════════════════════════════════════════════════╝")
        print("\nTapez 'help' pour la liste des commandes\n")
        
        # Mapping des commandes
        commands = {
            'help': self.cmd_help,
            'list': self.cmd_list,
            'search': self.cmd_search,
            'show': self.cmd_show,
            'stats': self.cmd_stats,
            'categories': self.cmd_categories,
            'tags': self.cmd_tags,
            'filter': self.cmd_filter,
            'export': self.cmd_export,
            'refresh': self.cmd_refresh,
            'user': self.cmd_user,
            'opening': self.cmd_opening,
            'clear': self.cmd_clear,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }
        
        while self.running:
            try:
                user_input = input("foodles> ").strip()
                
                if not user_input:
                    continue
                    
                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd in commands:
                    commands[cmd](args)
                else:
                    print(f"❌ Commande '{cmd}' inconnue. Tapez 'help' pour l'aide.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Au revoir!\n")
                break
            except EOFError:
                print("\n\n👋 Au revoir!\n")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    cli = FoodlesCLI()
    cli.run()
