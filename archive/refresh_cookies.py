#!/usr/bin/env python3
"""
Script pour récupérer de nouveaux cookies via Playwright.
Ouvre un navigateur, laisse l'utilisateur se connecter, puis capture les cookies.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from playwright.sync_api import sync_playwright
import time
from datetime import datetime

def get_new_cookies():
    """Capture de nouveaux cookies via login manuel"""
    
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║           🔐 RÉCUPÉRATION DES COOKIES FOODLES                          ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    print("📋 Instructions:")
    print("   1. Un navigateur Chrome va s'ouvrir")
    print("   2. Connectez-vous sur app.foodles.co")
    print("   3. Une fois connecté, restez sur la page")
    print("   4. Les cookies seront automatiquement capturés")
    print("   5. Le navigateur se fermera après 5 secondes\n")
    
    input("Appuyez sur ENTER pour continuer...")
    
    with sync_playwright() as p:
        print("\n🌐 Ouverture du navigateur...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("🔗 Navigation vers app.foodles.co...")
        page.goto("https://app.foodles.co/auth/login")
        
        print("\n⏳ En attente de votre connexion...")
        print("   (Le script attend que vous vous connectiez)")
        
        # Attendre que l'utilisateur se connecte (URL change)
        try:
            page.wait_for_url("https://app.foodles.co/canteen/**", timeout=120000)
            print("\n✅ Connexion détectée!")
        except:
            print("\n⚠️  Timeout ou pas de redirection - capture des cookies quand même")
        
        # Attendre un peu pour que tout se charge
        print("⏳ Attente de 3 secondes...")
        time.sleep(3)
        
        # Récupérer tous les cookies
        cookies = context.cookies()
        
        print(f"\n📦 {len(cookies)} cookies capturés")
        
        # Extraire les cookies importants
        sessionid = None
        csrftoken = None
        
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                sessionid = cookie['value']
                print(f"   ✅ sessionid: {sessionid[:20]}...")
            elif cookie['name'] == 'csrftoken':
                csrftoken = cookie['value']
                print(f"   ✅ csrftoken: {csrftoken[:20]}...")
        
        if sessionid and csrftoken:
            print("\n✅ Cookies trouvés!")
            
            # Sauvegarder dans .env
            env_content = f"""# Configuration Foodles
# Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FOODLES_SESSIONID={sessionid}
FOODLES_CSRFTOKEN={csrftoken}
FOODLES_CANTEEN_ID=2051
FOODLES_CLIENT_ID=480960
"""
            
            env_path = Path(__file__).parent / '.env'
            env_path.write_text(env_content)
            
            print(f"\n💾 Cookies sauvegardés dans {env_path}")
            print("\n📋 Vous pouvez maintenant utiliser:")
            print("   • python foodles_complete.py")
            print("   • python foodles_cli.py")
            print("   • python explore_403.py")
            
        else:
            print("\n❌ Cookies non trouvés!")
            print("💡 Assurez-vous d'être bien connecté sur app.foodles.co")
        
        print("\n⏳ Fermeture dans 5 secondes...")
        time.sleep(5)
        
        browser.close()
        
        return sessionid, csrftoken

if __name__ == "__main__":
    try:
        get_new_cookies()
    except KeyboardInterrupt:
        print("\n\n❌ Annulé par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur: {e}")
        import traceback
        traceback.print_exc()
