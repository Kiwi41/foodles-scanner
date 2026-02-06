# 🍱 Foodles API Scanner

Scanner automatique pour analyser les cantines Foodles.

## 📋 Description

Ce projet permet de scanner automatiquement plusieurs cantines Foodles (Copernic, Amazone, Hangar) et de générer des rapports comparatifs complets incluant :
- Stock disponible par cantine
- Produits en DLC courte (Date Limite de Consommation)
- Analyse végétarienne
- Comparaison des prix
- Classement par catégorie

## 🚀 Installation

```bash
# Cloner le projet
git clone <url>
cd foodle

# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copier le fichier de configuration :
```bash
cp .env.example .env
```

2. Obtenir les cookies de session :
   - Ouvrir [app.foodles.co](https://app.foodles.co) dans le navigateur
   - Se connecter
   - Ouvrir DevTools (F12) → Application → Cookies
   - Copier les valeurs de `sessionid` et `csrftoken`

3. Éditer le fichier `.env` :
```env
FOODLES_SESSIONID=votre_session_id_ici
FOODLES_CSRFTOKEN=votre_csrf_token_ici
```

## 📊 Utilisation

### Méthode 1 : Capture automatique (recommandé) 🤖

Capture automatiquement les 3 cantines en ~30 secondes avec Playwright :

```bash
python scripts/capture_hybrid_auto.py
```

**Avantages :**
- 100% automatique (aucune interaction requise)
- Méthode hybride : Playwright pour les clics + HTTP pour les données
- Lance automatiquement le rapport à la fin
- Fiable et rapide

### Méthode 2 : Rapport depuis données existantes

Génère un rapport comparatif depuis les dernières données capturées :

```bash
python scripts/generate_report.py
```

### Méthode 3 : Comparaison interactive

```bash
python scripts/compare_cantines.py
```

Options disponibles :
1. Comparer toutes les cantines
2. Rechercher un produit spécifique
3. Afficher les données sauvegardées

## 📁 Structure du projet

```
foodle/
├── README.md                    # Documentation principale (ce fichier)
├── .env                         # Configuration (cookies)
├── requirements.txt             # Dépendances Python
│
├── scripts/                     # Scripts principaux
│   ├── capture_hybrid_auto.py      # 🤖 Capture auto (Playwright + HTTP)
│   ├── generate_report.py          # 📊 Générateur de rapport détaillé
│   ├── compare_cantines.py         # 🔍 Comparaison interactive
│   └── auto_report.sh              # Wrapper shell (legacy)
│
├── lib/                         # Librairies API
│   ├── foodles_real_api.py         # Client API REST Foodles
│   └── parse_fridge.py             # Parser de données frigo
│
├── cantines_data/               # Données capturées (JSON)
│   ├── cantine_Copernic_*.json
│   ├── cantine_Amazone_*.json
│   ├── cantine_Hangar_*.json
│   └── bilan_comparatif_*.json
│
├── data/                        # Données brutes et archives
├── docs/                        # Documentation supplémentaire
└── archive/                     # Ancien code (historique)
```

## 📊 Résultats

### Exemple de rapport comparatif :

```
🏢 Worldline Copernic
   📍 3 rue Copernic, 41000 Blois
   📦 31 produits | 99 unités
   💰 Prix moyen: 2.79€
   🌱 26/31 végétariens (83.9%)
   🔥 0 produits en DLC courte

🏢 Worldline Amazone
   📍 5 rue Copernic, 41000 Blois
   📦 39 produits | 72 unités
   💰 Prix moyen: 2.42€
   🌱 35/39 végétariens (89.7%)
   🔥 7 produits en DLC courte

🏢 Worldline Hangar
   📍 11 rue Copernic, 41000 Blois
   📦 35 produits | 61 unités
   💰 Prix moyen: 2.50€
   🌱 29/35 végétariens (82.9%)
   🔥 7 produits en DLC courte
```

### Total réseau :
- **105 produits** uniques
- **232 unités** en stock
- **14 produits** en DLC courte

## 🔍 Fonctionnalités avancées

### Rechercher un produit spécifique

```bash
python scripts/compare_cantines.py
# Choisir l'option 2
```

### Générer un rapport détaillé

```bash
python scripts/generate_report.py
```

### Capturer uniquement les produits en DLC courte

Le champ `has_near_expiration_sale` identifie automatiquement les produits en promotion DLC.

## 🛠️ Développement

### Dépendances principales

- `requests` : Appels API REST
- `python-dotenv` : Gestion configuration
- `playwright` : Automatisation navigateur (optionnel)

### API Endpoints découverts

- `GET /api/fridge/` : Données du frigo actuel
- `GET /api/client/` : Informations client
- `GET /api/fridge/canteen/{id}/` : Données d'une cantine spécifique (nécessite cookie valide)

### Format des données

Les données sont stockées en JSON avec cette structure :

```json
{
  "categories": [
    {
      "name": "Plats",
      "products": [
        {
          "id": 123,
          "name": "Nom du produit",
          "quantity": 5,
          "price": {"amount": 5.80, "currency": "EUR"},
          "has_near_expiration_sale": false,
          "filter_reasons": {
            "excluded_diets": []
          }
        }
      ]
    }
  ]
}
```

## 🐛 Dépannage

### Erreur 403 (Accès refusé)

Les cookies ont expiré ou la cantine sélectionnée ne correspond pas aux cookies.

**Solution** : Recapturer les cookies depuis la bonne cantine.

### Erreur 404 (Non trouvé)

L'endpoint n'existe pas ou l'ID de cantine est incorrect.

**Solution** : Utiliser `capture_manual_cantine.py` qui utilise l'endpoint `/api/fridge/` général.

### Aucune donnée capturée

Vérifier que :
1. Les cookies sont valides (< 2 semaines)
2. La connexion internet fonctionne
3. Vous êtes bien connecté sur app.foodles.co

## 📝 Changelog

### Version 2.0 (30/01/2026)
- ✅ Scanner automatique des 3 cantines
- ✅ Détection des produits en DLC courte
- ✅ Rapport comparatif complet
- ✅ Analyse végétarienne
- ✅ Organisation du projet

### Version 1.0
- Client API REST basique
- Extraction manuelle des données

## 📄 Licence

Projet open-source MIT

## 👤 Auteur

Projet d'analyse automatique de cantines Foodles.

---

**Note** : Ce projet utilise l'API non-officielle de Foodles. Les cookies de session doivent être renouvelés régulièrement.
