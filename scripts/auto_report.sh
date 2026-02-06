#!/bin/bash
# Script bash pour automatiser complètement le scan et le rapport

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║          🚀 SCAN AUTOMATIQUE COMPLET DES 3 CANTINES                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🤖 Mode 100% automatique avec les données déjà capturées"
echo ""

# Se placer dans le dossier parent
cd "$(dirname "$0")/.."

# Activer l'environnement virtuel
source .venv/bin/activate

# Générer le rapport comparatif complet
echo "1" | python scripts/compare_cantines.py

echo ""
echo "✅ Rapport terminé!"
echo ""
