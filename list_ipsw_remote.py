import sys, struct, urllib.request, io

url = sys.argv[1]
total_size = int(sys.argv[2])

def fetch_range(start, end):
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

# Fetch last 64KB to find EOCD
print("Fetching last 64KB...")
tail = fetch_range(total_size - 65536, total_size - 1)

EOCD_SIG = b'\x50\x4b\x05\x06'
pos = tail.rfind(EOCD_SIG)
if pos == -1:
    print("EOCD not found, trying larger range...")
    tail = fetch_range(total_size - 1048576, total_size - 1)
    pos = tail.rfind(EOCD_SIG)

if pos == -1:
    print("Cannot find ZIP central directory")
    sys.exit(1)

eocd = tail[pos:]
sig, disk, start_disk, num_recs, total_recs, cd_size, cd_offset, comment_len = struct.unpack('<IHHHHIIH', eocd[:22])
print(f"Files: {total_recs}, CD at offset {cd_offset} ({cd_size} bytes)")

# Fetch central directory
print("Fetching central directory...")
cd_data = fetch_range(cd_offset, cd_offset + cd_size - 1)

# Parse entries
offset = 0
files = []
while offset < len(cd_data):
    if cd_data[offset:offset+4] != b'\x50\x4b\x01\x02':
        break
    hdr = cd_data[offset:offset+46]
    _, ver_made, ver_needed, flags, compression, mod_time, mod_date, crc32, comp_size, uncomp_size, fname_len, extra_len, comment_len, disk_start, int_attr, ext_attr, local_offset = struct.unpack('<IHHHHHHIIIHHHHHI', hdr)
    fname = cd_data[offset+46:offset+46+fname_len].decode('utf-8', errors='replace')
    files.append((fname, uncomp_size, comp_size, local_offset))
    offset += 46 + fname_len + extra_len + comment_len

print(f"Parsed {len(files)} files:")
with open('ipsw_files.txt', 'w') as f:
    for name, usize, csize, off in files:
        line = f"{name}  uncompressed={usize}  compressed={csize}  offset={off}"
        print(line)
        f.write(line + '\n')
