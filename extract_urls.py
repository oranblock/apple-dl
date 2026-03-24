import json, sys

with open('entries.json') as f:
    groups = json.load(f)

urls = []
for g in groups:
    for a in g.get('assets', []):
        if a.get('type') == 'video':
            urls.append(a['url'] + '  # ' + a.get('accessibilityLabel',''))

with open('all_urls.txt', 'w') as f:
    f.write('\n'.join(urls))

print(f"Total URLs: {len(urls)}")
for u in urls:
    print(u)
