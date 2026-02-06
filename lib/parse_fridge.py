#!/usr/bin/env python3
"""
Parser pour les données du frigo récupérées via /api/fridge/
Extrait les produits, prix, stocks, etc.
"""

import json
from typing import List, Dict, Any
from foodles_real_api import FoodlesRealAPI


class FridgeParser:
    """Parser pour les données du frigo Foodles"""
    
    def __init__(self, fridge_data: Dict[str, Any]):
        """
        Initialise le parser
        
        Args:
            fridge_data: Données brutes du frigo
        """
        self.data = fridge_data
        self.products = []
        self._parse()
    
    def _parse(self):
        """Parse les données du frigo"""
        # Explorer la structure
        if isinstance(self.data, dict):
            self._extract_products(self.data)
        elif isinstance(self.data, list):
            for item in self.data:
                self._extract_products(item)
    
    def _extract_products(self, obj: Any, path: str = ""):
        """
        Extrait récursivement les produits
        
        Args:
            obj: Objet à explorer
            path: Chemin actuel dans la structure
        """
        if isinstance(obj, dict):
            # Vérifier si c'est un produit
            if self._is_product(obj):
                self.products.append(obj)
            
            # Explorer récursivement
            for key, value in obj.items():
                self._extract_products(value, f"{path}.{key}" if path else key)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._extract_products(item, f"{path}[{i}]")
    
    def _is_product(self, obj: Dict) -> bool:
        """
        Vérifie si un objet est un produit
        
        Args:
            obj: Objet à vérifier
            
        Returns:
            True si c'est un produit
        """
        # Indicateurs qu'il s'agit d'un produit
        product_keys = ['name', 'price', 'id', 'title']
        
        if not isinstance(obj, dict):
            return False
        
        # Doit avoir au moins 2 indicateurs
        indicators = sum(1 for key in product_keys if key in obj)
        return indicators >= 2
    
    def get_products(self) -> List[Dict[str, Any]]:
        """
        Retourne tous les produits
        
        Returns:
            Liste des produits
        """
        return self.products
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        Recherche un produit par ID
        
        Args:
            product_id: ID du produit
            
        Returns:
            Produit trouvé ou None
        """
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Recherche des produits par nom
        
        Args:
            query: Terme de recherche
            
        Returns:
            Liste des produits correspondants
        """
        query = query.lower()
        results = []
        
        for product in self.products:
            name = str(product.get('name', '')).lower()
            title = str(product.get('title', '')).lower()
            
            if query in name or query in title:
                results.append(product)
        
        return results
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Filtre par catégorie
        
        Args:
            category: Nom de la catégorie
            
        Returns:
            Produits de cette catégorie
        """
        results = []
        category = category.lower()
        
        for product in self.products:
            product_category = str(product.get('category', '')).lower()
            if category in product_category:
                results.append(product)
        
        return results
    
    def get_available(self) -> List[Dict[str, Any]]:
        """
        Retourne les produits disponibles
        
        Returns:
            Produits en stock
        """
        results = []
        
        for product in self.products:
            # Différentes façons de vérifier la disponibilité
            available = (
                product.get('available', True) or
                product.get('in_stock', True) or
                product.get('stock', 0) > 0
            )
            
            if available:
                results.append(product)
        
        return results
    
    def print_summary(self):
        """Affiche un résumé des produits"""
        print(f"\n📊 RÉSUMÉ DU FRIGO")
        print("=" * 80)
        print(f"   Total produits: {len(self.products)}")
        
        if self.products:
            # Analyser les catégories
            categories = set()
            for p in self.products:
                cat = p.get('category') or p.get('type')
                if cat:
                    categories.add(cat)
            
            if categories:
                print(f"   Catégories: {len(categories)}")
                for cat in sorted(categories):
                    count = len(self.get_by_category(str(cat)))
                    print(f"      • {cat}: {count} produits")
            
            # Prix min/max
            prices = [p.get('price', 0) for p in self.products if 'price' in p]
            if prices:
                print(f"\n   Prix:")
                print(f"      • Min: {min(prices)}€")
                print(f"      • Max: {max(prices)}€")
                print(f"      • Moyen: {sum(prices)/len(prices):.2f}€")
            
            # Disponibilité
            available = len(self.get_available())
            print(f"\n   Disponibilité:")
            print(f"      • Disponibles: {available}")
            print(f"      • Non disponibles: {len(self.products) - available}")


def main():
    """Test du parser"""
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🥤 PARSER DE DONNÉES FRIGO                                       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Initialiser l'API
    api = FoodlesRealAPI(
        session_id="jflffcai4qqen1dqvmznt4gxfzu2nb14",
        csrf_token="hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    )
    
    print("1️⃣  Récupération des données du frigo...")
    try:
        fridge_data = api.get_fridge()
        print(f"   ✅ Données récupérées: {len(json.dumps(fridge_data))} caractères")
        
        # Sauvegarder pour analyse
        with open('fridge_raw_data.json', 'w', encoding='utf-8') as f:
            json.dump(fridge_data, f, indent=2, ensure_ascii=False)
        print(f"   💾 Sauvegardé dans: fridge_raw_data.json")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return
    
    print("\n2️⃣  Parsing des données...")
    parser = FridgeParser(fridge_data)
    products = parser.get_products()
    
    print(f"   ✅ {len(products)} produits extraits")
    
    # Afficher le résumé
    parser.print_summary()
    
    # Exemples de recherche
    print(f"\n\n3️⃣  EXEMPLES DE RECHERCHE")
    print("=" * 80)
    
    # Recherche par nom
    print("\n🔍 Recherche 'sandwich':")
    sandwiches = parser.search('sandwich')
    for p in sandwiches[:5]:
        name = p.get('name') or p.get('title', 'Sans nom')
        price = p.get('price', '?')
        print(f"   • {name} - {price}€")
    
    # Afficher quelques produits
    print(f"\n\n4️⃣  APERÇU DES PRODUITS")
    print("=" * 80)
    
    for i, product in enumerate(products[:10], 1):
        print(f"\n{i}. {product.get('name') or product.get('title', 'Produit sans nom')}")
        for key, value in list(product.items())[:8]:
            if value and not isinstance(value, (dict, list)):
                print(f"   {key}: {value}")
    
    if len(products) > 10:
        print(f"\n   ... et {len(products) - 10} autres produits")
    
    # Sauvegarder les produits parsés
    print(f"\n\n5️⃣  SAUVEGARDE")
    print("=" * 80)
    
    with open('fridge_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ {len(products)} produits sauvegardés dans: fridge_products.json")
    
    # Structure des données
    print(f"\n\n6️⃣  STRUCTURE DES DONNÉES")
    print("=" * 80)
    
    if products:
        print("\n   Champs communs trouvés:")
        all_keys = set()
        for p in products:
            all_keys.update(p.keys())
        
        for key in sorted(all_keys):
            count = sum(1 for p in products if key in p)
            percentage = (count / len(products)) * 100
            print(f"   • {key}: {count}/{len(products)} ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
