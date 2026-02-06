# 🚀 Guide de démarrage rapide - Foodles API

## Installation express

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configuration rapide (déjà fait dans les scripts)
# Les tokens sont déjà dans les scripts Python
```

## 🎯 Quoi utiliser selon vos besoins

### 1️⃣ Test rapide
```bash
python example.py
```
**Usage:** Tester rapidement l'API et voir un parsing basique

### 2️⃣ Interface interactive (recommandé pour débuter)
```bash
python cli.py
```
**Usage:** Menu interactif pour explorer l'API de manière conviviale
- ✅ Facile à utiliser
- ✅ Navigation par menu
- ✅ Recherche et sauvegarde

### 3️⃣ Exploration automatique
```bash
python explore_api.py
```
**Usage:** Découvrir automatiquement tous les endpoints disponibles
- ✅ Génère `api_exploration.json`
- ✅ Teste 17+ endpoints
- ✅ Rapport détaillé

### 4️⃣ Analyse approfondie
```bash
python save_responses.py
```
**Usage:** Sauvegarder et analyser en profondeur les réponses
- ✅ Crée le dossier `api_responses/`
- ✅ 3 fichiers par endpoint (brut, réponse, parsé)
- ✅ Analyse des mots-clés

## 📊 Résultats déjà obtenus

### ✅ Endpoints fonctionnels découverts
1. `/canteen/fridge` - Données du frigo
2. `/canteen` - Page principale de la cantine
3. `/` - Page d'accueil
4. `/account` - Compte utilisateur

### 📁 Fichiers générés
- `api_exploration.json` - Rapport d'exploration (17 endpoints testés)
- `api_responses/` - Dossier avec toutes les réponses sauvegardées
  - 12 fichiers générés (4 endpoints × 3 fichiers)
  - Total: ~760KB de données

## 🔧 Utilisation programmatique

```python
from foodles_api import FoodlesAPI
from rsc_parser import parse_rsc_response

# Initialiser
api = FoodlesAPI(
    session_id="jflffcai4qqen1dqvmznt4gxfzu2nb14",
    csrf_token="hCykn22T0BFnO5COVjV7nftJmaH8mcjZ"
)

# Récupérer le frigo
fridge = api.get_fridge()
parsed = parse_rsc_response(fridge)

# Analyser
print(f"Objets JSON trouvés: {len(parsed['all_json_objects'])}")
print(f"Produits: {parsed['products']}")
```

## 🎨 Fonctionnalités du parser RSC

Le parser `rsc_parser.py` offre:
- ✅ Extraction d'objets JSON
- ✅ Recherche de mots-clés
- ✅ Extraction de produits/menu
- ✅ Décodage Unicode
- ✅ Analyse structurelle (fragments, modules)
- ✅ Extraction par clé
- ✅ Détection de structures imbriquées

## 🔍 Recherche dans le contenu

```python
from rsc_parser import RSCParser

parser = RSCParser(content_rsc)

# Rechercher des mots-clés
results = parser.search_in_content("product")
print(f"Trouvé {len(results)} occurrences")

# Extraire des données spécifiques
prices = parser.extract_data_by_key("price")
names = parser.extract_data_by_key("name")
```

## 📈 Statistiques d'analyse

D'après les explorations:
- **Canteen endpoint**: 38 objets JSON, 5 mots-clés pertinents
- **Home endpoint**: 37 objets JSON, 9 mots-clés pertinents
- **Account endpoint**: 38 objets JSON, 9 mots-clés pertinents
- **Fridge endpoint**: 9 objets JSON, 4 mots-clés pertinents

## 🎯 Prochaines étapes

Pour aller plus loin:
1. Analyser les fichiers dans `api_responses/` pour comprendre la structure
2. Identifier les patterns de données dans les JSON
3. Créer des extracteurs spécifiques pour les produits
4. Implémenter les fonctionnalités de panier/commande
5. Ajouter l'authentification automatique

## 💡 Astuces

- Les endpoints nécessitent le paramètre `_rsc=1d46b`
- L'API utilise React Server Components (format spécial)
- Les cookies `sessionid` et `csrftoken` sont essentiels
- Le format RSC est parsable mais complexe

## 🐛 Debug

Si vous avez des erreurs 403/401:
```python
# Récupérer de nouveaux tokens depuis le navigateur
# F12 > Application > Cookies > app.foodles.co
```

Si une réponse semble vide:
```python
# Vérifier le contenu brut
print(response['raw_content'])
```

## 📞 Support

Tous les scripts incluent une gestion d'erreur détaillée.
Consultez les fichiers de log générés pour plus d'infos.
