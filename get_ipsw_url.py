import json, urllib.request

# Try ipsw.me web API directly
for path in [
    "https://ipsw.me/api/v4/firmwares.json",
    "https://api.ipsw.me/v4/firmwares.json",
    "https://ipsw.me/AppleTV14,1",
]:
    try:
        req = urllib.request.Request(path, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read(2000)
        print(f"OK {path}: {raw[:300]}")
        break
    except Exception as e:
        print(f"FAIL {path}: {e}")

# Try Apple's IPSW catalog
print("\n=== Apple IPSW Catalog ===")
try:
    req = urllib.request.Request(
        "https://api.ipsw.me/v4/ipsw/AppleTV14,1",
        headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.load(r)
    if isinstance(d, list):
        for f in d[:5]:
            print(f.get('version','?'), f.get('url','?')[:80])
            if f.get('url'):
                print(f"IPSW_URL={f['url']}")
                break
    else:
        print(d)
except Exception as e:
    print(f"Error: {e}")
