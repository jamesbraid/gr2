#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""One row per FIFO slot that has a first-level HQ2 word, for one or more hq2.bin images.

  hq2-slots.py table LABEL=IMG [LABEL=IMG ...]   markdown table: words and GE7 start per image
  hq2-slots.py classes LABEL=IMG [...]           counts per class
  hq2-slots.py compare IMG HOST.tsv              check the word counts against what a GL core stores (gl-fifo-stores.py output)

Walk (as ucode-decode.py hq2 does): jump words are followed, calls and the type-6/7 branches fall through, and the
walk ends at a start-ge word or at the op20 0x2000 word. Words = number of operand reads on the walk, at least 1
(the token word is always taken): an op 0x40/0x60 word whose operand is a slot form (below 0x400, low five bits
clear), has bits 15:12 equal to 3 or 4, or is 0x2400 to 0x25ff. Inferred reading; the margin and the exceptions are in
platforms/express/microcode.md. Prints field values and slot numbers only, never a listing.
"""
import sys, struct, collections

def load(path):
    d = open(path, 'rb').read()
    H = lambda o: struct.unpack('>H', d[o:o+2])[0]
    W = lambda o: struct.unpack('>I', d[o:o+4])[0]
    rl = ((H(0xf8) + 6) >> 1) * 2
    o, M = W(12), {}
    while H(o) != 0xffff:
        M[H(o)] = W(o + 4); o += rl
    return M

def is_read(op, lo):
    return op in (0x40, 0x60) and ((lo < 0x400 and not lo & 0x1f) or lo >> 12 in (3, 4) or (lo & 0xfe00) == 0x2400)

def walk(M, slot):
    a, seen, reads, cond, ended, ge = slot, set(), 0, False, None, None
    while a in M and a not in seen and len(seen) < 300:
        seen.add(a); w = M[a]; op, lo = w >> 16, w & 0xffff
        reads += is_read(op, lo)
        if op == 0xd8: ended, ge = 'ge', lo; break
        if op == 0x20 and lo == 0x2000: ended = 'end'; break
        if op == 0:
            k = lo >> 13
            if k == 3: a = lo & 0x1fff; continue
            if k in (6, 7): cond = True
        a += 1
    return max(1, reads), cond, ended, ge

def rows(M):
    return {s: walk(M, s) for s in range(512) if s in M}

def compare(img, tsv):
    host = collections.defaultdict(list)
    for l in open(tsv):
        f, s, c = l.rstrip('\n').split('\t'); host[int(s)].append(int(c))
    R, ex, mul, bad = rows(load(img)), 0, 0, []
    for s in sorted(host):
        if s not in R or R[s][1] or R[s][2] != 'ge': continue
        w = R[s][0]
        if all(c == w for c in host[s]): ex += 1
        elif all(c % w == 0 for c in host[s]): mul += 1
        else: bad.append((s, w, sorted(set(host[s]))))
    print(f'{ex + mul + len(bad)} slots with a plain walk that start a GE routine and that the host stores to: '
          f'{ex} equal, {mul} multiples (repeated dispatch), {len(bad)} neither')
    for b in bad: print('  slot %d: image %d, host %s' % b)

def main():
    if sys.argv[1] == 'compare': return compare(sys.argv[2], sys.argv[3])
    cmd, specs = sys.argv[1], [x.split('=', 1) for x in sys.argv[2:]]
    R = {lab: rows(load(p)) for lab, p in specs}
    if cmd == 'classes':
        for lab, r in R.items():
            c = collections.Counter(('conditional' if v[1] else 'plain') + ('/GE start' if v[2] == 'ge' else '/ends without GE') for v in r.values())
            print(lab, len(r), 'slots', dict(c))
        return
    labs = [lab for lab, _ in specs]
    print('| Slot | FIFO offset | ' + ' | '.join(f'{l} words | {l} GE7' for l in labs) + ' | Notes |')
    print('|---|---|' + '---|---|' * len(labs) + '---|')
    for s in sorted(set().union(*R.values())):
        cells, notes = [], []
        for lab in labs:
            v = R[lab].get(s)
            if v is None: cells += ['-', '-']; continue
            w, cond, ended, ge = v
            cells += [str(w) + ('*' if cond else ''), str(ge) if ge is not None else 'ends']
            if cond: notes.append(f'{lab}: conditional branch on the walk')
        print(f'| {s} | `+0x{0x40000 + 4 * s:05x}` | ' + ' | '.join(cells) + ' | ' + '; '.join(notes) + ' |')

main()
