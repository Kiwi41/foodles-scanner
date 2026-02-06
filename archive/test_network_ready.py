"""Test de préparation pour l'interception réseau"""
print("╔══════════════════════════════════════════════════════════╗")
print("║  ✅ PLAYWRIGHT INSTALLÉ ET PRÊT                          ║")
print("╚══════════════════════════════════════════════════════════╝")
print()
print("📦 Vérification de l'installation:")
try:
    from playwright.sync_api import sync_playwright
    print("  ✅ Module playwright importé")
    
    with sync_playwright() as p:
        browsers = []
        if p.chromium.executable_path:
            browsers.append("Chromium")
        print(f"  ✅ Navigateurs disponibles: {', '.join(browsers)}")
    
    print()
    print("🚀 Prêt pour l'interception réseau!")
    print()
    print("📋 Prochaines étapes:")
    print("  1. Exécuter: python network_interceptor.py")
    print("  2. Se connecter manuellement dans le navigateur")
    print("  3. Laisser le script capturer les requêtes")
    print("  4. Analyser les résultats dans network_capture/")
    print()
    print("📖 Voir: NETWORK_CAPTURE_GUIDE.md pour plus de détails")
    
except Exception as e:
    print(f"  ❌ Erreur: {e}")
    print()
    print("💡 Installez Playwright:")
    print("  pip install playwright")
    print("  playwright install chromium")

