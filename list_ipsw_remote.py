import sys, struct, urllib.request

url = sys.argv[1]
total_size = int(sys.argv[2])

def fetch_range(start, end):
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

# Fetch last 128KB to find EOCD + Zip64 locator
print("Fetching last 128KB...")
tail = fetch_range(total_size - 131072, total_size - 1)

# Find Zip64 EOCD Locator (PK\x06\x07)
Z64_LOC_SIG = b'\x50\x4b\x06\x07'
loc_pos = tail.rfind(Z64_LOC_SIG)

if loc_pos != -1:
    print("Found ZIP64 locator")
    # Parse locator: sig(4) disk(4) z64_eocd_offset(8) total_disks(4)
    _, disk, z64_offset, total_disks = struct.unpack('<IQII', tail[loc_pos:loc_pos+20])
    print(f"ZIP64 EOCD at offset: {z64_offset}")

    # Fetch Zip64 EOCD record
    z64_eocd_data = fetch_range(z64_offset, z64_offset + 100)
    # sig(4) size(8) ver_made(2) ver_needed(2) disk(4) cd_start_disk(4) 
    # num_entries_disk(8) num_entries(8) cd_size(8) cd_offset(8)
    sig, rec_size, ver_made, ver_needed, disk_num, cd_disk, num_disk, num_total, cd_size, cd_offset = struct.unpack('<IQHHIIQQQQ', z64_eocd_data[:56])
    print(f"Files: {num_total}, CD at offset {cd_offset} ({cd_size} bytes)")
else:
    # Standard EOCD
    EOCD_SIG = b'\x50\x4b\x05\x06'
    pos = tail.rfind(EOCD_SIG)
    _, disk, start_disk, num_recs, total_recs, cd_size, cd_offset, comment_len = struct.unpack('<IHHHHIIH', tail[pos:pos+22])
    print(f"Standard ZIP: Files={total_recs}, CD at offset {cd_offset} ({cd_size} bytes)")
    num_total = total_recs

# Fetch and parse central directory
print(f"Fetching central directory ({cd_size} bytes)...")
cd_data = fetch_range(cd_offset, cd_offset + cd_size - 1)

offset = 0
files = []
while offset < len(cd_data):
    if cd_data[offset:offset+4] != b'\x50\x4b\x01\x02':
        break
    # Standard CD header (46 bytes)
    fields = struct.unpack('<IHHHHHHIIIHHHHHI', cd_data[offset:offset+46])
    sig, ver_made, ver_needed, flags, compression, mod_time, mod_date, crc32, comp_size, uncomp_size, fname_len, extra_len, comment_len, disk_start, int_attr, ext_attr, local_offset = fields
    fname = cd_data[offset+46:offset+46+fname_len].decode('utf-8', errors='replace')
    extra = cd_data[offset+46+fname_len:offset+46+fname_len+extra_len]

    # Handle ZIP64 extra fields (tag 0x0001)
    e_off = 0
    while e_off + 4 <= len(extra):
        tag, size = struct.unpack('<HH', extra[e_off:e_off+4])
        if tag == 0x0001:
            vals = []
            pos2 = e_off + 4
            if uncomp_size == 0xFFFFFFFF and pos2 + 8 <= e_off + 4 + size:
                uncomp_size = struct.unpack('<Q', extra[pos2:pos2+8])[0]; pos2 += 8
            if comp_size == 0xFFFFFFFF and pos2 + 8 <= e_off + 4 + size:
                comp_size = struct.unpack('<Q', extra[pos2:pos2+8])[0]; pos2 += 8
            if local_offset == 0xFFFFFFFF and pos2 + 8 <= e_off + 4 + size:
                local_offset = struct.unpack('<Q', extra[pos2:pos2+8])[0]; pos2 += 8
        e_off += 4 + size

    files.append((fname, uncomp_size, comp_size, local_offset))
    offset += 46 + fname_len + extra_len + comment_len

print(f"\nParsed {len(files)} files:")
with open('ipsw_files.txt', 'w') as f:
    for name, usize, csize, loff in sorted(files):
        gb = usize / 1024**3
        line = f"{name}  {gb:.2f}GB  comp={csize//1024//1024}MB  offset={loff}"
        print(line)
        f.write(line + '\n')
