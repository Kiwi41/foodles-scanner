#!/usr/bin/env python3
"""
Scénario complet : Capture + Affichage DLC
Exécute la capture automatique des 3 cantines puis affiche le tableau des DLC
"""

import asyncio
import sys
import os

# Importer les modules des autres scripts
from capture_hybrid_auto import HybridAutoCapture
from show_dlc import load_cantines_data, display_table

async def main():
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║              🍱 SCAN COMPLET FOODLES + ANALYSE DLC                     ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Étape 1 : Capture automatique
    print("📥 ÉTAPE 1/2 : Capture automatique des cantines\n")
    capture = HybridAutoCapture()
    count = await capture.run()
    
    if count == 0:
        print("\n❌ Échec de la capture. Impossible de continuer.")
        return 1
    
    print(f"\n{'='*70}")
    print(f"✅ Capture terminée: {count}/3 cantines")
    print(f"{'='*70}\n")
    
    # Petite pause
    await asyncio.sleep(2)
    
    # Étape 2 : Affichage des DLC
    print("\n🔥 ÉTAPE 2/2 : Analyse des produits en DLC courte\n")
    
    cantines = ['Copernic', 'Amazone', 'Hangar']
    products_dlc, _ = load_cantines_data()
    
    if not products_dlc:
        print("ℹ️  Aucun produit en DLC courte aujourd'hui.")
        return 0
    
    display_table(products_dlc, cantines)
    
    print("\n" + "="*70)
    print("✅ SCAN COMPLET TERMINÉ!")
    print("="*70)
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
