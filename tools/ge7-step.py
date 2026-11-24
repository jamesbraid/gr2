#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Step the control flow of a GE7 routine, and check the diagnostic program's known answers.

  ge7-step.py step IMG START [--take A,B,..] [--limit N]   walk from START; one line per branch, RE3 write, immediate or stall
  ge7-step.py paths IMG FROM TO --avoid A,B,..             every taken/not-taken assignment of the cond 1-8 branches that
                                                           reaches TO from FROM without executing an --avoid word
  ge7-step.py selftest IDE [PROM [GE7]]                    regression: the diagnostic known answers, and with the 4.0.5D PROM the console tokens,
                                                           and with the full ge7.bin the statistics over all words

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
        if d['cond'] == 10 and not d['tgt']: return          # a stall ends the routine
        if 1 <= d['cond'] <= 8:
            for t in (False, True):
                taken[a] = t; go(d['tgt'] if t else a + 1, taken, seen)
            del taken[a]
        else: go(a + 1, taken, seen)
    go(a, {}, frozenset())
    return out

def ints(s): return {int(x, 0) for x in s.split(',') if x}

def selftest(ide, prom, full=None):
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
    check('GeSeq: %d outcome sets reach the end word 1450 (each leaves by an early exit, so none passes the test)' % len(P), len(P) == 4)
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
    # GeSeqTest again: a passing run ends with the shared-RAM store of the value 1 (word 1421: cond 15, SHFTSRC 3, after
    # IPASSA of register 1 at 1419). Exactly one assignment reaches it, and it takes none of the four early exits.
    stores = [a for a in range(1354, 1456) if a in diag and field(diag[a], 84, 2) == 3 and dec(diag[a])['cond'] == 15]
    check('GeSeq: the only shared store is at %s' % stores, stores == [1421])
    P1 = paths(diag, 1368, 1421, fail)
    want = {1369: 1, 1375: 1, 1383: 0, 1387: 1, 1394: 0, 1396: 0, 1400: 0, 1403: 0, 1407: 0, 1410: 0, 1412: 1}
    check('GeSeq: one outcome set reaches the shared store, with the exits 1394/1396/1403/1410 not taken',
          len(P1) == 1 and {k: int(v) for k, v in P1[0].items()} == want)
    P2 = paths(diag, 1368, 1436, fail)
    check('GeSeq: and the same set continues to 1436 with 1423 and 1431 taken',
          len(P2) == 1 and P2[0].get(1423) and P2[0].get(1431) and len(P2[0]) == 13)
    bad = [a for a in sorted(diag) if 1 <= dec(diag[a])['cond'] <= 8 and bool(field(diag[a], 51, 8)) != (dec(diag[a])['cond'] in (3, 4, 7, 8))]
    check('conds 3, 4, 7, 8 always carry a BRCOND value and conds 1, 2, 5, 6 none (diagnostic image; exceptions %s)' % bad, not bad)
    # Shared-RAM window: SHFTSRC = 3 words from a cond 14 word to the next cond 15 word are the engine's stores; their count is
    # the per-engine stride the host program uses (shared word 255 + stride * n + i).
    def window(a):
        n = 0
        for x in range(a, a + 600):
            if x in diag and field(diag[x], 84, 2) == 3: n += 1
            if x in diag and dec(diag[x])['cond'] == 15: return x, n
    for a, stride, nm in ((389, 1, 'ShramTest'), (396, 6, 'Ram12Test'), (974, 10, 'GeBusTest'), (1418, 1, 'GeSeqTest'), (1549, 1, 'FloatOps')):
        check('%s: stores between cond 14 at %d and cond 15 = host stride %d (%s)' % (nm, a, stride, window(a)), window(a)[1] == stride)
    # FpuCondTest (HQ2 slot 57, GE7 1562): every branch is cond 8 into one of three failure writers, and the word before each
    # test loads (function number + 27); the multiplier tests carry 16 to 19 (IMPY, FMPY, MPASSA, MPASSB).
    br = {a: dec(diag[a]) for a in range(1562, 1898) if a in diag and 1 <= dec(diag[a])['cond'] <= 8}
    pad = {}
    for a in br: pad.setdefault(field(diag[a], 51, 8), set()).add(br[a]['tgt'])
    check('FpuCond: %d branches, all cond 8, BRCOND -> failure writer %s' % (len(br), {hex(k): sorted(v) for k, v in sorted(pad.items())}),
          all(d['cond'] == 8 for d in br.values()) and pad == {0x64: {1900}, 0x69: {1900}, 0x63: {1903}, 0x68: {1903}, 0x6b: {1906}})
    fn = [(a, dec(diag[a])['tgt'] - 27, dec(diag[a + 1 + (field(diag[a + 1], 20, 4) != 12)])['alu']) for a in range(1580, 1897)
          if a in diag and dec(diag[a])['imm'] and field(diag[a], 68, 3) == 4 and dec(diag[a])['alu'] == 52 and not field(diag[a], 20, 4)]
    nmul = [f for _, f, _ in fn if 16 <= f <= 19]
    check('FpuCond: the number loaded before each of %d tests is the ALU function number plus 27 (%d multiplier tests 16..19)' % (len(fn), len(nmul)),
          all(f == alu or 16 <= f <= 19 for _, f, alu in fn) and sorted(nmul) == [16, 17, 18, 19] and len(fn) == 45)
    # BRCOND 0x64 is the zero flag: with register 0 = 0, register 5 = 1 and register 7 = all ones (the values the zero tests force),
    # the operation before every 0x64 branch of the integer and logic part gives zero (16 of 16 that use only those registers).
    S = lambda v: v - (1 << 32) if v >> 31 else v
    OPS = {40: lambda a, b: a + b, 41: lambda a, b: a - b, 42: lambda a, b: b - a, 52: lambda a, b: a, 55: lambda a, b: b,
           53: lambda a, b: -a, 56: lambda a, b: -b, 54: lambda a, b: abs(S(a)), 57: lambda a, b: abs(S(b)), 48: lambda a, b: min(S(a), S(b)),
           50: lambda a, b: max(S(a), S(b)), 49: lambda a, b: a if abs(S(a)) <= abs(S(b)) else b, 51: lambda a, b: a if abs(S(a)) >= abs(S(b)) else b,
           32: lambda a, b: ~a, 33: lambda a, b: a & b, 34: lambda a, b: a | b, 35: lambda a, b: a ^ b, 36: lambda a, b: a & ~b,
           37: lambda a, b: ~a & b, 38: lambda a, b: a | ~b, 39: lambda a, b: ~a | b}
    R = {0: 0, 5: 1, 7: 0xffffffff}
    tested = zero = 0
    for a in range(1694, 1830):
        if a in diag and dec(diag[a])['cond'] == 8 and field(diag[a], 51, 8) == 0x64:
            o = a - 1
            while o in diag and not (field(diag[o], 20, 4) == 12 and not dec(diag[o])['imm']): o -= 1
            w = diag[o]; c, d, f = field(w, 8, 4), field(w, 12, 4), field(w, 45, 6)
            if f in OPS and (field(w, 65, 3) != 3 or c in R) and (field(w, 68, 3) != 3 or d in R):
                tested += 1
                zero += (OPS[f](R.get(c, 0) if field(w, 65, 3) == 3 else 0, R.get(d, 0) if field(w, 68, 3) == 3 else 0) & 0xffffffff) == 0
    check('FpuCond: the operation before each of %d BRCOND 0x64 tests gives zero (%d)' % (tested, zero), tested == 16 and zero == 16)
    # Seed and square-root ROM tables the host expects (32-bit words, 128 each), closed forms.
    import math, struct
    i = D.find(struct.pack('>3I', 0x7f, 0x7e, 0x7c))
    seed = struct.unpack('>128I', D[i:i + 512]); sq = struct.unpack('>128I', D[i + 512:i + 1024])
    check('SeedRom table is round(128 * (2 / (1 + i/128) - 1)) clamped to 127', all(seed[k] == min(127, round(128 * (2 / (1 + k / 128) - 1))) for k in range(128)))
    check('SqRom table is floor(256 * (1/sqrt(m) - 1/2)) with m = 2(1 + i/64) for i < 64, 1 + (i-64)/64 above, clamped to 127',
          all(sq[k] == (math.floor(256 * (1 / math.sqrt(2 * (1 + k / 64)) - .5)) if k < 64 else min(127, math.floor(256 * (1 / math.sqrt(1 + (k - 64) / 64) - .5))))
              for k in range(128)))
    if prom:
        P5 = load(U['cut'](prom.read_bytes(), 0x4a6f4))
        want = {10: 'INIT', 51: 'COLOR', 58: 'PNT2I', 69: 'RECTI2D', 89: 'LINE2I', 107: 'CMOV2I'}
        for s, nm in want.items():
            e, end = step(P5, s)
            check('%s from %d: %d RE3 writes, ends at %s' % (nm, s, sum(x[1] == 're' for x in e), end), end == 'stall')
        f31 = {a: dec(P5[a])['tgt'] for a in P5 if dec(P5[a])['ctl'] == 0x31 and dec(P5[a])['tgt']}
        check('0x31 field: COLOR and CMOV2I (writers) and PNT2I, RECTI2D, LINE2I, DRAWCHAR (readers) use matching values %s' % {a: hex(v) for a, v in sorted(f31.items())},
              f31.get(55) == f31.get(63) == f31.get(84) == f31.get(90) == f31.get(123) == 0x1d and f31.get(112) == f31.get(115) == f31.get(117) == 0x3c and f31.get(116) == 0x3d)
    if full:
        F = load(full.read_bytes())
        cnt = {c: [dec(w)['cond'] for w in F.values()].count(c) for c in range(1, 9)}
        zero = {c: sum(1 for w in F.values() if dec(w)['cond'] == c and not field(w, 51, 8)) for c in range(1, 9)}
        check('full ge7.bin: BRCOND is non-zero on every cond 3, 4, 7, 8 word (%d, %d, %d, %d) and zero on 606 of 659 of the others'
              % tuple(cnt[c] for c in (3, 4, 7, 8)), all(zero[c] == 0 for c in (3, 4, 7, 8)) and sum(zero[c] for c in (1, 2, 5, 6)) == 606
              and sum(cnt[c] for c in (1, 2, 5, 6)) == 659)
        tg = [dec(w)['tgt'] for w in F.values() if 1 <= dec(w)['cond'] <= 8]
        check('full ge7.bin: all %d conditional-branch targets are records' % len(tg), all(t in F for t in tg))
        f = [dec(w)['tgt'] for w in F.values() if dec(w)['ctl'] == 0x31 and dec(w)['tgt']]
        miss = sum(t not in F for t in f)
        check('full ge7.bin: %d of %d non-zero 0x31 fields are not records, so they are not branch targets' % (miss, len(f)), miss == 325 and len(f) == 2144)
        c11 = [w for w in F.values() if dec(w)['cond'] == 11]
        check('full ge7.bin: %d of %d cond 11 words write RE3 address 0x5f (the flush)' % (sum(dec(w)['re'] == 0x5f for w in c11), len(c11)),
              len(c11) == 14 and sum(dec(w)['re'] == 0x5f for w in c11) == 13)
    return ok

def main():
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == 'selftest':
        sys.exit(0 if selftest(Path(a[0]), Path(a[1]) if len(a) > 1 else None, Path(a[2]) if len(a) > 2 else None) else 1)
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
