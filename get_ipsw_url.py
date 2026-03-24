import urllib.request, plistlib, io

print("Fetching mesu catalog...")
req = urllib.request.Request(
    "https://mesu.apple.com/assets/com_apple_MobileAsset_SoftwareUpdate/com_apple_MobileAsset_SoftwareUpdate.xml",
    headers={"User-Agent": "AppleTV14,1/17.4 CFNetwork/1494"}
)
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()

print(f"Total size: {len(data)} bytes")
plist = plistlib.loads(data)
assets = plist.get('Assets', [])
print(f"Total assets: {len(assets)}")

# Find Apple TV assets
for a in assets:
    board = a.get('BoardID', '') or a.get('SupportedDeviceModels', [])
    compat = a.get('SupportedDevices', []) or []
    if any('AppleTV' in str(x) for x in [board] + compat):
        ver = a.get('OSVersion', '')
        build = a.get('Build', '')
        url_key = a.get('__RelativePath', '')
        base = a.get('__BaseURL', '')
        print(f"  ATV: {compat} v{ver} build={build}")
        print(f"  URL: {base}{url_key}")
        print(f"  Size: {a.get('_DownloadSize', '?')}")
        print()
