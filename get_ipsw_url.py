import urllib.request, plistlib

print("Fetching mesu catalog...")
req = urllib.request.Request(
    "https://mesu.apple.com/assets/com_apple_MobileAsset_SoftwareUpdate/com_apple_MobileAsset_SoftwareUpdate.xml",
    headers={"User-Agent": "AppleTV14,1/17.4 CFNetwork/1494"}
)
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()

plist = plistlib.loads(data)
assets = plist.get('Assets', [])
print(f"Total assets: {len(assets)}")

# Find newest Apple TV 4K assets (AppleTV11,1 = 4K 1st/2nd gen, AppleTV14,1 = 4K 3rd gen)
target_models = {'AppleTV11,1', 'AppleTV14,1', 'AppleTV13,2'}
seen = {}

for a in assets:
    compat = a.get('SupportedDevices', [])
    models = [x for x in compat if x in target_models]
    if not models:
        continue
    ver = a.get('OSVersion', '')
    build = a.get('Build', '')
    key = (tuple(sorted(models)), ver, build)
    if key not in seen:
        seen[key] = a
        base = a.get('__BaseURL', '')
        rel = a.get('__RelativePath', '')
        size = a.get('_DownloadSize', 0)
        print(f"{models} v{ver} build={build} size={size//1024//1024}MB")
        print(f"  {base}{rel}")

# Also check for aerial/wallpaper asset types
print("\n=== Aerial/Wallpaper assets ===")
for a in assets:
    atype = a.get('AssetType', '')
    if 'aerial' in atype.lower() or 'wallpaper' in atype.lower() or 'idle' in atype.lower():
        base = a.get('__BaseURL', '')
        rel = a.get('__RelativePath', '')
        print(f"{atype}: {base}{rel}")
