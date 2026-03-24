import json, urllib.request

devices = ["AppleTV14,1", "AppleTV13,2", "AppleTV11,1", "AppleTV6,2"]

for dev in devices:
    try:
        req = urllib.request.Request(
            f"https://api.ipsw.me/v4/device/{dev}?type=ipsw",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.load(r)
        firms = d.get('firmwares', [])
        if firms:
            print(f"\n{dev} firmwares:")
            for f in firms[:3]:
                print(f"  {f['version']} {f['buildid']} {f['url'][:100]}")
            print(f"IPSW_DEVICE={dev}")
            print(f"IPSW_URL={firms[0]['url']}")
            break
    except Exception as e:
        print(f"{dev}: {e}")
