#!/usr/bin/env python3
"""
Démonstration offline utilisant les données déjà capturées.
Pas besoin d'authentification - utilise les fichiers JSON existants.
"""
import json
from pathlib import Path
from collections import Counter

def load_products():
    """Charge les produits depuis le fichier JSON"""
    products_file = Path(__file__).parent / 'foodles_products.json'
    
    if not products_file.exists():
        # Essayer avec fridge_raw_data.json
        raw_file = Path(__file__).parent / 'fridge_raw_data.json'
        if raw_file.exists():
            print("📦 Chargement depuis fridge_raw_data.json...")
            with open(raw_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraire les produits
            products = []
            for category in data.get('categories', []):
                for product in category.get('products', []):
                    product['category'] = category.get('name')
                    # Extraire les noms des tags
                    if 'tags' in product:
                        product['tags'] = [t['name'] if isinstance(t, dict) else t for t in product['tags']]
                    products.append(product)
            return products
        else:
            print("❌ Aucun fichier de données trouvé!")
            return []
    
    print("📦 Chargement depuis foodles_products.json...")
    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # Normaliser les tags si nécessaire
    for p in products:
        if 'tags' in p and p['tags']:
            p['tags'] = [t['name'] if isinstance(t, dict) else t for t in p['tags']]
    
    return products

def format_price(product):
    """Formate le prix"""
    price = product.get('price', 0)
    if isinstance(price, dict):
        price = price.get('value', 0)
    if price == 0:
        return "Prix non disponible"
    return f"{price:.2f}€"

def demo_recherche(products):
    """Démo de recherche"""
    print("\n" + "="*80)
    print("🔍 DÉMONSTRATION - RECHERCHE")
    print("="*80)
    
    queries = ["poulet", "compote", "coca"]
    
    for query in queries:
        results = [p for p in products if query.lower() in p.get('name', '').lower() or 
                   query.lower() in (p.get('description') or '').lower()]
        
        print(f"\n🔍 Recherche: '{query}' → {len(results)} résultat(s)")
        for i, p in enumerate(results[:3], 1):
            print(f"   {i}. {p.get('name', 'Sans nom')[:60]}")
            print(f"      💰 {format_price(p)} | 📂 {p.get('category', '?')}")

def demo_categories(products):
    """Démo par catégories"""
    print("\n" + "="*80)
    print("📂 DÉMONSTRATION - CATÉGORIES")
    print("="*80)
    
    by_cat = {}
    for p in products:
        cat = p.get('category', 'Autre')
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(p)
    
    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        print(f"\n📂 {cat}: {len(items)} produits")
        for i, p in enumerate(items[:3], 1):
            print(f"   {i}. {p.get('name', 'Sans nom')[:60]}")
        if len(items) > 3:
            print(f"   ... et {len(items)-3} autres")

def demo_tags(products):
    """Démo filtrage par tags"""
    print("\n" + "="*80)
    print("🏷️  DÉMONSTRATION - TAGS")
    print("="*80)
    
    all_tags = []
    for p in products:
        all_tags.extend(p.get('tags', []))
    
    tag_counts = Counter(all_tags)
    
    print(f"\n📊 Top 10 tags les plus fréquents:")
    for tag, count in tag_counts.most_common(10):
        print(f"   • {tag}: {count}×")
    
    # Filtrage exemple
    print(f"\n🏷️  Exemple: Produits 'Végétarien'")
    vege = [p for p in products if 'Végétarien' in p.get('tags', [])]
    for i, p in enumerate(vege[:5], 1):
        print(f"   {i}. {p.get('name', 'Sans nom')[:60]}")
    if len(vege) > 5:
        print(f"   ... et {len(vege)-5} autres")

def demo_stats(products):
    """Démo statistiques"""
    print("\n" + "="*80)
    print("📊 DÉMONSTRATION - STATISTIQUES")
    print("="*80)
    
    print(f"\n📦 Total produits: {len(products)}")
    
    # Par catégorie
    by_cat = {}
    for p in products:
        cat = p.get('category', 'Autre')
        by_cat[cat] = by_cat.get(cat, 0) + 1
    
    print(f"\n📂 Répartition par catégorie:")
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = (count / len(products) * 100) if products else 0
        bar = "█" * int(pct / 5)
        print(f"   • {cat:20} {count:3} produits  {bar} {pct:.1f}%")
    
    # Tags
    all_tags = []
    for p in products:
        all_tags.extend(p.get('tags', []))
    
    print(f"\n🏷️  Total tags uniques: {len(set(all_tags))}")
    print(f"   Moyenne de tags par produit: {len(all_tags)/len(products):.1f}")

def demo_produit_detail(products):
    """Démo détail d'un produit"""
    print("\n" + "="*80)
    print("📦 DÉMONSTRATION - DÉTAIL PRODUIT")
    print("="*80)
    
    if not products:
        return
    
    # Prendre un produit intéressant
    product = next((p for p in products if 'poulet' in p.get('name', '').lower()), products[0])
    
    print(f"\n╔══════════════════════════════════════════════════════════════════════╗")
    print(f"║  {product.get('name', 'Sans nom')[:68]:68}  ║")
    print(f"╚══════════════════════════════════════════════════════════════════════╝")
    
    print(f"\n🆔 ID: {product.get('id')}")
    print(f"📂 Catégorie: {product.get('category', '?')}")
    print(f"💰 Prix: {format_price(product)}")
    
    if product.get('description'):
        print(f"\n📝 Description:")
        desc = product['description']
        # Wrap text
        words = desc.split()
        line = "   "
        for word in words:
            if len(line) + len(word) + 1 > 75:
                print(line)
                line = "   " + word
            else:
                line += " " + word if line != "   " else word
        if line != "   ":
            print(line)
    
    if product.get('tags'):
        print(f"\n🏷️  Tags: {', '.join(product['tags'][:8])}")
        if len(product['tags']) > 8:
            print(f"   ... et {len(product['tags'])-8} autres")
    
    if product.get('image'):
        print(f"\n🖼️  Image disponible: {product['image'][:60]}...")

def main():
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║          🍽️  FOODLES - DÉMONSTRATION OFFLINE                          ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    
    print("\n💡 Cette démo utilise les données déjà capturées")
    print("   Pas besoin d'authentification ou de connexion!\n")
    
    # Charger les produits
    products = load_products()
    
    if not products:
        print("❌ Aucune donnée disponible!")
        print("💡 Exécutez d'abord: python foodles_complete.py (avec cookies valides)")
        return
    
    print(f"✅ {len(products)} produits chargés\n")
    
    # Démonstrations
    demo_stats(products)
    demo_categories(products)
    demo_recherche(products)
    demo_tags(products)
    demo_produit_detail(products)
    
    print("\n" + "="*80)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("="*80)
    
    print(f"""
💡 UTILISATION INTERACTIVE:

   Pour explorer les données de manière interactive:
   
   1. En Python:
      from demo_offline import load_products
      products = load_products()
      
      # Recherche
      results = [p for p in products if 'poulet' in p['name'].lower()]
      
      # Par catégorie
      plats = [p for p in products if p.get('category') == 'Plats']
   
   2. Fichiers JSON disponibles:
      • foodles_products.json  - Tous les produits
      • fridge_raw_data.json   - Données brutes
      • foodles_stats.json     - Statistiques

📚 DOCUMENTATION:
   Voir RECAP_FINAL.md pour plus d'informations
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur: {e}")
        import traceback
        traceback.print_exc()
