import json, sys, urllib.request

agents = [
    "com.apple.tv.TVShows/2 CFNetwork/1490.0.4 Darwin/23.2.0",
    "AppleTV6,2/11.1",
    "com.apple.TVWallpaper/1 CFNetwork",
]
urls = [
    "https://sylvan.apple.com/Apple_TV_4K_v3.json",
    "https://sylvan.apple.com/Apple_TV_4K_v2.json",
]
for ua in agents:
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            print(f"OK {len(data)}b | {ua[:30]} | {url}")
            if len(data) > 500:
                with open("newer_manifest.json", "wb") as f:
                    f.write(data)
                d = json.loads(data)
                assets = d.get('assets', [])
                print(f"  Assets: {len(assets)}")
                snoopy = [a for a in assets if 'snoopy' in str(a).lower()]
                print(f"  Snoopy: {len(snoopy)}")
                if snoopy:
                    for s in snoopy:
                        print("  ", s.get('url',''))
        except Exception as e:
            print(f"FAIL | {ua[:30]} | {url} | {e}")
