#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Check and read the GR2 microcode images (hq2.bin, ge7.bin, or the PROM-embedded copies).

  ucode-decode.py info IMG            header, record count, checksum check, GE7 field statistics
  ucode-decode.py hq2 IMG [SLOT...]   follow the HQ2 words from FIFO slots (default: console slots 401-409, 417-419)
  ucode-decode.py cut PROM OFFSET OUT cut an embedded image out of a PROM (HQ2 0x49840, GE7 0x4a6f4 in 4.0.5D)
  ucode-decode.py ide IDE [OUTDIR]    find the microcode images embedded in the ide.IP20 diagnostic program (writes them to OUTDIR)
  ucode-decode.py fields IMG START [N] GE7 field values of N (default 8) words from START, by the field map in microcode.md
  ucode-decode.py alu IMG             histogram of the GE7 ALU function field, named from the diagnostic program's table

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

# GE7 microword fields: (name, lowest bit, width), bit 0 = C4[0] ... bit 95 = C2[31], bits 96-102 = C1[6:0].
FIELDS = [('REGA', 0, 4), ('REGB', 4, 4), ('REGC', 8, 4), ('REGD', 12, 4), ('REGE', 16, 4), ('REGWR', 20, 4),
          ('RAM0AD', 24, 7), ('RAM1AD', 31, 6), ('RAM2AD', 37, 6), ('FMPYOP', 43, 2), ('FALUOP', 45, 6),
          ('BRCOND', 51, 8), ('MPYA', 59, 3), ('MPYB', 62, 3), ('ALUA', 65, 3), ('ALUB', 68, 3), ('BUSEL', 71, 1),
          ('REGSEL', 72, 1), ('RESEN', 73, 1), ('RAM0DEST', 74, 3), ('RAM1DEST', 77, 3), ('RAM2DEST', 80, 3),
          ('MISCSRC', 83, 1), ('SHFTSRC', 84, 2), ('REGFDEST', 86, 2), ('DSEL', 88, 2), ('QSAM', 90, 1),
          ('TSAM', 91, 1), ('VPSAM', 92, 1), ('LSAM', 93, 1), ('FIFOEN', 94, 1), ('READDR', 95, 8)]
# ALU function names, as printed by the diagnostic program's floating-point condition test (function number -> name).
ALU = {3: 'FADD', 4: 'FPASSA', 5: 'FNEGA', 6: 'FPASSB', 7: 'FNEGB', 8: 'FSUB', 9: 'FRSUB', 10: 'FMIN', 11: 'FMAX',
       12: 'FLOATA', 13: 'FLOATB', 14: 'FIXA', 15: 'FIXB', 16: 'IMPY', 17: 'FMPY', 18: 'MPASSA', 19: 'MPASSB',
       20: 'FABSA', 22: 'FABSB', 30: 'FMINABS', 31: 'FMAXABS', 32: 'NOTA', 33: 'AND', 34: 'OR', 35: 'XOR',
       36: 'ANDNOTB', 37: 'ANDNOTA', 38: 'ORNOTB', 39: 'ORNOTA', 40: 'IADD', 41: 'ISUB', 42: 'IRSUB', 44: 'SLRREG',
       45: 'SARREG', 46: 'SLLREG', 48: 'IMIN', 49: 'IMINABS', 50: 'IMAX', 51: 'IMAXABS', 52: 'IPASSA', 53: 'INEGA',
       54: 'IABSA', 55: 'IPASSB', 56: 'INEGB', 57: 'IABSB', 60: 'SLRBR', 61: 'SARBR', 62: 'SLLBR'}

def bits(w):
    return (w[1] & 0x7f) << 96 | w[2] << 64 | w[3] << 32 | w[4]

def field(w, lo, n):
    return (bits(w) >> lo) & ((1 << n) - 1)

def find_images(d):
    """Images embedded in a program: a 966e/965e magic, version 1, the 0x1c text offset, then a sane record table."""
    out = []
    for m in (b'\x96\x6e\x00\x01\x00\x00\x00\x1c', b'\x96\x5e\x00\x01\x00\x00\x00\x1c'):
        i = d.find(m)
        while i >= 0:
            try:
                out.append((i, d[i:i + records(d[i:])[1]]))
            except Exception:
                pass
            i = d.find(m, i + 1)
    return sorted(out)

def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'cut':
        open(args[2], 'wb').write(cut(open(args[0], 'rb').read(), int(args[1], 0))); return
    if cmd == 'ide':
        d = open(args[0], 'rb').read()
        for off, img in find_images(d):
            rl, end, R = records(img)
            print('offset %#x magic %04x records %d addr %d..%d size %d %s' % (off, H(img, 0), len(R), R[0][0], R[-1][0], end,
                  'GE7' if H(img, 0) == 0x966e else 'HQ2'))
            if len(args) > 1:
                open('%s/%s-%x.bin' % (args[1], 'ge7' if H(img, 0) == 0x966e else 'hq2', off), 'wb').write(img)
        return
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
    elif cmd == 'fields':
        M = {a: w for a, _, w, _ in R}
        n = int(args[2]) if len(args) > 2 else 8
        for a in range(int(args[1]), int(args[1]) + n):
            if a in M:
                w = M[a]
                f = ' '.join('%s=%x' % (k, field(w, lo, wd)) for k, lo, wd in FIELDS if field(w, lo, wd))
                print('%d: C0=%08x cond=%d ctl=%02x tgt=%04x %s' % (a, w[0], w[0] >> 22, (w[0] >> 16) & 0x3f, w[0] & 0xffff, f))
    elif cmd == 'alu':
        c = Counter(field(w, 45, 6) for _, _, w, _ in R)
        print(' '.join('%s:%d' % (ALU.get(k, k), v) for k, v in c.most_common()))
    elif cmd == 'hq2':
        M = {a: w[0] for a, _, w, _ in R}
        for s in map(int, args[1:]) or list(range(401, 410)) + [417, 418, 419]:
            print(s, walk(M, s) if s in M else 'none')

main()
