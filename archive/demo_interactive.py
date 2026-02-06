#!/usr/bin/env python3
"""
Démonstration interactive complète de toutes les fonctionnalités du projet Foodles.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import time
import json
from demo_offline import load_products

def print_header(title, subtitle=""):
    """Affiche un en-tête stylisé"""
    print("\n" + "="*80)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("="*80 + "\n")

def pause(message="Appuyez sur ENTRÉE pour continuer..."):
    """Pause interactive"""
    input(f"\n💡 {message}")

def demo_introduction():
    """Introduction de la démo"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🍽️  FOODLES - DÉMONSTRATION INTERACTIVE COMPLÈTE".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("📋 CETTE DÉMO VA VOUS MONTRER:\n")
    print("   1️⃣  Analyse et statistiques des produits")
    print("   2️⃣  Recherche et filtrage avancés")
    print("   3️⃣  Détails complets d'un produit")
    print("   4️⃣  Exploration par catégories")
    print("   5️⃣  Analyse des tags")
    print("   6️⃣  Export et sauvegarde des données")
    print("   7️⃣  Utilisation en Python (code)")
    
    pause()

def demo_chargement():
    """Démo du chargement"""
    print_header("1️⃣  CHARGEMENT DES DONNÉES", "Lecture des fichiers JSON capturés")
    
    print("📦 Chargement en cours", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    
    products = load_products()
    print(f" ✅\n")
    
    print(f"✅ {len(products)} produits chargés avec succès!")
    print(f"📁 Source: foodles_products.json")
    print(f"💾 Données capturées depuis l'API Foodles réelle")
    
    return products

def demo_statistiques(products):
    """Démo des statistiques"""
    print_header("2️⃣  STATISTIQUES GLOBALES", "Vue d'ensemble des données")
    
    # Comptage par catégorie
    by_cat = {}
    for p in products:
        cat = p.get('category', 'Autre')
        by_cat[cat] = by_cat.get(cat, 0) + 1
    
    print(f"📊 RÉPARTITION PAR CATÉGORIE:\n")
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = (count / len(products) * 100)
        bar = "█" * int(pct / 5)
        print(f"   {cat:15} {count:3} produits  {bar} {pct:.1f}%")
    
    # Tags
    all_tags = []
    for p in products:
        all_tags.extend(p.get('tags', []))
    
    unique_tags = len(set(all_tags))
    avg_tags = len(all_tags) / len(products) if products else 0
    
    print(f"\n🏷️  ANALYSE DES TAGS:\n")
    print(f"   • Total de tags uniques: {unique_tags}")
    print(f"   • Moyenne par produit: {avg_tags:.1f} tags")
    print(f"   • Total d'associations: {len(all_tags)}")
    
    pause()

def demo_recherche(products):
    """Démo de recherche"""
    print_header("3️⃣  RECHERCHE DE PRODUITS", "Recherche full-text dans noms et descriptions")
    
    queries = [
        ("poulet", "Recherchons tous les plats avec du poulet"),
        ("compote", "Recherchons les compotes"),
        ("lait", "Recherchons les produits laitiers")
    ]
    
    for query, description in queries:
        print(f"🔍 {description}...\n")
        print(f"   Requête: '{query}'")
        
        results = [p for p in products 
                  if query.lower() in p.get('name', '').lower() or 
                     query.lower() in (p.get('description') or '').lower()]
        
        print(f"   Résultats: {len(results)} produit(s) trouvé(s)\n")
        
        for i, p in enumerate(results[:3], 1):
            name = p.get('name', 'Sans nom')
            cat = p.get('category', '?')
            print(f"   {i}. {name[:55]}")
            print(f"      📂 {cat} | 🆔 ID: {p.get('id')}")
        
        if len(results) > 3:
            print(f"      ... et {len(results)-3} autre(s)\n")
        else:
            print()
        
        time.sleep(1)
    
    pause()

def demo_categorie(products):
    """Démo par catégorie"""
    print_header("4️⃣  EXPLORATION PAR CATÉGORIE", "Affichage des produits d'une catégorie")
    
    # Grouper par catégorie
    by_cat = {}
    for p in products:
        cat = p.get('category', 'Autre')
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(p)
    
    # Prendre la catégorie avec le plus de produits
    main_cat = max(by_cat.items(), key=lambda x: len(x[1]))
    cat_name, cat_products = main_cat
    
    print(f"📂 Catégorie: {cat_name}")
    print(f"   {len(cat_products)} produits disponibles\n")
    
    print("📋 LISTE DES PRODUITS:\n")
    
    for i, p in enumerate(cat_products[:8], 1):
        name = p.get('name', 'Sans nom')
        tags = p.get('tags', [])[:3]
        
        print(f"   {i:2}. {name[:50]}")
        if tags:
            print(f"       🏷️  {', '.join(tags)}")
    
    if len(cat_products) > 8:
        print(f"\n   ... et {len(cat_products)-8} autres produits")
    
    pause()

def demo_tags(products):
    """Démo des tags"""
    print_header("5️⃣  FILTRAGE PAR TAGS", "Sélection de produits par caractéristiques")
    
    # Compter tous les tags
    from collections import Counter
    all_tags = []
    for p in products:
        all_tags.extend(p.get('tags', []))
    
    tag_counts = Counter(all_tags)
    
    print("🏷️  TOP 10 DES TAGS LES PLUS FRÉQUENTS:\n")
    
    for i, (tag, count) in enumerate(tag_counts.most_common(10), 1):
        bar = "█" * min(30, count)
        print(f"   {i:2}. {tag:30} {count:3}× {bar}")
    
    print("\n\n💡 EXEMPLE: Filtrer les produits végétariens\n")
    
    vege = [p for p in products if 'Végétarien' in p.get('tags', [])]
    
    if vege:
        print(f"   ✅ {len(vege)} produit(s) végétarien(s) trouvé(s):\n")
        for i, p in enumerate(vege[:5], 1):
            print(f"   {i}. {p.get('name', 'Sans nom')[:60]}")
        
        if len(vege) > 5:
            print(f"   ... et {len(vege)-5} autre(s)")
    
    pause()

def demo_detail(products):
    """Démo détail produit"""
    print_header("6️⃣  DÉTAILS D'UN PRODUIT", "Affichage complet des informations")
    
    # Trouver un produit intéressant
    product = next((p for p in products if len(p.get('tags', [])) > 3), products[0])
    
    print("╔" + "="*78 + "╗")
    name = product.get('name', 'Sans nom')[:76]
    print("║  " + name.ljust(76) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print(f"🆔 ID: {product.get('id')}")
    print(f"📂 Catégorie: {product.get('category', 'Non spécifiée')}")
    
    # Prix
    price = product.get('price', 0)
    if isinstance(price, dict):
        price = price.get('value', 0)
    if price > 0:
        print(f"💰 Prix: {price:.2f}€")
    else:
        print(f"💰 Prix: Non disponible (hors heures d'ouverture)")
    
    # Description
    desc = product.get('description')
    if desc:
        print(f"\n📝 Description:")
        # Wrap text
        words = desc.split()
        line = "   "
        for word in words:
            if len(line) + len(word) + 1 > 75:
                print(line)
                line = "   " + word
            else:
                line += (" " + word) if line != "   " else word
        if line != "   ":
            print(line)
    
    # Tags
    tags = product.get('tags', [])
    if tags:
        print(f"\n🏷️  Tags ({len(tags)}):")
        print(f"   {', '.join(tags[:10])}")
        if len(tags) > 10:
            print(f"   ... et {len(tags)-10} autre(s)")
    
    # Image
    if product.get('image'):
        print(f"\n🖼️  Image: Disponible")
        print(f"   URL: {product['image'][:60]}...")
    
    pause()

def demo_export():
    """Démo export"""
    print_header("7️⃣  EXPORT ET SAUVEGARDE", "Génération de fichiers JSON")
    
    print("💾 FICHIERS DISPONIBLES:\n")
    
    files = [
        ("foodles_products.json", "Tous les produits (structure complète)", "83 KB"),
        ("foodles_stats.json", "Statistiques agrégées", "1.1 KB"),
        ("fridge_raw_data.json", "Données brutes de l'API", "67 KB"),
        ("manual_capture/api_calls_*.json", "Captures d'API complètes", "~30 KB")
    ]
    
    for filename, description, size in files:
        print(f"   📄 {filename}")
        print(f"      {description}")
        print(f"      Taille: {size}\n")
    
    print("✨ CES FICHIERS PEUVENT ÊTRE:\n")
    print("   • Importés dans d'autres applications")
    print("   • Analysés avec des outils de data science (pandas, etc.)")
    print("   • Utilisés pour créer des visualisations")
    print("   • Partagés ou archivés")
    
    pause()

def demo_code():
    """Démo utilisation en code Python"""
    print_header("8️⃣  UTILISATION EN PYTHON", "Exemples de code pour développeurs")
    
    print("💻 EXEMPLE 1: Charger et filtrer les produits\n")
    print("```python")
    print("from demo_offline import load_products")
    print("")
    print("# Charger tous les produits")
    print("products = load_products()")
    print("")
    print("# Recherche")
    print("poulets = [p for p in products")
    print("           if 'poulet' in p['name'].lower()]")
    print("")
    print("# Filtre par catégorie")
    print("desserts = [p for p in products")
    print("            if p.get('category') == 'Desserts']")
    print("```\n")
    
    pause("Appuyez sur ENTRÉE pour voir l'exemple 2...")
    
    print("\n💻 EXEMPLE 2: Statistiques avec pandas\n")
    print("```python")
    print("import pandas as pd")
    print("from demo_offline import load_products")
    print("")
    print("# Créer un DataFrame")
    print("products = load_products()")
    print("df = pd.DataFrame(products)")
    print("")
    print("# Analyse")
    print("df.groupby('category').size()")
    print("df['name'].str.contains('poulet').sum()")
    print("```\n")
    
    pause("Appuyez sur ENTRÉE pour voir l'exemple 3...")
    
    print("\n💻 EXEMPLE 3: Utiliser le client API (avec cookies valides)\n")
    print("```python")
    print("from foodles_complete import FoodlesClient")
    print("")
    print("# Initialiser le client")
    print("client = FoodlesClient()")
    print("")
    print("# Récupérer les produits en temps réel")
    print("products = client.get_all_products()")
    print("")
    print("# Rechercher")
    print("results = client.search_products('poulet')")
    print("")
    print("# Statistiques")
    print("stats = client.get_statistics()")
    print("")
    print("# Export")
    print("client.export_products('mes_produits.json')")
    print("```\n")
    
    pause()

def demo_conclusion(products):
    """Conclusion"""
    print_header("✅ CONCLUSION", "Récapitulatif de la démonstration")
    
    print("🎉 VOUS AVEZ DÉCOUVERT:\n")
    print(f"   ✅ {len(products)} produits Foodles analysés")
    print("   ✅ Recherche et filtrage puissants")
    print("   ✅ Statistiques détaillées")
    print("   ✅ Export JSON")
    print("   ✅ Utilisation en Python")
    
    print("\n\n🚀 PROCHAINES ÉTAPES POSSIBLES:\n")
    print("   1. Lancer le CLI interactif:")
    print("      $ python foodles_cli.py")
    print("")
    print("   2. Explorer les données en Python:")
    print("      $ python")
    print("      >>> from demo_offline import load_products")
    print("      >>> products = load_products()")
    print("")
    print("   3. Utiliser le client API (si cookies valides):")
    print("      $ python foodles_complete.py")
    print("")
    print("   4. Consulter la documentation:")
    print("      $ cat RECAP_FINAL.md")
    
    print("\n\n📚 FICHIERS CRÉÉS PENDANT CETTE SESSION:\n")
    print("   • ~2500 lignes de code Python")
    print("   • 15+ scripts différents")
    print("   • 8 fichiers de documentation")
    print("   • Données JSON complètes")
    
    print("\n\n" + "="*80)
    print("  🎊 DÉMONSTRATION TERMINÉE - Merci !  ".center(80))
    print("="*80 + "\n")

def main():
    """Fonction principale"""
    try:
        demo_introduction()
        products = demo_chargement()
        
        if not products:
            print("❌ Pas de données disponibles pour la démo")
            return
        
        demo_statistiques(products)
        demo_recherche(products)
        demo_categorie(products)
        demo_tags(products)
        demo_detail(products)
        demo_export()
        demo_code()
        demo_conclusion(products)
        
    except KeyboardInterrupt:
        print("\n\n❌ Démo interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n💥 Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
