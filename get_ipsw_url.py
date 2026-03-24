import json, urllib.request

req = urllib.request.Request(
    "https://api.ipsw.me/v4/device/AppleTV14,1",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req) as r:
    d = json.load(r)

firms = d.get('firmwares', [])
print("Available firmwares:")
for f in firms[:5]:
    print(f['version'], f['buildid'], f['url'][:80])

# Print first URL on its own line for shell capture
if firms:
    print("IPSW_URL=" + firms[0]['url'])
