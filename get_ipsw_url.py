import urllib.request, plistlib

# Try all known Apple TV content/idle asset catalog URLs
catalog_urls = [
    "https://mesu.apple.com/assets/com_apple_MobileAsset_TVIdleAssets/com_apple_MobileAsset_TVIdleAssets.xml",
    "https://mesu.apple.com/assets/com_apple_MobileAsset_TVIdleScreenVideoAssets/com_apple_MobileAsset_TVIdleScreenVideoAssets.xml",
    "https://mesu.apple.com/assets/com_apple_MobileAsset_TVWallpaperAerials/com_apple_MobileAsset_TVWallpaperAerials.xml",
    "https://mesu.apple.com/assets/com_apple_MobileAsset_TVWallpaper/com_apple_MobileAsset_TVWallpaper.xml",
    "https://mesu.apple.com/assets/tvos/com_apple_MobileAsset_TVIdleAssets/com_apple_MobileAsset_TVIdleAssets.xml",
    "https://mesu.apple.com/assets/tvos16/com_apple_MobileAsset_TVIdleAssets/com_apple_MobileAsset_TVIdleAssets.xml",
    "https://mesu.apple.com/assets/tvos17/com_apple_MobileAsset_TVIdleAssets/com_apple_MobileAsset_TVIdleAssets.xml",
]

for url in catalog_urls:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "AppleTV14,1/17.4 CFNetwork/1494.0.7 Darwin/23.4.0"
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        print(f"OK {len(raw)}b: {url}")
        try:
            plist = plistlib.loads(raw)
            assets = plist.get('Assets', [])
            print(f"  Assets: {len(assets)}")
            for a in assets[:3]:
                base = a.get('__BaseURL', '')
                rel = a.get('__RelativePath', '')
                print(f"  {base}{rel}")
                # Check for snoopy
                full_str = str(a)
                if 'snoopy' in full_str.lower():
                    print(f"  *** SNOOPY FOUND ***")
                    print(f"  {full_str[:500]}")
        except:
            print(f"  Raw: {raw[:200]}")
    except Exception as e:
        print(f"FAIL {url}: {e}")
