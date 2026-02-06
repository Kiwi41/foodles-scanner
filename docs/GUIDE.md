# 📚 Guide d'utilisation Foodles Scanner

## 🎯 Cas d'usage

### 1. Je veux voir les produits en DLC courte aujourd'hui

```bash
# Option rapide: rapport automatique
./scripts/auto_report.sh

# Le rapport indique pour chaque cantine:
# 🔥 7 produits en DLC courte (Amazone)
# 🔥 7 produits en DLC courte (Hangar)
# 🔥 0 produits en DLC courte (Copernic)
```

### 2. Je veux mettre à jour les données d'une cantine

```bash
python scripts/capture_manual_cantine.py

# Puis suivre les instructions:
# 1. Se connecter sur app.foodles.co
# 2. Changer vers la cantine désirée
# 3. F12 → Application → Cookies
# 4. Copier sessionid et csrftoken
```

### 3. Je veux comparer les cantines

```bash
python scripts/compare_cantines.py

# Option 1: Comparer toutes les cantines
# Option 2: Rechercher un produit spécifique
# Option 3: Afficher les données sauvegardées
```

### 4. Je veux chercher un produit spécifique

```bash
python scripts/compare_cantines.py
# Choisir option 2
# Entrer le nom du produit (ex: "cookie", "poulet", "quiche")
```

## 🔄 Workflow typique

### Première utilisation

```bash
# 1. Installation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditer .env avec les cookies

# 3. Première capture
python scripts/capture_manual_cantine.py
# Capturer les 3 cantines (répéter 3 fois)

# 4. Générer le rapport
./scripts/auto_report.sh
```

### Usage quotidien

```bash
# Rapport rapide avec les données existantes
./scripts/auto_report.sh

# Mise à jour d'une cantine (optionnel)
python scripts/capture_manual_cantine.py
```

## 📊 Comprendre les rapports

### Synthèse comparative

```
🏢 Worldline Amazone
   📍 5 rue Copernic, 41000 Blois
   📦 39 produits | 72 unités       ← Variété vs Stock
   💰 Prix moyen: 2.42€              ← Prix moyen des produits
   🌱 35/39 végétariens (89.7%)      ← % de produits végétariens
   🔥 7 produits en DLC courte       ← Produits en promotion
```

### Comparaison par catégorie

```
📂 Plats
   Worldline Copernic  :  7 produits |  23 unités
   Worldline Amazone   :  9 produits |  16 unités
   Worldline Hangar    :  9 produits |  16 unités
```

### Top produits

```
1. 🌱 Super Cookie                |  7x | 2.20€
   └─ Worldline Copernic - Desserts
```
- 🌱 = Végétarien
- 🥩 = Non végétarien
- 7x = 7 unités en stock

## 🔐 Gestion des cookies

### Pourquoi les cookies expirent ?

Les cookies de session Foodles ont une durée de vie limitée (~2 semaines). Après expiration :
- Erreur 403 (Accès refusé)
- Erreur 401 (Non autorisé)

### Comment renouveler ?

1. Se connecter sur app.foodles.co
2. Changer vers la cantine désirée
3. F12 → Application → Cookies → app.foodles.co
4. Copier `sessionid` et `csrftoken`
5. Mettre à jour `.env` OU les entrer dans `capture_manual_cantine.py`

### Cookies par cantine

⚠️ **Important** : Les cookies sont liés à la cantine sélectionnée !

- Si tu es sur **Copernic** → Les cookies donnent accès à Copernic
- Pour Amazone/Hangar → Il faut **changer de cantine** puis récupérer de nouveaux cookies

## 🏗️ Architecture

### Flux de données

```
app.foodles.co
      ↓
   API REST (https://api.foodles.co)
      ↓
capture_manual_cantine.py
      ↓
cantines_data/cantine_*.json
      ↓
compare_cantines.py / auto_report.sh
      ↓
Rapport comparatif
```

### Scripts principaux

| Script | Fonction | Usage |
|--------|----------|-------|
| `capture_manual_cantine.py` | Capture données | Mise à jour |
| `compare_cantines.py` | Comparaison interactive | Exploration |
| `auto_report.sh` | Rapport automatique | Quotidien |
| `generate_report.py` | Rapport détaillé | Analyse |

## 🎓 Cas avancés

### Automatiser la capture quotidienne

Créer un cron job :

```bash
# Éditer crontab
crontab -e

# Ajouter (capture tous les jours à 8h)
0 8 * * * cd /path/to/foodle && ./scripts/auto_report.sh > logs/daily_$(date +\%Y\%m\%d).txt
```

### Analyser l'évolution dans le temps

Les fichiers sont horodatés : `cantine_Amazone_20260130.json`

```bash
# Comparer 2 captures
python scripts/compare_dates.py cantine_Amazone_20260130.json cantine_Amazone_20260131.json
```

### Exporter en CSV

```bash
# Depuis Python
import json
import csv

with open('cantines_data/cantine_Amazone_20260130.json') as f:
    data = json.load(f)
    
# Traiter et exporter...
```

## ❓ FAQ

### Pourquoi certains produits n'ont pas de prix ?

Certains produits ne sont pas vendus (échantillons, tests).

### Qu'est-ce que "DLC courte" ?

**DLC** = Date Limite de Consommation

Les produits en DLC courte sont :
- Proches de leur date d'expiration
- En promotion (prix réduit)
- Identifiés par `has_near_expiration_sale: true`

### Comment savoir si un produit est végétarien ?

Le champ `filter_reasons.excluded_diets` indique les régimes exclus :
- `[]` ou `["PESCATARIAN"]` = Végétarien ✅
- `["VEGETARIAN"]` = Non végétarien ❌

### Les données sont-elles en temps réel ?

Non, les données sont capturées au moment de l'exécution. Pour avoir les données actuelles, relancer `capture_manual_cantine.py`.

### Puis-je utiliser ce projet pour d'autres cantines ?

Oui, il suffit de modifier les IDs de cantines dans `scripts/compare_cantines.py` :

```python
self.cantines = [
    {'id': XXXX, 'nom': 'Ma Cantine', 'adresse': '...'},
]
```

## 🐛 Résolution de problèmes

### Erreur: "Module not found"

```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur: "Permission denied"

```bash
# Rendre les scripts exécutables
chmod +x scripts/*.sh
```

### Les données sont vides

Vérifier :
1. Cookies valides (< 2 semaines)
2. Bonne cantine sélectionnée
3. Connexion internet OK

### Le rapport ne s'affiche pas bien

Utiliser un terminal avec support UTF-8 et émojis.

## 📞 Support

Pour toute question, consulter :
- [README.md](../README.md) : Documentation principale
- [docs/](.) : Documentation technique
- [archive/](../archive/) : Ancien code de référence

---

**Dernière mise à jour** : 30 janvier 2026
