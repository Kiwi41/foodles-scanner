# 🎉 APIs Foodles Découvertes

## ✅ APIs Fonctionnelles

### 🔐 Authentification

```python
# Vérifier le type de connexion
GET https://api.foodles.co/api/auth/login-type/?email=EMAIL

# Se connecter
POST https://api.foodles.co/api/auth/login/
Body: {"email": "...", "password": "..."}
```

### 👤 Utilisateur

```python
# Informations utilisateur actuel
GET https://api.foodles.co/api/async/client/current/

# Mettre à jour l'utilisateur
PATCH https://api.foodles.co/api/client/v2/{CLIENT_ID}/
```

### 💳 Paiements

```python
# Cartes tickets restaurant
GET https://api.foodles.co/api/payments/meal-voucher-card/
```

### 🏢 Entreprises

```python
# Liste des entreprises
GET https://api.foodles.co/api/company/?page=1&ps=25
```

### 🥤 Frigo

```python
# Informations du frigo
GET https://api.foodles.co/api/fridge/
```

### 🍽️ Cantine / Menu

```python
# Menu du jour
GET https://api.foodles.co/api/ondemand/stores/{STORE_ID}/menu/?when=YYYY-MM-DD

# Panier
GET https://api.foodles.co/api/ondemand/stores/{STORE_ID}/cart/?when=YYYY-MM-DD

# Horaires d'ouverture
GET https://api.foodles.co/api/ondemand/stores/{STORE_ID}/opening/
```

## 📊 Résultats de la Capture

- **Total requêtes capturées**: 188
- **APIs Foodles identifiées**: 32
- **Endpoints uniques**: 20+

## 🔑 Authentification

Les APIs utilisent des cookies:
- `sessionid`: Cookie de session
- `csrftoken`: Token CSRF
- Header `X-CSRFToken`: Même valeur que le cookie

## 📝 Utilisation

```python
from foodles_real_api import FoodlesRealAPI

# Avec cookies existants
api = FoodlesRealAPI(
    session_id="...",
    csrf_token="..."
)

# Ou connexion email/password
api = FoodlesRealAPI()
api.login("email@example.com", "password")

# Utiliser les APIs
user = api.get_current_user()
fridge = api.get_fridge()
menu = api.get_store_menu(2051)
```

## ⚠️ Limitations Découvertes

1. **Menu/Panier**: Retourne 403 (Forbidden)
   - Probablement fermé ou nécessite des permissions spécifiques
   
2. **Produits**: Format RSC sur `/canteen/fridge/product/{ID}`
   - Pas d'API REST pour les détails produits
   - Données intégrées dans le HTML

## 🎯 Prochaines Étapes

1. ✅ **Client API fonctionnel** créé
2. ✅ **Authentification** opérationnelle
3. ✅ **Frigo** accessible
4. ⏳ **Panier/Commandes** - À explorer (403 pour le moment)
5. ⏳ **Produits détaillés** - Nécessite parsing RSC

## 📦 Données Disponibles

### `/api/fridge/`
- Liste des produits du frigo
- ~44 KB de données JSON
- Contient probablement: stocks, prix, disponibilité

### `/api/async/client/current/`
- ID client: 480960
- Profil utilisateur
- Préférences

### `/api/payments/meal-voucher-card/`
- Cartes TR enregistrées
- Soldes disponibles

## 🚀 Fichiers Créés

1. `foodles_real_api.py` - Client API complet
2. `capture_manual.py` - Script de capture interactive
3. `manual_capture/` - Résultats de la capture
   - `api_calls_20260130_144853.json`
   - `report_20260130_144853.json`

## 💡 Découvertes Techniques

1. **API Backend réelle**: `https://api.foodles.co/api/`
2. **Format**: JSON standard (pas RSC)
3. **Auth**: Cookies-based
4. **CORS**: Requiert `Origin: https://app.foodles.co`
5. **IDs**: 
   - Client: 480960
   - Store: 2051 (Worldline Copernic)
   - Produits: 10400, 16818, 11145, etc.
