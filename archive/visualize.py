"""
Visualiseur de données Foodles - Affiche les données de manière lisible
"""
from foodles_api import FoodlesAPI
from rsc_parser import RSCParser, parse_rsc_response
import json
from collections import Counter
from typing import Dict, Any


class DataVisualizer:
    """Visualise les données extraites de l'API Foodles"""
    
    def __init__(self):
        self.data = {}
    
    def load_from_file(self, filepath: str):
        """Charge les données depuis un fichier JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def analyze_keywords(self, content: str) -> Dict[str, int]:
        """
        Analyse la fréquence des mots-clés dans le contenu
        
        Args:
            content: Contenu à analyser
            
        Returns:
            Dictionnaire {mot: fréquence}
        """
        # Liste étendue de mots-clés pertinents
        keywords = [
            # Produits
            'product', 'products', 'item', 'items', 'meal', 'meals',
            'dish', 'dishes', 'food', 'snack', 'beverage', 'drink',
            
            # Prix et stock
            'price', 'cost', 'amount', 'total', 'stock', 'available',
            'availability', 'quantity', 'qty',
            
            # Commande
            'order', 'orders', 'cart', 'basket', 'checkout', 'purchase',
            'buy', 'payment', 'transaction',
            
            # Utilisateur
            'user', 'account', 'profile', 'customer', 'client',
            
            # Cantine
            'canteen', 'fridge', 'menu', 'delivery', 'schedule',
            'location', 'address',
            
            # Métadonnées
            'name', 'title', 'description', 'category', 'type',
            'id', 'uuid', 'slug', 'url', 'image', 'photo',
            
            # Dates
            'date', 'time', 'timestamp', 'created', 'updated',
            'delivery', 'schedule'
        ]
        
        content_lower = content.lower()
        frequencies = {}
        
        for keyword in keywords:
            count = content_lower.count(keyword)
            if count > 0:
                frequencies[keyword] = count
        
        # Trier par fréquence décroissante
        return dict(sorted(frequencies.items(), key=lambda x: x[1], reverse=True))
    
    def find_interesting_patterns(self, content: str) -> Dict[str, list]:
        """
        Trouve des patterns intéressants dans le contenu
        
        Args:
            content: Contenu à analyser
            
        Returns:
            Dictionnaire de patterns trouvés
        """
        import re
        
        patterns = {
            'urls': re.findall(r'https?://[^\s"\'<>]+', content),
            'ids': re.findall(r'"id"\s*:\s*"?(\w+)"?', content),
            'prices': re.findall(r'\d+[.,]\d{2}', content),
            'emails': re.findall(r'[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}', content),
            'dates': re.findall(r'\d{4}-\d{2}-\d{2}', content),
            'components': re.findall(r'\$L\w+', content),
            'chunks': re.findall(r'static/chunks/[\w-]+\.js', content),
        }
        
        # Filtrer les listes vides et dédupliquer
        return {k: list(set(v))[:10] for k, v in patterns.items() if v}
    
    def extract_structured_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les données structurées des objets JSON
        
        Args:
            parsed_data: Données parsées du RSC
            
        Returns:
            Données structurées extraites
        """
        structured = {
            'components': [],
            'routes': [],
            'parameters': [],
            'metadata': []
        }
        
        for obj in parsed_data.get('all_json_objects', []):
            # Composants
            if 'Component' in obj:
                structured['components'].append(obj)
            
            # Routes et paramètres
            if 'params' in obj or 'searchParams' in obj:
                structured['routes'].append(obj)
            
            # Métadonnées
            if 'name' in obj or 'title' in obj or 'description' in obj:
                structured['metadata'].append(obj)
        
        return structured
    
    def print_analysis(self, endpoint_name: str, response_data: Dict[str, Any]):
        """
        Affiche une analyse complète des données
        
        Args:
            endpoint_name: Nom de l'endpoint
            response_data: Données de réponse
        """
        print("\n" + "=" * 80)
        print(f"📊 ANALYSE DÉTAILLÉE: {endpoint_name}")
        print("=" * 80)
        
        if 'raw_content' not in response_data:
            print("❌ Pas de contenu RSC à analyser")
            return
        
        content = response_data['raw_content']
        parsed = parse_rsc_response(response_data)
        
        # 1. Statistiques de base
        print("\n📈 STATISTIQUES DE BASE")
        print("-" * 80)
        print(f"Taille du contenu: {len(content)} caractères")
        print(f"Nombre de lignes: {parsed['summary']['total_lines']}")
        print(f"Fragments: {parsed['summary']['fragments_count']}")
        print(f"Modules: {parsed['summary']['modules_count']}")
        print(f"Objets JSON: {len(parsed['all_json_objects'])}")
        
        # 2. Analyse des mots-clés
        print("\n🔍 MOTS-CLÉS LES PLUS FRÉQUENTS")
        print("-" * 80)
        keywords = self.analyze_keywords(content)
        for i, (keyword, count) in enumerate(list(keywords.items())[:15], 1):
            print(f"{i:2}. {keyword:20} → {count:3} occurrences")
        
        # 3. Patterns intéressants
        print("\n🎯 PATTERNS DÉTECTÉS")
        print("-" * 80)
        patterns = self.find_interesting_patterns(content)
        for pattern_type, items in patterns.items():
            if items:
                print(f"\n{pattern_type.upper()}:")
                for item in items[:5]:
                    print(f"  - {item}")
        
        # 4. Données structurées
        print("\n📦 DONNÉES STRUCTURÉES")
        print("-" * 80)
        structured = self.extract_structured_data(parsed)
        print(f"Composants: {len(structured['components'])}")
        print(f"Routes: {len(structured['routes'])}")
        print(f"Métadonnées: {len(structured['metadata'])}")
        
        if structured['metadata']:
            print("\nMétadonnées trouvées:")
            for meta in structured['metadata'][:3]:
                print(f"  {json.dumps(meta, ensure_ascii=False)[:100]}...")
        
        # 5. Chunks JS chargés
        if 'chunks' in patterns and patterns['chunks']:
            print("\n📦 CHUNKS JAVASCRIPT")
            print("-" * 80)
            print(f"Nombre de chunks: {len(patterns['chunks'])}")
            print("Chunks principaux:")
            for chunk in patterns['chunks'][:10]:
                print(f"  - {chunk}")


def main():
    """Fonction principale"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuration
    session_id = "jflffcai4qqen1dqvmznt4gxfzu2nb14"
    csrf_token = "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    
    api = FoodlesAPI(session_id, csrf_token)
    api.set_delivery_settings(2051, "Worldline Copernic", "2026-01-30")
    
    visualizer = DataVisualizer()
    
    print("🎨 VISUALISEUR DE DONNÉES FOODLES")
    print("=" * 80)
    
    # Analyser les différents endpoints
    endpoints = [
        ("Frigo", "/canteen/fridge"),
        ("Cantine", "/canteen"),
        ("Accueil", "/"),
        ("Compte", "/account")
    ]
    
    for name, endpoint in endpoints:
        try:
            print(f"\n⏳ Récupération de {name}...")
            response = api.make_request(endpoint, params={"_rsc": "1d46b"})
            visualizer.print_analysis(name, response)
            
        except Exception as e:
            print(f"❌ Erreur pour {name}: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Analyse terminée!")
    print("=" * 80)


if __name__ == "__main__":
    main()
