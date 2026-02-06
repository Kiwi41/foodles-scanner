"""
Parser pour les réponses RSC (React Server Components) de Foodles
"""
import re
import json
from typing import Dict, List, Any, Optional


class RSCParser:
    """Parser pour le format RSC utilisé par Foodles"""
    
    def __init__(self, rsc_content: str):
        self.content = rsc_content
        self.lines = rsc_content.split('\n')
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse le contenu RSC et extrait les données structurées
        
        Returns:
            Dictionnaire avec les données parsées
        """
        result = {
            'fragments': [],
            'modules': [],
            'data': [],
            'raw_lines': []
        }
        
        for line in self.lines:
            if not line.strip():
                continue
            
            # Essayer de parser chaque ligne
            parsed_line = self._parse_line(line)
            if parsed_line:
                result['raw_lines'].append(parsed_line)
                
                # Catégoriser par type
                if parsed_line.get('type') == 'fragment':
                    result['fragments'].append(parsed_line)
                elif parsed_line.get('type') == 'module':
                    result['modules'].append(parsed_line)
                elif parsed_line.get('type') == 'data':
                    result['data'].append(parsed_line)
        
        return result
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne RSC individuelle"""
        try:
            # Format: "id:data" or "id:[data]"
            match = re.match(r'^(\w+):(.*)', line)
            if not match:
                return None
            
            line_id, content = match.groups()
            
            result = {
                'id': line_id,
                'raw': content
            }
            
            # Déterminer le type
            if content.startswith('$'):
                result['type'] = 'fragment'
                result['fragment_type'] = content
            elif content.startswith('I['):
                result['type'] = 'module'
                result['content'] = self._extract_array(content)
            elif content.startswith('[') or content.startswith('{'):
                result['type'] = 'data'
                try:
                    result['content'] = json.loads(content)
                except:
                    result['content'] = content
            else:
                result['type'] = 'unknown'
                result['content'] = content
            
            return result
        except Exception as e:
            return {'id': 'error', 'error': str(e), 'raw': line}
    
    def _extract_array(self, content: str) -> List:
        """Extrait le contenu d'un tableau dans le format RSC"""
        try:
            # Essayer de parser comme JSON
            return json.loads(content[1:])  # Skip 'I'
        except:
            return [content]
    
    def extract_products(self) -> List[Dict[str, Any]]:
        """
        Extrait les produits du contenu RSC
        
        Returns:
            Liste des produits trouvés
        """
        products = []
        
        # Chercher les patterns de produits dans le contenu
        # Les produits sont souvent dans des structures JSON
        for line in self.lines:
            # Rechercher des patterns JSON qui ressemblent à des produits
            if '"name"' in line and '"price"' in line:
                try:
                    # Extraire les objets JSON de la ligne
                    json_objects = re.findall(r'\{[^{}]*"name"[^{}]*\}', line)
                    for obj_str in json_objects:
                        try:
                            product = json.loads(obj_str)
                            if 'name' in product:
                                products.append(product)
                        except:
                            continue
                except:
                    continue
        
        return products
    
    def extract_menu_items(self) -> List[Dict[str, Any]]:
        """
        Extrait les éléments du menu
        
        Returns:
            Liste des éléments du menu
        """
        items = []
        
        # Patterns pour identifier les éléments de menu
        patterns = [
            r'"title"\s*:\s*"([^"]+)"',
            r'"description"\s*:\s*"([^"]+)"',
            r'"category"\s*:\s*"([^"]+)"'
        ]
        
        for line in self.lines:
            item = {}
            for pattern in patterns:
                matches = re.findall(pattern, line)
                if matches:
                    key = pattern.split('"')[1]
                    item[key] = matches[0]
            
            if item:
                items.append(item)
        
        return items
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé du contenu RSC
        
        Returns:
            Résumé avec statistiques
        """
        parsed = self.parse()
        
        return {
            'total_lines': len(self.lines),
            'fragments_count': len(parsed['fragments']),
            'modules_count': len(parsed['modules']),
            'data_entries': len(parsed['data']),
            'content_preview': self.content[:500] if len(self.content) > 500 else self.content
        }
    
    def search_in_content(self, keyword: str) -> List[str]:
        """
        Recherche un mot-clé dans le contenu
        
        Args:
            keyword: Mot-clé à rechercher
            
        Returns:
            Liste des lignes contenant le mot-clé
        """
        results = []
        keyword_lower = keyword.lower()
        
        for line in self.lines:
            if keyword_lower in line.lower():
                # Limiter la longueur de la ligne pour l'affichage
                if len(line) > 200:
                    line = line[:200] + '...'
                results.append(line)
        
        return results
    
    def extract_all_json_objects(self) -> List[Dict[str, Any]]:
        """
        Extrait tous les objets JSON du contenu
        
        Returns:
            Liste de tous les objets JSON trouvés
        """
        json_objects = []
        
        for line in self.lines:
            # Chercher des objets JSON complets
            matches = re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', line)
            for match in matches:
                try:
                    obj = json.loads(match.group())
                    json_objects.append(obj)
                except:
                    continue
        
        return json_objects
    
    def decode_unicode_escapes(self, text: str) -> str:
        """
        Décode les échappements Unicode dans le texte
        
        Args:
            text: Texte avec échappements Unicode
            
        Returns:
            Texte décodé
        """
        try:
            return text.encode('utf-8').decode('unicode_escape')
        except:
            return text
    
    def extract_data_by_key(self, key: str) -> List[Any]:
        """
        Extrait toutes les valeurs associées à une clé spécifique
        
        Args:
            key: La clé à rechercher
            
        Returns:
            Liste des valeurs trouvées
        """
        values = []
        pattern = f'"{key}"\\s*:\\s*([^,}}]+)'
        
        for line in self.lines:
            matches = re.finditer(pattern, line)
            for match in matches:
                value = match.group(1).strip().strip('"')
                values.append(value)
        
        return values
    
    def find_nested_structures(self) -> Dict[str, List[str]]:
        """
        Identifie les structures imbriquées dans le contenu
        
        Returns:
            Dictionnaire avec les types de structures trouvées
        """
        structures = {
            'arrays': [],
            'objects': [],
            'functions': [],
            'components': []
        }
        
        for line in self.lines:
            # Tableaux
            if '[' in line:
                array_matches = re.findall(r'\[([^\[\]]*)\]', line)
                structures['arrays'].extend(array_matches[:3])  # Limiter à 3
            
            # Composants React
            if '$' in line or 'Component' in line:
                structures['components'].append(line[:100])
        
        return structures


def parse_rsc_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction utilitaire pour parser une réponse API Foodles
    
    Args:
        response_data: Données de réponse de l'API
        
    Returns:
        Données parsées et structurées
    """
    if 'raw_content' not in response_data:
        return response_data
    
    parser = RSCParser(response_data['raw_content'])
    
    return {
        'summary': parser.get_summary(),
        'parsed_data': parser.parse(),
        'products': parser.extract_products(),
        'menu_items': parser.extract_menu_items(),
        'all_json_objects': parser.extract_all_json_objects()
    }
