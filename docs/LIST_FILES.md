# 📁 Liste complète des fichiers du projet

## 🐍 Code Python (10 fichiers)

| Fichier | Description | Lignes |
|---------|-------------|--------|
| `foodles_api.py` | Client API principal | ~200 |
| `config.py` | Gestion de configuration | ~60 |
| `rsc_parser.py` | Parser React Server Components | ~250 |
| `example.py` | Exemple d'utilisation avec parsing | ~90 |
| `cli.py` | Interface en ligne de commande interactive | ~220 |
| `explore_api.py` | Explorateur automatique d'endpoints | ~130 |
| `save_responses.py` | Sauvegarde et analyse des réponses | ~130 |
| `visualize.py` | Visualiseur de données avancé | ~240 |
| `extract_products.py` | Extracteur de produits | ~260 |
| `debug_content.py` | Debug du contenu RSC | ~40 |

**Total:** ~1620 lignes de Python

## 📖 Documentation (5 fichiers)

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale complète |
| `QUICKSTART.md` | Guide de démarrage rapide |
| `PROJECT_SUMMARY.md` | Résumé complet du projet |
| `TODO.md` | Prochaines étapes et roadmap |
| `LIST_FILES.md` | Ce fichier - liste de tous les fichiers |

## ⚙️ Configuration (4 fichiers)

| Fichier | Description |
|---------|-------------|
| `requirements.txt` | Dépendances Python |
| `.env.example` | Template de configuration |
| `.gitignore` | Fichiers à ignorer par Git |
| `config.py` | Configuration programmatique |

## 📊 Données générées (15+ fichiers)

### Dans `api_responses/` (12 fichiers)
```
fridge_20260130_141934_raw.txt
fridge_20260130_141934_response.json
fridge_20260130_141934_parsed.json

canteen_20260130_141934_raw.txt
canteen_20260130_141934_response.json
canteen_20260130_141934_parsed.json

home_20260130_141935_raw.txt
home_20260130_141935_response.json
home_20260130_141935_parsed.json

account_20260130_141935_raw.txt
account_20260130_141935_response.json
account_20260130_141935_parsed.json
```

### Racine du projet
```
api_exploration.json         - Rapport d'exploration (17 endpoints)
api_documentation.json       - Documentation structurée de l'API
products.json               - Fichier produits (vide pour l'instant)
fridge_full_content.txt     - Contenu RSC complet du frigo
```

## 📈 Statistiques

- **Total fichiers Python:** 10
- **Total lignes Python:** ~1620
- **Total documentation:** 5 fichiers
- **Total fichiers générés:** 15+
- **Taille données générées:** ~760KB
- **Endpoints testés:** 17
- **Endpoints fonctionnels:** 4

## 🎯 Points d'entrée recommandés

1. **Découvrir le projet:** `README.md`
2. **Démarrage rapide:** `QUICKSTART.md`
3. **Test basique:** `python example.py`
4. **Interface interactive:** `python cli.py`
5. **Exploration complète:** `python explore_api.py`

## 📦 Structure arborescente

```
foodle/
├── 📄 Configuration
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── config.py
│
├── 🐍 Code source
│   ├── foodles_api.py (Client API)
│   ├── rsc_parser.py (Parser RSC)
│   ├── example.py (Exemple)
│   ├── cli.py (Interface CLI)
│   ├── explore_api.py (Explorateur)
│   ├── save_responses.py (Sauvegarde)
│   ├── visualize.py (Visualiseur)
│   ├── extract_products.py (Extracteur)
│   └── debug_content.py (Debug)
│
├── 📖 Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── PROJECT_SUMMARY.md
│   ├── TODO.md
│   └── LIST_FILES.md
│
├── 📊 Données générées
│   ├── api_responses/
│   │   ├── fridge_*.{raw.txt,response.json,parsed.json}
│   │   ├── canteen_*.{raw.txt,response.json,parsed.json}
│   │   ├── home_*.{raw.txt,response.json,parsed.json}
│   │   └── account_*.{raw.txt,response.json,parsed.json}
│   ├── api_exploration.json
│   ├── api_documentation.json
│   ├── products.json
│   └── fridge_full_content.txt
│
└── 🔧 Environnement
    ├── .venv/ (environnement virtuel Python)
    └── .env (configuration locale - non versionné)
```

## 🚀 Commandes utiles

```bash
# Lister tous les fichiers Python
ls -1 *.py

# Compter les lignes de code
wc -l *.py

# Voir la taille des fichiers générés
du -sh api_responses/

# Lancer tous les scripts en séquence
python example.py && python explore_api.py && python save_responses.py

# Nettoyer les fichiers générés
rm -rf api_responses/ *.json *.txt
```

## 📝 Notes

- Tous les scripts utilisent les mêmes credentials configurés
- Les données sont sauvegardées avec timestamp
- Le dossier `api_responses/` est ignoré par Git
- Le fichier `.env` doit être créé depuis `.env.example`

---

**Généré le:** 30 janvier 2026
**Total fichiers:** 40+
**Status:** ✅ Complet et fonctionnel
