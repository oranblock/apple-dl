import struct

with open('ipsw_tail.bin', 'rb') as f:
    data = f.read()

EOCD_SIG = b'\x50\x4b\x05\x06'
pos = data.rfind(EOCD_SIG)
if pos == -1:
    print('EOCD not found in tail - need larger range')
    print('Tail size:', len(data))
else:
    eocd = data[pos:]
    _, disk, start_disk, num_recs, total_recs, cd_size, cd_offset, comment_len = struct.unpack('<IHHHHIIH', eocd[:22])
    print(f'CD offset: {cd_offset}, size: {cd_size}, records: {total_recs}')
