#!/usr/bin/env python3
"""
Client Foodles API COMPLET avec toutes les fonctionnalités.
Version finale intégrant parsing, recherche, et automatisation.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from foodles_real_api import FoodlesRealAPI


class FoodlesClient:
    """Client Foodles avec fonctionnalités complètes"""
    
    def __init__(self, session_id: str = None, csrf_token: str = None):
        """
        Initialise le client
        
        Args:
            session_id: Cookie de session
            csrf_token: Token CSRF
        """
        self.api = FoodlesRealAPI(session_id, csrf_token)
        self._fridge_data = None
        self._products = None
    
    # ==================== PRODUITS ====================
    
    def get_all_products(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère tous les produits du frigo
        
        Args:
            force_refresh: Forcer le rechargement
            
        Returns:
            Liste des produits
        """
        if self._products and not force_refresh:
            return self._products
        
        # Récupérer les données du frigo
        fridge_data = self.api.get_fridge()
        self._fridge_data = fridge_data
        
        # Extraire les produits
        products = []
        if 'categories' in fridge_data:
            for category in fridge_data['categories']:
                cat_name = category.get('name', 'Autre')
                for product in category.get('products', []):
                    product['category'] = cat_name
                    products.append(product)
        
        self._products = products
        return products
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """
        Recherche des produits
        
        Args:
            query: Terme de recherche
            
        Returns:
            Produits correspondants
        """
        products = self.get_all_products()
        query = query.lower()
        
        results = []
        for product in products:
            name = str(product.get('name', '')).lower()
            desc = str(product.get('description', '')).lower()
            
            if query in name or query in desc:
                results.append(product)
        
        return results
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un produit par ID"""
        products = self.get_all_products()
        for product in products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Récupère les produits d'une catégorie"""
        products = self.get_all_products()
        category = category.lower()
        
        return [
            p for p in products
            if category in str(p.get('category', '')).lower()
        ]
    
    def get_products_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Récupère les produits avec un tag spécifique"""
        products = self.get_all_products()
        tag = tag.lower()
        
        results = []
        for product in products:
            tags = product.get('tags', [])
            for t in tags:
                if tag in str(t.get('name', '')).lower():
                    results.append(product)
                    break
        
        return results
    
    # ==================== STATS ET ANALYSE ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Génère des statistiques sur le frigo
        
        Returns:
            Dict avec les stats
        """
        products = self.get_all_products()
        
        # Catégories
        categories = {}
        for p in products:
            cat = p.get('category', 'Autre')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Tags
        tags = {}
        for p in products:
            for t in p.get('tags', []):
                tag_name = t.get('name', 'Inconnu')
                tags[tag_name] = tags.get(tag_name, 0) + 1
        
        # Prix
        prices = [p.get('price') for p in products if p.get('price')]
        price_stats = {}
        if prices:
            # Gérer les prix dict ou float
            numeric_prices = []
            for price in prices:
                if isinstance(price, dict):
                    numeric_prices.append(price.get('value', 0))
                else:
                    numeric_prices.append(price)
            
            price_stats = {
                'min': min(numeric_prices),
                'max': max(numeric_prices),
                'average': sum(numeric_prices) / len(numeric_prices)
            }
        
        return {
            'total_products': len(products),
            'categories': categories,
            'tags': tags,
            'prices': price_stats
        }
    
    def print_products(self, products: List[Dict[str, Any]], limit: int = 10):
        """
        Affiche une liste de produits de manière formatée
        
        Args:
            products: Liste des produits
            limit: Nombre max à afficher
        """
        for i, product in enumerate(products[:limit], 1):
            name = product.get('name', 'Sans nom')
            price = product.get('price', '?')
            if isinstance(price, dict):
                price = price.get('value', '?')
            category = product.get('category', 'Autre')
            
            print(f"\n{i}. {name}")
            print(f"   💰 Prix: {price}€")
            print(f"   📂 Catégorie: {category}")
            print(f"   🆔 ID: {product.get('id')}")
            
            # Tags
            tags = [t.get('name') for t in product.get('tags', [])]
            if tags:
                print(f"   🏷️  Tags: {', '.join(tags[:5])}")
        
        if len(products) > limit:
            print(f"\n   ... et {len(products) - limit} autres produits")
    
    # ==================== EXPORT ====================
    
    def export_products(self, filename: str = "foodles_products.json"):
        """
        Exporte tous les produits dans un fichier JSON
        
        Args:
            filename: Nom du fichier de sortie
        """
        products = self.get_all_products()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        return filename
    
    def export_stats(self, filename: str = "foodles_stats.json"):
        """
        Exporte les statistiques
        
        Args:
            filename: Nom du fichier
        """
        stats = self.get_statistics()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        return filename


# ==================== EXEMPLES D'UTILISATION ====================

def main():
    """Démonstration complète"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🍽️  CLIENT FOODLES COMPLET - DÉMONSTRATION                       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Initialiser
    client = FoodlesClient(
        session_id="jflffcai4qqen1dqvmznt4gxfzu2nb14",
        csrf_token="hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    )
    
    # 1. Récupérer tous les produits
    print("1️⃣  RÉCUPÉRATION DES PRODUITS")
    print("=" * 80)
    
    products = client.get_all_products()
    print(f"   ✅ {len(products)} produits récupérés\n")
    
    # 2. Statistiques
    print("2️⃣  STATISTIQUES")
    print("=" * 80)
    
    stats = client.get_statistics()
    print(f"\n   📊 Total produits: {stats['total_products']}")
    
    print(f"\n   📂 Catégories:")
    for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
        print(f"      • {cat}: {count} produits")
    
    if stats['prices']:
        print(f"\n   💰 Prix:")
        print(f"      • Min: {stats['prices']['min']}€")
        print(f"      • Max: {stats['prices']['max']}€")
        print(f"      • Moyen: {stats['prices']['average']:.2f}€")
    
    print(f"\n   🏷️  Tags les plus fréquents:")
    top_tags = sorted(stats['tags'].items(), key=lambda x: x[1], reverse=True)[:10]
    for tag, count in top_tags:
        print(f"      • {tag}: {count}x")
    
    # 3. Recherche
    print(f"\n\n3️⃣  RECHERCHE DE PRODUITS")
    print("=" * 80)
    
    search_terms = ['poulet', 'salade', 'dessert']
    for term in search_terms:
        results = client.search_products(term)
        print(f"\n   🔍 '{term}': {len(results)} résultat(s)")
        if results:
            for p in results[:3]:
                print(f"      • {p.get('name')}")
    
    # 4. Filtres par catégorie
    print(f"\n\n4️⃣  PRODUITS PAR CATÉGORIE")
    print("=" * 80)
    
    for category in ['Plats', 'Desserts', 'Boissons']:
        prods = client.get_products_by_category(category)
        print(f"\n   📂 {category}: {len(prods)} produits")
        client.print_products(prods, limit=3)
    
    # 5. Export
    print(f"\n\n5️⃣  EXPORT DES DONNÉES")
    print("=" * 80)
    
    products_file = client.export_products()
    stats_file = client.export_stats()
    
    print(f"\n   ✅ Produits exportés: {products_file}")
    print(f"   ✅ Stats exportées: {stats_file}")
    
    print("\n" + "=" * 80)
    print("✅ Démonstration terminée!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
