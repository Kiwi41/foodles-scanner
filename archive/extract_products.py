"""
Extracteur de produits Foodles - Récupère les produits du frigo
"""
from foodles_api import FoodlesAPI
from rsc_parser import RSCParser
import json
import re
from typing import List, Dict, Any
from datetime import datetime


class ProductExtractor:
    """Extrait les produits du contenu RSC"""
    
    def __init__(self, api: FoodlesAPI):
        self.api = api
    
    def extract_products_from_fridge(self) -> List[Dict[str, Any]]:
        """
        Extrait tous les produits du frigo
        
        Returns:
            Liste des produits avec détails
        """
        print("⏳ Récupération du frigo...")
        fridge_data = self.api.get_fridge()
        
        if 'raw_content' not in fridge_data:
            print("❌ Pas de contenu RSC")
            return []
        
        content = fridge_data['raw_content']
        products = []
        
        # Méthode 1: Extraire via JSON objects
        parser = RSCParser(content)
        json_objects = parser.extract_all_json_objects()
        
        print(f"🔍 Analyse de {len(json_objects)} objets JSON...")
        
        for obj in json_objects:
            if self._is_product(obj):
                product = self._clean_product(obj)
                products.append(product)
        
        # Méthode 2: Parser le contenu brut pour trouver les produits
        print("🔍 Recherche de produits dans le contenu brut...")
        raw_products = self._extract_from_raw_content(content)
        products.extend(raw_products)
        
        # Déduplication par ID
        unique_products = {}
        for p in products:
            if 'id' in p:
                unique_products[p['id']] = p
        
        return list(unique_products.values())
    
    def _extract_from_raw_content(self, content: str) -> List[Dict[str, Any]]:
        """Extrait les produits directement du contenu brut"""
        products = []
        
        # Chercher les patterns de produits avec regex
        # Pattern: {"id":123,"name":"xxx","description":"yyy",...}
        pattern = r'\{"id":(\d+),"name":"([^"]+)"[^}]*\}'
        
        # Chercher toutes les occurrences
        lines = content.split('\n')
        for line in lines:
            # Chercher les objets qui contiennent id, name, et d'autres champs de produit
            if '"id":' in line and '"name":' in line and ('"price"' in line or '"amount"' in line or '"description"' in line):
                # Essayer d'extraire les objets JSON de cette ligne
                # Utiliser une approche plus robuste
                try:
                    # Trouver tous les objets JSON potentiels
                    depth = 0
                    start = -1
                    for i, char in enumerate(line):
                        if char == '{':
                            if depth == 0:
                                start = i
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0 and start != -1:
                                obj_str = line[start:i+1]
                                try:
                                    obj = json.loads(obj_str)
                                    if self._is_product(obj):
                                        products.append(self._clean_product(obj))
                                except:
                                    pass
                except:
                    pass
        
        return products
    
    def _is_product(self, obj: Dict) -> bool:
        """Vérifie si un objet ressemble à un produit"""
        # Critères pour identifier un produit
        has_id = 'id' in obj
        has_name = 'name' in obj
        has_price_or_amount = 'price' in obj or 'amount' in obj
        has_description = 'description' in obj
        
        # Au moins 2 critères sur 4
        score = sum([has_id, has_name, has_price_or_amount, has_description])
        return score >= 2
    
    def _clean_product(self, obj: Dict) -> Dict[str, Any]:
        """Nettoie et structure les données du produit"""
        product = {}
        
        # Champs de base
        fields = ['id', 'name', 'description', 'price', 'amount', 
                  'slug', 'category', 'quantity', 'stock', 'available',
                  'image', 'photo', 'photos']
        
        for field in fields:
            if field in obj:
                product[field] = obj[field]
        
        # Extraire les images
        if 'photos' in obj and isinstance(obj['photos'], list) and obj['photos']:
            product['image_url'] = obj['photos'][0].get('file') if isinstance(obj['photos'][0], dict) else None
        elif 'photo' in obj and isinstance(obj['photo'], dict):
            product['image_url'] = obj['photo'].get('file')
        
        return product
    
    def get_categories(self, products: List[Dict]) -> Dict[str, int]:
        """Groupe les produits par catégorie"""
        categories = {}
        for product in products:
            category = product.get('category', product.get('name', 'Autre'))
            if isinstance(category, dict):
                category = category.get('name', 'Autre')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def print_products(self, products: List[Dict], limit: int = None):
        """Affiche les produits de manière formatée"""
        print(f"\n{'='*80}")
        print(f"🛒 PRODUITS TROUVÉS: {len(products)}")
        print(f"{'='*80}")
        
        if not products:
            print("❌ Aucun produit trouvé")
            return
        
        # Grouper par catégorie si disponible
        by_category = {}
        for p in products:
            cat = p.get('category', 'Autre')
            if isinstance(cat, dict):
                cat = cat.get('name', 'Autre')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(p)
        
        # Afficher par catégorie
        displayed = 0
        for category, items in by_category.items():
            print(f"\n📦 {category.upper()} ({len(items)} produits)")
            print("-" * 80)
            
            for i, product in enumerate(items, 1):
                if limit and displayed >= limit:
                    break
                
                name = product.get('name', 'Sans nom')
                price = product.get('price', product.get('amount', 'N/A'))
                product_id = product.get('id', 'N/A')
                
                # Nettoyer le nom (enlever les caractères bizarres)
                name = self._decode_text(name)
                
                print(f"\n{i}. {name}")
                print(f"   ID: {product_id}")
                
                if price != 'N/A':
                    if isinstance(price, dict) and 'value' in price:
                        price_val = price['value']
                        print(f"   Prix: {price_val}€")
                    elif isinstance(price, (int, float)):
                        print(f"   Prix: {price}€")
                
                if 'description' in product:
                    desc = self._decode_text(product['description'])
                    desc_short = desc[:100] + '...' if len(desc) > 100 else desc
                    print(f"   Description: {desc_short}")
                
                if 'image_url' in product:
                    print(f"   Image: {product['image_url'][:60]}...")
                
                if 'quantity' in product:
                    print(f"   Quantité: {product['quantity']}")
                
                displayed += 1
        
        if limit and displayed >= limit:
            print(f"\n... {len(products) - limit} autres produits non affichés")
    
    def _decode_text(self, text: str) -> str:
        """Décode le texte avec caractères spéciaux"""
        if not isinstance(text, str):
            return str(text)
        
        # Remplacer les caractères mal encodés courants
        replacements = {
            'Ã©': 'é',
            'Ã¨': 'è',
            'Ãª': 'ê',
            'Ã«': 'ë',
            'Ã ': 'à',
            'Ã¢': 'â',
            'Ã´': 'ô',
            'Ã®': 'î',
            'Ã¯': 'ï',
            'Ã§': 'ç',
            'Ã¹': 'ù',
            'Ã»': 'û',
            'Ã¼': 'ü',
            'Ã': 'É',
            'Ã': 'À',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def save_products(self, products: List[Dict], filename: str = "products.json"):
        """Sauvegarde les produits dans un fichier JSON"""
        output = {
            'extraction_date': datetime.now().isoformat(),
            'total_products': len(products),
            'categories': self.get_categories(products),
            'products': products
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Produits sauvegardés dans: {filename}")


def main():
    """Fonction principale"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuration
    session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
    csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    
    api = FoodlesAPI(session_id, csrf_token)
    api.set_delivery_settings(2051, "Worldline Copernic", "2026-01-30")
    
    # Extraire les produits
    extractor = ProductExtractor(api)
    
    print("🚀 EXTRACTION DES PRODUITS FOODLES")
    print("=" * 80)
    
    products = extractor.extract_products_from_fridge()
    
    # Afficher les produits
    extractor.print_products(products, limit=20)
    
    # Statistiques
    print(f"\n{'='*80}")
    print("📊 STATISTIQUES")
    print(f"{'='*80}")
    categories = extractor.get_categories(products)
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} produits")
    
    # Sauvegarder
    extractor.save_products(products)
    
    print(f"\n{'='*80}")
    print("✅ Extraction terminée!")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
