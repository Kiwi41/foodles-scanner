# 🕵️ Guide d'utilisation de l'intercepteur réseau

## 📋 Prérequis

```bash
# Playwright est déjà installé
# Les navigateurs sont téléchargés
```

## 🚀 Lancement de l'intercepteur

### Option 1: Mode automatique (sans login manuel)

```bash
python network_interceptor.py
```

Le script va:
1. Ouvrir un navigateur Chrome visible
2. Naviguer vers app.foodles.co
3. **Vous devez vous connecter manuellement**
4. Le script capturera automatiquement toutes les requêtes réseau
5. Visiter plusieurs pages (frigo, cantine, compte, etc.)
6. Sauvegarder tous les résultats

### Option 2: Mode headless (arrière-plan)

Modifiez dans [network_interceptor.py](network_interceptor.py) ligne 95:
```python
browser = p.chromium.launch(headless=True)  # True pour invisible
```

## 📊 Ce qui sera capturé

### Requêtes réseau
- **Toutes les URLs** visitées
- **Méthodes HTTP** (GET, POST, PUT, DELETE)
- **Headers** de requête
- **Données POST** (si applicable)

### Réponses API
- **Status codes** (200, 404, etc.)
- **Headers** de réponse
- **Body JSON** complet pour les APIs
- **Contenu texte** pour les pages HTML

## 📁 Fichiers générés

Dans le dossier `network_capture/`:

```
network_capture/
├── requests_20260130_HHMMSS.json     # Toutes les requêtes
├── responses_20260130_HHMMSS.json    # Toutes les réponses
├── api_calls_20260130_HHMMSS.json    # Uniquement les appels API
└── report_20260130_HHMMSS.json       # Rapport résumé
```

## 🔍 Analyse des résultats

### Trouver les endpoints API

```bash
# Lire le rapport
cat network_capture/report_*.json | jq '.unique_endpoints'

# Chercher des endpoints spécifiques
grep -i "api.*product" network_capture/api_calls_*.json

# Voir les réponses JSON
cat network_capture/responses_*.json | jq '.[].body' | head -50
```

### En Python

```python
import json

# Charger le rapport
with open('network_capture/report_TIMESTAMP.json') as f:
    report = json.load(f)

print(f"Endpoints trouvés: {len(report['unique_endpoints'])}")
for endpoint in report['unique_endpoints']:
    print(f"  - {endpoint}")

# Charger les réponses
with open('network_capture/responses_TIMESTAMP.json') as f:
    responses = json.load(f)

# Filtrer les réponses avec des données JSON
json_responses = [r for r in responses if isinstance(r.get('body'), dict)]
print(f"\nRéponses JSON: {len(json_responses)}")
```

## 🎯 Stratégies de capture

### 1. Capture passive (recommandé pour débuter)
- Laisser le navigateur ouvert
- Se connecter manuellement
- Naviguer normalement sur le site
- Le script capture tout

### 2. Capture interactive
- Cliquer sur les produits
- Ajouter au panier
- Passer une commande (test)
- Toutes les requêtes API seront capturées

### 3. Capture ciblée
Modifiez `pages_to_visit` dans le script:
```python
pages_to_visit = [
    ('Frigo', '/canteen/fridge'),
    ('Menu du jour', '/canteen/menu'),
    ('Historique commandes', '/account/orders'),
    # Ajoutez vos pages
]
```

## 🔧 Personnalisation

### Ajouter des interactions

Dans [network_interceptor.py](network_interceptor.py), ajoutez après la ligne 144:

```python
# Cliquer sur un produit spécifique
page.click('text=Coca-Cola')
page.wait_for_timeout(2000)

# Ajouter au panier
page.click('button:has-text("Ajouter")')
page.wait_for_timeout(2000)

# Scroll infini
for i in range(5):
    page.evaluate('window.scrollBy(0, 500)')
    page.wait_for_timeout(1000)
```

### Filtrer les requêtes capturées

Modifiez la condition ligne 33:

```python
# Capturer uniquement certaines URLs
if 'foodles.co' in request.url and '/api/' in request.url:
    self.api_calls.append(req_data)
```

## 🐛 Dépannage

### Le navigateur ne s'ouvre pas
```bash
# Réinstaller Chromium
/home/a154355/git/perso/foodle/.venv/bin/playwright install chromium --force
```

### Timeout errors
Augmentez les timeouts dans le script:
```python
page.goto(url, wait_until='networkidle', timeout=60000)  # 60 secondes
```

### Pas de requêtes capturées
- Vérifiez que vous êtes connecté
- Naviguez manuellement pour déclencher des requêtes
- Regardez la console du navigateur (F12)

## 💡 Astuces

### 1. Capturer uniquement les APIs produits
```python
if 'product' in request.url.lower() or 'fridge' in request.url.lower():
    print(f"🎯 PRODUIT: {request.url}")
    self.api_calls.append(req_data)
```

### 2. Sauvegarder les cookies
```python
cookies = context.cookies()
with open('foodles_cookies.json', 'w') as f:
    json.dump(cookies, f)
```

### 3. Réutiliser une session
```python
# Charger les cookies sauvegardés
with open('foodles_cookies.json') as f:
    cookies = json.load(f)
context.add_cookies(cookies)
```

## 📖 Exemples d'utilisation

### Capturer les produits du frigo
```bash
python network_interceptor.py
# Puis dans le navigateur:
# 1. Connectez-vous
# 2. Allez sur /canteen/fridge
# 3. Scrollez pour charger tous les produits
# 4. Attendez 10-15 secondes
# 5. Le script sauvegarde automatiquement
```

### Analyser les résultats
```python
import json

with open('network_capture/api_calls_*.json') as f:
    api_calls = json.load(f)

# Trouver les endpoints liés aux produits
product_endpoints = [
    call for call in api_calls 
    if 'product' in call['url'].lower()
]

print(f"Endpoints produits: {len(product_endpoints)}")
for endpoint in product_endpoints[:5]:
    print(f"  {endpoint['method']} {endpoint['url']}")
```

## 🎓 Prochaines étapes

Après avoir capturé les vraies requêtes API:

1. **Identifier les patterns d'URL**
   ```
   https://app.foodles.co/api/v1/products?canteen=2051
   https://app.foodles.co/api/cart/add
   ```

2. **Extraire les headers nécessaires**
   - Authorization
   - X-CSRF-Token
   - Content-Type

3. **Répliquer les appels dans foodles_api.py**
   ```python
   def get_products_real(self, canteen_id: int):
       url = f"{self.BASE_URL}/api/v1/products"
       params = {'canteen': canteen_id}
       return self.session.get(url, params=params).json()
   ```

4. **Tester et valider**

## ⚠️ Notes importantes

- **Respecter les CGU** de Foodles
- **Ne pas surcharger** le serveur avec trop de requêtes
- **Protéger vos tokens** (ne jamais les commit)
- **Utiliser headless=False** au début pour debugger

---

**Prêt?** Lancez `python network_interceptor.py` et découvrez les vraies API! 🚀
