#!/usr/bin/env python3
"""
Scan le code JavaScript de Foodles pour trouver les vraies APIs cachées.
"""

import re
import requests
from config import FoodlesConfig

def fetch_and_analyze_js():
    """Télécharge et analyse les fichiers JS de Foodles"""
    
    config = FoodlesConfig()
    config.set_credentials(
        "jflffcai4qqen1dqvmznt4gxfzu2nb14",
        "hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
    )
    
    print("\n╔════════════════════════════════════════════════════════════════════════╗")
    print("║     🔍 RECHERCHE DES APIs CACHÉES DANS LE CODE JAVASCRIPT           ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Headers et cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://app.foodles.co/',
    }
    
    cookies = {
        'sessionid': config.session_id,
        'csrftoken': config.csrf_token,
        'isloggedin': '1'
    }
    
    # Charger la page d'accueil pour trouver les fichiers JS
    print("1️⃣  Chargement de la page Foodles...")
    response = requests.get(
        "https://app.foodles.co/canteen/fridge",
        headers=headers,
        cookies=cookies
    )
    
    html = response.text
    print(f"   ✅ Page chargée ({len(html)} caractères)")
    
    # Extraire tous les liens vers les fichiers JS
    js_files = re.findall(r'/_next/static/chunks/[^"\']+\.js', html)
    print(f"\n2️⃣  Fichiers JavaScript trouvés: {len(js_files)}")
    
    # Patterns à rechercher dans le code JS
    api_patterns = [
        # Endpoints API classiques
        r'/api/[a-zA-Z0-9/_-]+',
        # GraphQL
        r'graphql["\']?\s*:\s*["\'][^"\']+',
        # Fetch/axios avec URLs
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.[a-z]+\(["\']([^"\']+)["\']',
        # Routes Next.js
        r'router\.push\(["\']([^"\']+)["\']',
        # Mutations/Actions
        r'action["\']?\s*:\s*["\']([^"\']+)',
        r'mutation["\']?\s*:\s*["\']([^"\']+)',
        # Endpoints dans des objets config
        r'endpoint[s]?["\']?\s*:\s*["\']([^"\']+)',
        r'url["\']?\s*:\s*["\']([^"\']+)',
        # API routes
        r'\/canteen\/[a-zA-Z0-9/_-]+',
        r'\/cart\/[a-zA-Z0-9/_-]+',
        r'\/order\/[a-zA-Z0-9/_-]+',
        r'\/product\/[a-zA-Z0-9/_-]+',
    ]
    
    all_endpoints = set()
    
    # Analyser les fichiers JS les plus prometteurs
    priority_files = [
        f for f in js_files 
        if any(keyword in f for keyword in ['app', 'page', 'canteen', 'cart', 'order', 'product'])
    ]
    
    # Si pas de fichiers prioritaires, prendre les 10 premiers
    if not priority_files:
        priority_files = js_files[:10]
    
    print(f"   Analyse de {len(priority_files)} fichiers prioritaires...\n")
    
    for i, js_file in enumerate(priority_files, 1):
        url = f"https://app.foodles.co{js_file}"
        print(f"   [{i}/{len(priority_files)}] {js_file[:60]}...")
        
        try:
            js_response = requests.get(url, timeout=10)
            js_code = js_response.text
            
            # Chercher tous les patterns
            for pattern in api_patterns:
                matches = re.findall(pattern, js_code, re.IGNORECASE)
                for match in matches:
                    # Nettoyer et valider
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    
                    match = match.strip()
                    
                    # Filtrer les résultats pertinents
                    if match and (
                        match.startswith('/api/') or
                        match.startswith('/canteen') or
                        match.startswith('/cart') or
                        match.startswith('/order') or
                        match.startswith('/product') or
                        'foodles' in match.lower()
                    ):
                        all_endpoints.add(match)
        
        except Exception as e:
            print(f"      ⚠️  Erreur: {e}")
    
    print(f"\n3️⃣  RÉSULTATS DE L'ANALYSE:")
    print("=" * 80)
    
    if all_endpoints:
        print(f"\n✅ {len(all_endpoints)} endpoints potentiels trouvés:\n")
        
        # Grouper par catégorie
        categories = {
            'API': [],
            'Canteen': [],
            'Cart': [],
            'Order': [],
            'Product': [],
            'Other': []
        }
        
        for endpoint in sorted(all_endpoints):
            if '/api/' in endpoint:
                categories['API'].append(endpoint)
            elif '/canteen' in endpoint:
                categories['Canteen'].append(endpoint)
            elif '/cart' in endpoint:
                categories['Cart'].append(endpoint)
            elif '/order' in endpoint:
                categories['Order'].append(endpoint)
            elif '/product' in endpoint:
                categories['Product'].append(endpoint)
            else:
                categories['Other'].append(endpoint)
        
        for category, endpoints in categories.items():
            if endpoints:
                print(f"\n📂 {category}:")
                for endpoint in endpoints[:15]:  # Limiter à 15 par catégorie
                    print(f"   • {endpoint}")
                if len(endpoints) > 15:
                    print(f"   ... et {len(endpoints) - 15} autres")
    
    else:
        print("\n❌ Aucun endpoint trouvé dans le code JavaScript")
        print("\nℹ️  Cela confirme que Foodles utilise exclusivement:")
        print("   • Server-Side Rendering (Next.js)")
        print("   • React Server Components")
        print("   • Aucune API REST client-side classique")
    
    # Rechercher des informations sur les actions
    print(f"\n\n4️⃣  RECHERCHE D'ACTIONS/MUTATIONS:")
    print("=" * 80)
    
    action_patterns = [
        r'(addToCart|add_to_cart|ADD_TO_CART)',
        r'(removeFromCart|remove_from_cart|REMOVE_FROM_CART)',
        r'(checkout|placeOrder|place_order|ORDER)',
        r'(updateCart|update_cart|UPDATE_CART)',
    ]
    
    print("\nAnalyse des actions dans le code...\n")
    
    # Chercher dans le HTML initial aussi
    for pattern in action_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"   ✅ Action trouvée: {pattern} ({len(matches)} occurrences)")
    
    print(f"\n\n💡 RECOMMANDATION FINALE:")
    print("=" * 80)
    print("""
Foodles utilise une architecture moderne qui rend difficile l'accès aux APIs:

✅ CE QUI FONCTIONNE:
   • Récupération des pages HTML/RSC
   • Parsing du format RSC avec notre parser
   • Navigation via cookies d'authentification

❌ CE QUI EST BLOQUÉ:
   • Ajout au panier via API REST
   • Commande via API REST
   • Accès direct aux données produits via API

🎯 SOLUTIONS POSSIBLES:

1. AUTOMATISATION BROWSER (Recommandé pour les actions)
   • Utiliser Playwright pour automatiser des actions réelles
   • Simuler des clics pour ajouter au panier
   • Capturer les requêtes déclenchées en temps réel

2. REVERSE ENGINEERING AVANCÉ
   • Analyser le code RSC plus en profondeur
   • Chercher les "Server Actions" de Next.js 13+
   • Ces actions sont des fonctions côté serveur appelées depuis le client

3. INSPECTION MANUELLE
   • Ouvrir les DevTools pendant une vraie session
   • Ajouter un produit au panier manuellement
   • Observer EXACTEMENT quelle requête est envoyée
   • Répliquer cette requête dans notre code

Voulez-vous que je crée un script Playwright pour automatiser
les actions (clic, ajout panier) avec capture en temps réel ?
    """)


if __name__ == "__main__":
    fetch_and_analyze_js()
