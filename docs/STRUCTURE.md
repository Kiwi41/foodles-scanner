# Foodles Scanner - Structure du projet

Dernière mise à jour : 30 janvier 2026

## 📁 Arborescence

```
foodle/
│
├── 📄 README.md                 # Documentation principale
├── 📄 requirements.txt          # Dépendances Python
├── 🔒 .env                      # Configuration (cookies)
├── 🔒 .env.example              # Template configuration
├── 📄 .gitignore                # Fichiers ignorés par Git
│
├── 📂 scripts/                  # ⭐ Scripts principaux
│   ├── capture_manual_cantine.py   # Capture d'une cantine
│   ├── compare_cantines.py         # Comparaison interactive
│   ├── auto_report.sh              # Rapport automatique (recommandé)
│   └── generate_report.py          # Rapport détaillé
│
├── 📂 lib/                      # Librairies API
│   ├── foodles_real_api.py         # Client API REST
│   └── parse_fridge.py             # Parser de données
│
├── 📂 cantines_data/            # 💾 Données capturées
│   ├── cantine_Copernic_*.json     # Données Copernic
│   ├── cantine_Amazone_*.json      # Données Amazone
│   ├── cantine_Hangar_*.json       # Données Hangar
│   └── bilan_comparatif_*.json     # Rapports générés
│
├── 📂 data/                     # Données brutes/historiques
│   ├── foodles_products.json       # Produits extraits
│   ├── fridge_raw_data.json        # Données brutes frigo
│   ├── api_documentation.json      # Doc API
│   └── ...
│
├── 📂 docs/                     # 📚 Documentation
│   ├── GUIDE.md                    # Guide d'utilisation complet
│   ├── APIS_DISCOVERED.md          # APIs découvertes
│   ├── PROJECT_SUMMARY.md          # Résumé projet
│   ├── QUICKSTART.md               # Démarrage rapide
│   └── ...
│
├── 📂 archive/                  # Code historique
│   ├── foodles_cli.py              # Ancien CLI
│   ├── network_interceptor.py      # Intercepteur réseau
│   ├── smart_scan_cantines.py      # Scanner semi-auto
│   └── ... (30+ fichiers)
│
├── 📂 api_responses/            # Réponses API brutes
├── 📂 network_capture/          # Captures réseau Playwright
└── 📂 manual_capture/           # Captures manuelles
```

## 🚀 Scripts principaux (à utiliser)

### 1. Rapport automatique ⭐
```bash
./scripts/auto_report.sh
```
**Usage** : Quotidien, génère le rapport en 1 seconde

### 2. Capture manuelle
```bash
python scripts/capture_manual_cantine.py
```
**Usage** : Mettre à jour les données d'une cantine

### 3. Comparaison interactive
```bash
python scripts/compare_cantines.py
```
**Usage** : Explorer, rechercher, comparer

### 4. Rapport détaillé
```bash
python scripts/generate_report.py
```
**Usage** : Analyse approfondie

## 📚 Documentation

- [README.md](../README.md) : Documentation principale
- [docs/GUIDE.md](docs/GUIDE.md) : Guide d'utilisation complet
- [docs/APIS_DISCOVERED.md](docs/APIS_DISCOVERED.md) : APIs REST découvertes
- [docs/QUICKSTART.md](docs/QUICKSTART.md) : Démarrage rapide

## 📊 Données

### Données actuelles (cantines_data/)
- **cantine_Copernic_20260130.json** : 31 produits, 99 unités
- **cantine_Amazone_20260130.json** : 39 produits, 72 unités, 7 DLC
- **cantine_Hangar_20260130.json** : 35 produits, 61 unités, 7 DLC

### Rapports (cantines_data/)
- **bilan_comparatif_*.json** : Rapports générés automatiquement

## 🗄️ Archive

Le dossier `archive/` contient l'historique du développement :
- Premiers prototypes (example.py, cli.py)
- Tentatives d'automatisation (smart_scan_cantines.py)
- Outils d'exploration (network_interceptor.py)
- Tests et expérimentations

⚠️ **Ces fichiers ne sont plus utilisés** mais conservés pour référence.

## 🔧 Configuration

### Fichiers de configuration
- `.env` : Cookies de session (sessionid, csrftoken)
- `.env.example` : Template à copier
- `.gitignore` : Exclut .env, __pycache__, .venv

### Dépendances (requirements.txt)
```
requests==2.31.0
python-dotenv==1.0.0
playwright==1.40.0
```

## 📈 Statistiques

- **Scripts actifs** : 4 (dans scripts/)
- **Librairies** : 2 (dans lib/)
- **Fichiers archivés** : 30+ (dans archive/)
- **Documentation** : 8 fichiers
- **Cantines scannées** : 3 (Copernic, Amazone, Hangar)
- **Produits suivis** : 105 uniques, 232 unités

## 🔄 Workflow

```
1. Configuration    → .env avec cookies
2. Capture          → scripts/capture_manual_cantine.py
3. Rapport          → scripts/auto_report.sh
4. Exploration      → scripts/compare_cantines.py
```

## 🎯 Prochaines étapes

- [ ] Automatisation complète (cron job)
- [ ] Export CSV/Excel
- [ ] Graphiques d'évolution
- [ ] Notifications Discord/Slack
- [ ] API REST locale

---

**Version** : 2.0  
**Dernière révision** : 30 janvier 2026
