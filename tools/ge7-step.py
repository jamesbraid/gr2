#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Step the control flow of a GE7 routine, and check the diagnostic program's known answers.

  ge7-step.py step IMG START [--take A,B,..] [--limit N]   walk from START; one line per branch, RE3 write, immediate or stall
  ge7-step.py paths IMG FROM TO --avoid A,B,..             every taken/not-taken assignment of the cond 1-8 branches that
                                                           reaches TO from FROM without executing an --avoid word
  ge7-step.py selftest IDE [PROM]                          regression: GeSeqTest, FloatOps and (with the 4.0.5D PROM) the console tokens

Sequencer model (platforms/express/microcode.md): C0[15:0] target/immediate, C0[21:16] control, C0[25:22] condition.
A word with condition 1-8 and a target is a conditional jump (taken only if listed in --take). Condition 10 with no target stops
(the stall). Every other word, whatever its control value, falls through to the next address: a 0x31 word is not followed even
when its target is non-zero, because the known answers need it so (see microcode.md). ALUA = 5 reads the C0 target as an immediate.
Data flow is not modelled. Prints field values only, never a listing.
"""
import importlib.util, itertools, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('ucd', Path(__file__).with_name('ucode-decode.py'))
src = Path(spec.origin).read_text().replace('\nmain()\n', '\n')
U = {}; exec(compile(src, 'ucode-decode', 'exec'), U)
records, field, find_images, ALU = U['records'], U['field'], U['find_images'], U['ALU']

def load(d):
    return {a: w for a, _, w, _ in records(d)[2]}

def dec(w):
    c0 = w[0]
    return dict(cond=c0 >> 22, ctl=(c0 >> 16) & 0x3f, tgt=c0 & 0xffff, imm=field(w, 65, 3) == 5,
                re=field(w, 95, 8) if field(w, 94, 1) else None, alu=field(w, 45, 6))

def step(M, a, take=(), limit=400, quiet=False):
    """Walk from a. Returns (events, end): end is 'stall', 'gap' (no word) or 'limit'."""
    ev, seen = [], set()
    for _ in range(limit):
        if a not in M: return ev, 'gap'
        d = dec(M[a])
        if d['re'] is not None: ev.append((a, 're', d['re']))
        if d['imm']: ev.append((a, 'imm', d['tgt']))
        if 1 <= d['cond'] <= 8:
            t = a in take
            ev.append((a, 'br%d' % d['cond'], t))
            a = d['tgt'] if t else a + 1
            if a in seen and t: return ev, 'loop'
            seen.add(a)
            continue
        if d['cond'] == 10 and not d['tgt']: ev.append((a, 'stall', None)); return ev, 'stall'
        a += 1
    return ev, 'limit'

def paths(M, a, goal, avoid):
    out = []
    def go(a, taken, seen):
        if a == goal: out.append(dict(taken)); return
        if a not in M or a in avoid or a in seen: return
        d = dec(M[a]); seen = seen | {a}
        if 1 <= d['cond'] <= 8:
            for t in (False, True):
                taken[a] = t; go(d['tgt'] if t else a + 1, taken, seen)
            del taken[a]
        else: go(a + 1, taken, seen)
    go(a, {}, frozenset())
    return out

def ints(s): return {int(x, 0) for x in s.split(',') if x}

def selftest(ide, prom):
    D = ide.read_bytes()
    img = {H: m for H, m in ((U['H'](i, 0), i) for _, i in find_images(D))}
    ge = [load(i) for _, i in find_images(D) if U['H'](i, 0) == 0x966e]
    diag = max(ge, key=len)
    ok = True
    def check(name, cond):
        nonlocal ok; ok &= bool(cond); print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    # GeSeqTest (HQ2 slot 12 -> GE7 1354): outcomes of the cond 1-8 branches that reach the final writes at 1450
    # without executing any of the seven failure words (cond 10 plus a RAM0 write).
    fail = {a for a in diag if 1354 <= a <= 1450 and dec(diag[a])['cond'] == 10 and field(diag[a], 74, 3) == 3}
    P = paths(diag, 1368, 1450, fail)
    check('GeSeq: failure words are %s' % sorted(fail), sorted(fail) == [1372, 1379, 1391, 1415, 1427, 1434, 1440])
    check('GeSeq: %d consistent outcome sets' % len(P), len(P) == 4)
    check('GeSeq: 1369 (cond 5), 1375 (cond 1), 1387 (cond 3, BRCOND 0x62) taken, 1383 (cond 3, BRCOND 0x60) not, in every set',
          all(p[1369] and p[1375] and p[1387] and not p[1383] for p in P))
    check('GeSeq: the BRCOND 0x60 branches 1383, 1400, 1407 (into the failure at 1438) are never taken',
          all(not p.get(x, False) for p in P for x in (1383, 1400, 1407)))
    # FloatOps (slot 59 -> 1533): the six dispatch words each reach their arm (1543 + n), every arm reaches the tail, the tail the stall.
    for n in range(6):
        e, end = step(diag, 1533, take={1537 + n, 1543 + n})
        arm = [x for x in e if x[1].startswith('br')]
        check('FloatOps op %d: dispatch %d -> arm %d -> stall at %d' % (n + 1, 1537 + n, 1543 + n, e[-1][0]),
              end == 'stall' and e[-1][0] == 1551 and (1543 + n, 'br5', True) in arm)
    # 0x31 words that must fall through: the first word of routines the host starts, and FloatOps' third word.
    starts = {388, 395, 917, 933, 960, 1535}
    check('0x31 with target 0 is the routine\'s own work word at %s' % sorted(starts),
          all(dec(diag[a])['ctl'] == 0x31 and not dec(diag[a])['tgt'] for a in starts))
    check('ALUB is never 5 (ALUA = 5 is the immediate select)', all(field(w, 68, 3) != 5 for w in diag.values()))
    if prom:
        P5 = load(U['cut'](prom.read_bytes(), 0x4a6f4))
        want = {10: 'INIT', 51: 'COLOR', 58: 'PNT2I', 69: 'RECTI2D', 89: 'LINE2I', 107: 'CMOV2I'}
        for s, nm in want.items():
            e, end = step(P5, s)
            check('%s from %d: %d RE3 writes, ends at %s' % (nm, s, sum(x[1] == 're' for x in e), end), end == 'stall')
    return ok

def main():
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == 'selftest':
        sys.exit(0 if selftest(Path(a[0]), Path(a[1]) if len(a) > 1 else None) else 1)
    M = load(open(a[0], 'rb').read())
    opt = lambda k, dflt='': a[a.index(k) + 1] if k in a else dflt
    if cmd == 'step':
        e, end = step(M, int(a[1]), ints(opt('--take')), int(opt('--limit', 400)))
        for ad, k, v in e:
            print('%d %s %s' % (ad, k, '' if v is None else (hex(v) if k in ('re', 'imm') else v)))
        print('end:', end)
    elif cmd == 'paths':
        P = paths(M, int(a[1]), int(a[2]), ints(opt('--avoid')))
        print(len(P), 'assignments')
        for p in P: print(' '.join('%d=%d' % (k, v) for k, v in sorted(p.items())))

main()
