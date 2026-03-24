import zipfile, sys

try:
    z = zipfile.ZipFile('partial.ipsw')
    for n in sorted(z.namelist()):
        print(n)
except Exception as e:
    print('zip error:', e)
    # Try reading raw bytes to identify format
    with open('partial.ipsw', 'rb') as f:
        hdr = f.read(16)
    print('header hex:', hdr.hex())
    print('header:', hdr)
