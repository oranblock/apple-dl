import sys, struct, urllib.request

url = sys.argv[1]
total_size = int(sys.argv[2])

def fetch_range(start, end):
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

# Fetch last 128KB
print("Fetching ZIP tail...")
tail = fetch_range(total_size - 131072, total_size - 1)

# Step 1: Find standard EOCD (always last signature before comment)
EOCD_SIG = b'\x50\x4b\x05\x06'
eocd_pos = tail.rfind(EOCD_SIG)
if eocd_pos == -1:
    print("No EOCD found"); sys.exit(1)

# Step 2: Check if ZIP64 — locator is exactly 20 bytes before EOCD
Z64_LOC_SIG = b'\x50\x4b\x06\x07'
loc_pos = eocd_pos - 20
cd_offset = cd_size = num_total = 0

if loc_pos >= 0 and tail[loc_pos:loc_pos+4] == Z64_LOC_SIG:
    print("ZIP64 format detected")
    # Locator: sig(4) disk(4) z64_eocd_offset(8) total_disks(4)
    _, disk, z64_off, ndisks = struct.unpack('<IQII', tail[loc_pos:loc_pos+20])
    print(f"ZIP64 EOCD record at file offset: {z64_off}")
    # Fetch ZIP64 EOCD record (56 bytes minimum)
    z64 = fetch_range(z64_off, z64_off + 55)
    sig, rec_size, ver_made, ver_needed, d_num, cd_disk, n_disk, n_total, cd_size, cd_offset = struct.unpack('<IQHHIIQQQQ', z64[:56])
    num_total = n_total
    print(f"Files: {num_total}, CD at {cd_offset} ({cd_size//1024}KB)")
else:
    print("Standard ZIP32")
    _, disk, sd, num_recs, total_recs, cd_size, cd_offset, cl = struct.unpack('<IHHHHIIH', tail[eocd_pos:eocd_pos+22])
    num_total = total_recs
    print(f"Files: {num_total}, CD at {cd_offset} ({cd_size//1024}KB)")

# Fetch central directory
print(f"Fetching central directory...")
cd_data = fetch_range(cd_offset, cd_offset + cd_size - 1)

offset = 0
files = []
while offset + 46 <= len(cd_data):
    if cd_data[offset:offset+4] != b'\x50\x4b\x01\x02':
        break
    sig, vm, vn, flags, comp, mt, md, crc, csize, usize, fnl, exl, cml, ds, ia, ea, loff = struct.unpack('<IHHHHHHIIIHHHHHI', cd_data[offset:offset+46])
    fname = cd_data[offset+46:offset+46+fnl].decode('utf-8', errors='replace')
    extra = cd_data[offset+46+fnl:offset+46+fnl+exl]

    # Parse ZIP64 extra
    e = 0
    while e + 4 <= len(extra):
        tag, esz = struct.unpack('<HH', extra[e:e+4]); p = e+4
        if tag == 0x0001:
            if usize == 0xFFFFFFFF and p+8 <= e+4+esz: usize = struct.unpack('<Q', extra[p:p+8])[0]; p+=8
            if csize == 0xFFFFFFFF and p+8 <= e+4+esz: csize = struct.unpack('<Q', extra[p:p+8])[0]; p+=8
            if loff == 0xFFFFFFFF and p+8 <= e+4+esz: loff = struct.unpack('<Q', extra[p:p+8])[0]; p+=8
        e += 4 + esz

    files.append((fname, usize, csize, loff))
    offset += 46 + fnl + exl + cml

print(f"\n=== {len(files)} files in IPSW ===")
with open('ipsw_files.txt', 'w') as f:
    for name, usize, csize, loff in sorted(files):
        line = f"{usize//1024//1024:8}MB  {name}  (offset={loff})"
        print(line); f.write(line+'\n')
