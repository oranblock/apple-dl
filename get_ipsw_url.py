import urllib.request, json

# Apple's own software update catalog for tvOS
catalogs = [
    "https://mesu.apple.com/assets/com_apple_MobileAsset_SoftwareUpdate/com_apple_MobileAsset_SoftwareUpdate.xml",
    "https://gdmf.apple.com/v2/pmv",
]
for url in catalogs:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "AppleTV14,1/17.4 CFNetwork/1494.0.7 Darwin/23.4.0",
            "X-Apple-Client-Versions": "iTunesU=1; MZCommerce=24",
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read(5000)
        print(f"OK {url}:")
        print(raw[:1000].decode('utf-8', errors='replace'))
        print()
    except Exception as e:
        print(f"FAIL {url}: {e}")

# Try Apple GDMF API (publicly known catalog endpoint)
try:
    req = urllib.request.Request(
        "https://gdmf.apple.com/v2/pmv",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.load(r)
    tvos = d.get('AssetSets', {}).get('tvOS', [])
    print(f"tvOS versions: {len(tvos)}")
    for v in tvos[:5]:
        print(v)
except Exception as e:
    print(f"GDMF: {e}")
