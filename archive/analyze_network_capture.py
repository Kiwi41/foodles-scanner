#!/usr/bin/env python3
"""
Analyse approfondie de la capture réseau pour extraire les vraies données Foodles.
"""

import json
from pathlib import Path
import re
from datetime import datetime

def analyze_api_calls():
    """Analyse les fichiers capturés"""
    
    capture_dir = Path("network_capture")
    if not capture_dir.exists():
        print("❌ Aucun fichier de capture trouvé dans network_capture/")
        return
    
    # Trouver le fichier le plus récent
    json_files = list(capture_dir.glob("api_calls_*.json"))
    if not json_files:
        print("❌ Aucun fichier api_calls_*.json trouvé")
        return
    
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"📂 Analyse de: {latest_file.name}")
    print("=" * 80)
    
    with open(latest_file) as f:
        api_calls = json.load(f)
    
    # Catégoriser les appels
    foodles_calls = []
    third_party_calls = []
    
    for call in api_calls:
        url = call.get('url', '')
        if 'app.foodles.co' in url or 'foodles' in url.lower():
            foodles_calls.append(call)
        else:
            third_party_calls.append(call)
    
    print(f"\n📊 RÉSUMÉ DE LA CAPTURE")
    print(f"   Total appels: {len(api_calls)}")
    print(f"   • Foodles: {len(foodles_calls)}")
    print(f"   • Tiers (analytics, monitoring): {third_party_calls.__len__()}")
    
    print(f"\n🎯 APPELS FOODLES TROUVÉS:")
    print("-" * 80)
    
    unique_urls = {}
    for call in foodles_calls:
        url = call['url']
        method = call['method']
        key = f"{method} {url}"
        
        if key not in unique_urls:
            unique_urls[key] = {
                'method': method,
                'url': url,
                'count': 0,
                'has_post_data': bool(call.get('post_data')),
                'headers': call.get('headers', {})
            }
        unique_urls[key]['count'] += 1
    
    for i, (key, info) in enumerate(unique_urls.items(), 1):
        print(f"\n{i}. {info['method']} {info['url']}")
        print(f"   Appelé {info['count']} fois")
        if info['has_post_data']:
            print(f"   ⚠️  Contient des données POST")
        
        # Afficher les headers intéressants
        headers = info['headers']
        interesting_headers = ['cookie', 'authorization', 'x-csrf-token', 'content-type']
        for h in interesting_headers:
            if h in headers or h.lower() in [k.lower() for k in headers.keys()]:
                print(f"   Header: {h} présent")
    
    # Analyser les services tiers
    print(f"\n\n🔍 SERVICES TIERS DÉTECTÉS:")
    print("-" * 80)
    
    third_party_domains = {}
    for call in third_party_calls:
        url = call['url']
        # Extraire le domaine
        match = re.search(r'https?://([^/]+)', url)
        if match:
            domain = match.group(1)
            if domain not in third_party_domains:
                third_party_domains[domain] = {
                    'count': 0,
                    'endpoints': set()
                }
            third_party_domains[domain]['count'] += 1
            # Extraire le path
            path_match = re.search(r'https?://[^/]+(/[^?]*)', url)
            if path_match:
                third_party_domains[domain]['endpoints'].add(path_match.group(1))
    
    for domain, info in sorted(third_party_domains.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"\n• {domain}")
        print(f"  {info['count']} appels")
        if len(info['endpoints']) <= 5:
            for endpoint in sorted(info['endpoints']):
                print(f"    → {endpoint}")
    
    # Rechercher des données POST intéressantes
    print(f"\n\n💾 DONNÉES POST ANALYSÉES:")
    print("-" * 80)
    
    for call in foodles_calls:
        if call.get('post_data'):
            print(f"\n📤 POST {call['url']}")
            post_data = call['post_data']
            if isinstance(post_data, str):
                # Essayer de parser comme JSON
                try:
                    data = json.loads(post_data)
                    print(f"   Type: JSON")
                    print(f"   Clés: {list(data.keys())[:10]}")
                except:
                    print(f"   Type: Texte ({len(post_data)} caractères)")
                    print(f"   Début: {post_data[:200]}")
    
    print(f"\n\n💡 CONCLUSION:")
    print("=" * 80)
    print("""
Les captures réseau montrent que Foodles utilise une architecture Next.js avec:
1. Server-Side Rendering (SSR) - Les données sont dans le HTML initial
2. React Server Components (RSC) - Format propriétaire

❌ Aucune API REST classique n'a été trouvée pour:
   - Liste des produits du frigo
   - Ajout au panier
   - Commandes

🎯 SOLUTIONS POSSIBLES:

A. REVERSE ENGINEERING DU FORMAT RSC
   • Les réponses HTML contiennent les données dans un format RSC
   • Notre parser RSC peut extraire ces données
   • Mais c'est fragile et peut changer

B. INTERCEPTION DES ACTIONS CLIENT-SIDE
   • Utiliser Playwright pour simuler des clics
   • Intercepter les requêtes XHR/Fetch qui se déclenchent
   • Nécessite une connexion active

C. API BACKEND (SI ELLE EXISTE)
   • Possible que Foodles ait une API interne non documentée
   • Nécessiterait d'inspecter le code JavaScript de l'app
   • Ou d'utiliser les DevTools Network pendant l'utilisation réelle

Recommandation: Analyser le code JavaScript de l'app pour trouver
les vraies APIs utilisées pour les actions (ajouter au panier, etc.)
    """)


def analyze_responses():
    """Analyse les réponses capturées"""
    capture_dir = Path("network_capture")
    response_files = list(capture_dir.glob("responses_*.json"))
    
    if not response_files:
        print("❌ Aucun fichier de réponses trouvé")
        return
    
    latest_file = max(response_files, key=lambda p: p.stat().st_mtime)
    print(f"\n\n📥 ANALYSE DES RÉPONSES")
    print(f"   Fichier: {latest_file.name}")
    print("=" * 80)
    
    with open(latest_file) as f:
        responses = json.load(f)
    
    print(f"   Total réponses capturées: {len(responses)}")
    
    # Analyser chaque réponse
    for i, response in enumerate(responses, 1):
        url = response.get('url', '')
        status = response.get('status_code', 0)
        content_type = response.get('content_type', '')
        body = response.get('body', '')
        
        if 'foodles' in url.lower():
            print(f"\n{i}. {url}")
            print(f"   Status: {status}")
            print(f"   Content-Type: {content_type}")
            print(f"   Taille: {len(body)} caractères")
            
            if 'json' in content_type.lower():
                try:
                    data = json.loads(body)
                    print(f"   Type: JSON valide")
                    print(f"   Clés racine: {list(data.keys())[:10]}")
                except:
                    pass


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🔍 ANALYSE APPROFONDIE DE LA CAPTURE RÉSEAU FOODLES             ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    analyze_api_calls()
    analyze_responses()
    
    print("\n" + "=" * 80)
    print("✅ Analyse terminée!")
    print("=" * 80 + "\n")
