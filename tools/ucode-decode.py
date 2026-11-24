#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Check and read the GR2 microcode images (hq2.bin, ge7.bin, or the PROM-embedded copies).

  ucode-decode.py info IMG            header, record count, checksum check, GE7 field statistics
  ucode-decode.py hq2 IMG [SLOT...]   follow the HQ2 words from FIFO slots (default: console slots 401-409, 417-419)
  ucode-decode.py cut PROM OFFSET OUT cut an embedded image out of a PROM (HQ2 0x49840, GE7 0x4a6f4 in 4.0.5D)

Prints statistics and per-slot walks only, never a full listing. Format: platforms/express/microcode.md.
"""
import struct, sys
from collections import Counter

W = lambda d, o: struct.unpack('>I', d[o:o+4])[0]
H = lambda d, o: struct.unpack('>H', d[o:o+2])[0]

def records(d):
    rl = ((H(d, 0xf8) + 6) >> 1) * 2
    o, out = W(d, 12), []
    while H(d, o) != 0xffff:
        a, x, t = H(d, o), H(d, o+2), H(d, o+rl-2)
        w = [W(d, o+4+4*i) for i in range((rl-6)//4)]
        out.append((a, x, w, t)); o += rl
    return rl, o + rl, out

def cut(prom, off):
    d = prom[off:]
    return d[:records(d)[1]]

def dis(w):
    op, lo = w >> 16, w & 0xffff
    if op == 0:
        k = lo >> 13
        return {3: 'jump', 4: 'call', 5: 'return'}.get(k, 'branch%d' % k) + ' %d' % (lo & 0x1fff)
    if op in (0x40, 0x60) and lo < 0x400 and not lo & 0x1f:
        return '%s slot%d' % ('read-last' if op == 0x40 else 'read', lo >> 5)
    if op == 0xd8:
        return 'start-ge %d' % lo
    return {0x80: 'ctl80', 0x20: 'op20'}.get(op, 'op%02x' % op) + ' %04x' % lo

def walk(M, s, n=60):
    out, a, seen = [], s, set()
    while a in M and a not in seen and len(out) < n:
        seen.add(a); w = M[a]; out.append('%d:%s' % (a, dis(w)))
        if w >> 16 == 0xd8: break
        a = (w & 0x1fff) if w >> 13 == 3 else a + 1
    return ' ; '.join(out)

def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'cut':
        open(args[2], 'wb').write(cut(open(args[0], 'rb').read(), int(args[1], 0))); return
    d = open(args[0], 'rb').read()
    rl, end, R = records(d)
    if cmd == 'info':
        bad = sum(((a + x + sum(b for v in w for b in v.to_bytes(4, 'big'))) & 0xffff) != t for a, x, w, t in R)
        print('magic %04x ver %d reclen %d records %d addr %d..%d size %d; checksum mismatches %d'
              % (H(d, 0), H(d, 2), rl, len(R), R[0][0], R[-1][0], end, bad))
        if len(R[0][2]) == 5:
            u = [0] * 5
            for _, _, w, _ in R:
                for i in range(5): u[i] |= w[i]
            print('bits used per word:', ' '.join('%08x' % v for v in u))
            A = {a for a, _, _, _ in R}
            seq = Counter(w[0] >> 22 for _, _, w, _ in R)
            print('top w0 bits 25:22 values:', seq.most_common(6))
            B = [(a, w[0] & 0xffff) for a, _, w, _ in R if (w[0] >> 22) and (w[0] >> 22) < 9 and w[0] & 0xffff]
            print('hi4 1..8 targets landing on a record: %d of %d' % (sum(t in A for _, t in B), len(B)))
        else:
            M = {a: w[0] for a, _, w, _ in R}
            print('op (bits 23:16) counts:', sorted(Counter(w >> 16 for w in M.values()).items()))
            j = [(w & 0x1fff) for w in M.values() if w >> 13 == 3 and not w >> 16]
            print('jump targets landing on a record: %d of %d' % (sum(t in M for t in j), len(j)))
    elif cmd == 'hq2':
        M = {a: w[0] for a, _, w, _ in R}
        for s in map(int, args[1:]) or list(range(401, 410)) + [417, 418, 419]:
            print(s, walk(M, s) if s in M else 'none')

main()
