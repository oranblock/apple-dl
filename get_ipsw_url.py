import urllib.request, plistlib

req = urllib.request.Request(
    "https://mesu.apple.com/assets/com_apple_MobileAsset_SoftwareUpdate/com_apple_MobileAsset_SoftwareUpdate.xml",
    headers={"User-Agent": "AppleTV14,1/17.4 CFNetwork/1494"}
)
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()

plist = plistlib.loads(data)
assets = plist.get('Assets', [])

# Collect all unique ATV models and versions
atv_builds = {}
for a in assets:
    compat = a.get('SupportedDevices', [])
    for dev in compat:
        if 'AppleTV' in dev:
            ver = a.get('OSVersion','?')
            build = a.get('Build','?')
            if dev not in atv_builds:
                atv_builds[dev] = set()
            atv_builds[dev].add((ver, build))

for dev in sorted(atv_builds.keys()):
    builds = sorted(atv_builds[dev], reverse=True)
    print(f"{dev}: {[f'v{v} ({b})' for v,b in builds[:5]]}")

# Find latest AppleTV11,1 or newer OTA
print("\n=== Newest 4K packages ===")
for a in assets:
    compat = a.get('SupportedDevices', [])
    if any(dev in ['AppleTV11,1','AppleTV14,1','AppleTV13,2'] for dev in compat):
        ver = a.get('OSVersion','?')
        build = a.get('Build','?')
        base = a.get('__BaseURL','')
        rel = a.get('__RelativePath','')
        size = a.get('_DownloadSize', 0)
        print(f"{compat} v{ver} {build} {size//1024//1024}MB")
        print(f"  URL: {base}{rel}")
        print(f"IPSW_URL={base}{rel}")
        break
