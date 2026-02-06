#!/usr/bin/env python3
"""
Script pour logger TOUTES les requêtes réseau
Pour comprendre comment les données sont chargées
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    sessionid = '0e7doeqn3nqkxn1zb722c4blty5vayg5'
    csrftoken = 'w23gonol4yxqMKsfRr7XcHMl7lEaXsdy'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        await context.add_cookies([
            {'name': 'sessionid', 'value': sessionid, 'domain': '.foodles.co', 'path': '/'},
            {'name': 'csrftoken', 'value': csrftoken, 'domain': '.foodles.co', 'path': '/'}
        ])
        
        page = await context.new_page()
        
        # Logger TOUTES les requêtes
        async def log_request(request):
            if 'api.foodles.co' in request.url:
                print(f"→ REQUEST: {request.method} {request.url}")
        
        async def log_response(response):
            if 'api.foodles.co' in response.url:
                print(f"← RESPONSE: {response.status} {response.url}")
                if response.status == 200 and '/api/' in response.url:
                    try:
                        data = await response.json()
                        if 'categories' in data:
                            print(f"   ✅ CONTIENT 'categories' !")
                            nb_cats = len(data.get('categories', []))
                            print(f"   📊 {nb_cats} catégories trouvées")
                    except:
                        pass
        
        page.on('request', log_request)
        page.on('response', log_response)
        
        print("🌐 Chargement de app.foodles.co...")
        await page.goto('https://app.foodles.co/', wait_until='domcontentloaded')
        
        print("\n⏳ Attente 10 secondes... (cliquez manuellement si vous voulez)")
        await asyncio.sleep(10)
        
        print("\n✅ Terminé - fermeture dans 3s")
        await asyncio.sleep(3)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
