import json, urllib.request, os

def fetch(url, ua="AppleTV11,1/1 AtVUI"):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read()
    except:
        return None

# Try all known manifest paths
manifest_urls = [
    "https://sylvan.apple.com/Aerials/resources-13.tar",
    "https://sylvan.apple.com/Aerials/2x/entries.json",
    # tvOS 14/15/16 guesses
    "https://sylvan.apple.com/Aerials/resources-14.tar",
    "https://sylvan.apple.com/Aerials/resources-15.tar",
    "https://sylvan.apple.com/Aerials/resources-16.tar",
    "https://sylvan.apple.com/Aerials/resources-17.tar",
    "https://sylvan.apple.com/Aerials/4K/entries.json",
    "https://sylvan.apple.com/Aerials/2x/entries-sdr.json",
]

all_urls = set()
for murl in manifest_urls:
    data = fetch(murl)
    if data:
        size = len(data)
        print(f"OK {size}b: {murl}")
        if murl.endswith('.tar'):
            import tarfile, io
            try:
                tar = tarfile.open(fileobj=io.BytesIO(data))
                for member in tar.getmembers():
                    if member.name.endswith('.json'):
                        content = tar.extractfile(member).read()
                        try:
                            d = json.loads(content)
                            assets = d if isinstance(d, list) else d.get('assets', [])
                            for a in assets:
                                for k,v in (a.items() if isinstance(a, dict) else []):
                                    if isinstance(v, str) and '.mov' in v.lower():
                                        all_urls.add(v)
                        except: pass
            except Exception as e:
                print(f"  tar error: {e}")
        elif murl.endswith('.json'):
            try:
                d = json.loads(data)
                assets = d if isinstance(d, list) else d.get('assets', [])
                for a in assets:
                    for k,v in (a.items() if isinstance(a, dict) else []):
                        if isinstance(v, str) and '.mov' in v.lower():
                            all_urls.add(v)
            except: pass
    else:
        print(f"FAIL: {murl}")

# Also parse local tvos15.json
try:
    with open('tvos15.json') as f:
        d = json.load(f)
    for a in d.get('assets', []):
        for k,v in a.items():
            if isinstance(v, str) and '4K-SDR' in k:
                all_urls.add(v)
except: pass

snoopy = [u for u in all_urls if 'snoopy' in u.lower()]
print(f"\nTotal URLs: {len(all_urls)}")
print(f"Snoopy: {snoopy}")

# Save 4K SDR URLs
sdr_4k = sorted([u for u in all_urls if '4K' in u and 'SDR' in u])
other = sorted([u for u in all_urls if u not in sdr_4k])
with open('urls_4k_sdr.txt', 'w') as f:
    f.write('\n'.join(sdr_4k))
with open('urls_all.txt', 'w') as f:
    f.write('\n'.join(sorted(all_urls)))
print(f"4K SDR: {len(sdr_4k)}")
print(f"Other: {len(other)}")
