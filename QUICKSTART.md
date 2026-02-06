# ⚡ Démarrage rapide

## Installation (1 minute)

```bash
# 1. Cloner et se placer dans le projet
cd foodle

# 2. Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les cookies
cp .env.example .env
nano .env  # Ajouter sessionid et csrftoken
```

## Obtenir les cookies (30 secondes)

1. Ouvrir https://app.foodles.co dans le navigateur
2. Se connecter
3. Appuyer sur **F12** (DevTools)
4. Onglet **Application** → **Cookies** → **app.foodles.co**
5. Copier les valeurs de **sessionid** et **csrftoken**
6. Les coller dans `.env`

## Première capture automatique (30 secondes)

```bash
python scripts/capture_hybrid_auto.py
```

Le script va :
1. Ouvrir Chrome automatiquement
2. Cliquer sur chaque cantine (Copernic, Amazone, Hangar)
3. Récupérer les données via HTTP
4. Afficher le rapport comparatif

## C'est tout ! 🎉

Tu as maintenant accès à :
- Capture 100% automatique des 3 cantines
- Rapport comparatif détaillé
- Produits en DLC courte
- Analyse végétarienne
- Comparaison des stocks

## Prochaines étapes

- [README.md](README.md) : Documentation complète
- [docs/GUIDE.md](docs/GUIDE.md) : Guide d'utilisation détaillé
- [docs/STRUCTURE.md](docs/STRUCTURE.md) : Structure du projet

## Commandes utiles

```bash
# Capture automatique des 3 cantines (recommandé)
python scripts/capture_hybrid_auto.py

# Générer un rapport depuis données existantes
python scripts/generate_report.py

# Comparaison interactive
python scripts/compare_cantines.py
```
