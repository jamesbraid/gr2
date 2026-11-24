#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Step the control flow of a GE7 routine, and check the diagnostic program's known answers.

  ge7-step.py step IMG START [--take A,B,..] [--limit N]   walk from START; one line per branch, RE3 write, immediate or stall
  ge7-step.py paths IMG FROM TO --avoid A,B,..             every taken/not-taken assignment of the cond 1-8 branches that
                                                           reaches TO from FROM without executing an --avoid word
  ge7-step.py run IMG START [--slot N=V,..] [--steps N] [--bus V]
                                                           data-flow run of one engine: RAM0 input slots, the image's constants block,
                                                           branches resolved from the decoded flags; prints RE writes and shared stores
  ge7-step.py selftest IDE [PROM [GE7 [HQ2 [PROM4.0.5G]]]]              regression: the diagnostic known answers, and with the 4.0.5D PROM the console tokens,
                                                           with the full ge7.bin the statistics over all words, with the full hq2.bin the routine starts

Sequencer model (platforms/express/microcode.md): C0[15:0] target or shared-RAM address, C0[21:16] control, C0[25:22] condition.
`step` and `paths` treat a word with condition 1-8 and a target as a conditional jump (taken only if listed in --take) and do not
model data. Condition 10 with no target stops (the stall). Every other word, whatever its control value, falls through to the next
address (a 0x31 or 0x32 word carries an address, not a target). `run` models the data path (class Engine below) and resolves the
branches from the decoded flags. Prints field values and data results only, never a listing.
"""
import importlib.util, itertools, math, struct, sys
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

# ---- data path (platforms/express/microcode.md, "The data path") --------------------------------------------------------
M32 = 0xffffffff
ADDR = (0x11, 0x12, 0x13, 0x31, 0x32, 0x33)       # controls whose C0[15:0] loads the store address counter (bit 21 does not matter)
# The tables the host expects of SeedRomTest and SqRomTest (closed forms, `selftest` checks the program's copies against them).
SEED = [min(127, round(128 * (2 / (1 + i / 128) - 1))) for i in range(128)]
SQRT = [math.floor(256 * (1 / math.sqrt(2 * (1 + i / 64)) - .5)) if i < 64 else min(127, math.floor(256 * (1 / math.sqrt(1 + (i - 64) / 64) - .5))) for i in range(128)]
S32 = lambda v: (v & M32) - (1 << 32) if v & 0x80000000 else v & M32
f2b = lambda f: struct.unpack('>I', struct.pack('>f', f))[0]
b2f = lambda b: struct.unpack('>f', struct.pack('>I', b & M32))[0]

def constants(d):
    """The 500-word constants block of an image (loaded to shared RAM word 0); ALUA = 5 on a 0x3f word reads word C0[15:0] of it."""
    return list(struct.unpack('>500I', d[0xfc:0xfc + 2000]))

def alu(fn, a, b, cnt=0):
    """ALU function number -> (result, flags). Flags are the three the diagnostic program tests: zero, neg and pass, plus eq
    (A == B, the compare flag the dispatch code uses). neg is the sign of the value the function selects or passes before any final
    negate or absolute value (the adders: the sign of the result); pass is set when that value is the B operand."""
    a, b = a & M32, b & M32
    fa, fb = b2f(a), b2f(b)
    pick = None                                    # (value, from_b): functions that select or pass an operand
    n = ALU.get(fn)
    if n in ('IPASSA', 'INEGA', 'IABSA', 'FPASSA', 'FNEGA', 'FABSA', 'FLOATA', 'FIXA', 'NOTA'): pick = (a, False)
    elif n in ('IPASSB', 'INEGB', 'IABSB', 'FPASSB', 'FNEGB', 'FABSB', 'FLOATB', 'FIXB'): pick = (b, True)
    elif n in ('IMIN', 'IMAX', 'IMINABS', 'IMAXABS', 'FMIN', 'FMAX', 'FMINABS', 'FMAXABS'):
        fl = n[0] == 'F'
        x, y = (fa, fb) if fl else (S32(a), S32(b))
        if n.endswith('ABS'): x, y = abs(x), abs(y)
        useb = y < x if 'MIN' in n else y > x
        pick = (b, True) if useb else (a, False)
    T = {'IADD': lambda: a + b, 'ISUB': lambda: a - b, 'IRSUB': lambda: b - a, 'IPASSA': lambda: a, 'IPASSB': lambda: b,
         'INEGA': lambda: -a, 'INEGB': lambda: -b, 'IABSA': lambda: abs(S32(a)), 'IABSB': lambda: abs(S32(b)),
         'NOTA': lambda: ~a, 'AND': lambda: a & b, 'OR': lambda: a | b, 'XOR': lambda: a ^ b, 'ANDNOTB': lambda: a & ~b,
         'ANDNOTA': lambda: ~a & b, 'ORNOTB': lambda: a | ~b, 'ORNOTA': lambda: ~a | b,
         'SLLBR': lambda: a << (cnt & 31), 'SLRBR': lambda: a >> (cnt & 31), 'SARBR': lambda: S32(a) >> (cnt & 31),
         'FPASSA': lambda: a, 'FPASSB': lambda: b, 'FNEGA': lambda: a ^ 0x80000000, 'FNEGB': lambda: b ^ 0x80000000,
         'FABSA': lambda: a & 0x7fffffff, 'FABSB': lambda: b & 0x7fffffff,
         'FADD': lambda: f2b(fa + fb), 'FSUB': lambda: f2b(fa - fb), 'FRSUB': lambda: f2b(fb - fa),
         'FLOATA': lambda: f2b(float(S32(a))), 'FLOATB': lambda: f2b(float(S32(b))),
         'FIXA': lambda: int(fa) if abs(fa) < 2 ** 31 else 0, 'FIXB': lambda: int(fb) if abs(fb) < 2 ** 31 else 0}
    f = T.get(n)
    r = (pick[0] if pick and n[1:4] in ('MIN', 'MAX') else f() if f else pick[0] if pick else 0) & M32
    neg = (pick[0] if pick else r) >> 31 & 1
    return r, dict(zero=(r & 0x7fffffff == 0) if n[0] == 'F' else r == 0, neg=bool(neg), pas=bool(pick and pick[1]), eq=a == b)

def mult(op, a, b):
    """Multiplier: FMPYOP 0 IMPY, 1 FMPY, 2 MPASSA, 3 MPASSB -> result and its flags (zero, neg)."""
    r = {0: lambda: S32(a) * S32(b), 1: lambda: f2b(b2f(a) * b2f(b)), 2: lambda: a, 3: lambda: b}[op]() & M32
    return r, dict(mzero=r & 0x7fffffff == 0 if op == 1 else r == 0, mneg=bool(r >> 31))

# BRCOND -> the line a conditional branch tests, as far as the known answers fix it (microcode.md, "Flags and conditions"). The lines
# are active low except 0x62: a branch (conditions 3, 4, 7, 8) is taken when the line is high. Others raise KeyError.
LINES = {0x62: lambda f: f['eq'], 0x64: lambda f: not f['zero'], 0x63: lambda f: not f['neg'], 0x6b: lambda f: not f['pas'],
         0x68: lambda f: not f['mneg'], 0x69: lambda f: not f['mzero']}

class Engine:
    """One geometry engine's data path, enough to run the diagnostic known answers and the console routines.

    Source selects (ALUA / ALUB): 0 RAM0[RAM0AD], 1 RAM1[RAM1AD], 3 register REGC / REGD, 4 and 6 the previous word's result, 5 the constants
    block word C0[15:0] on a control 0x3f word and the state word (`state`, a second namespace) at C0[15:0] or the address counter on any other
    control, 7 the multiplier output of the previous word (MPASSA of RAM0[RAM0AD] when the word does not multiply). Multiplier selects MPYA: 0 RAM0,
    1 RAM1, 3 REGA, 4 the same word as ALUA = 5; MPYB: 0, 1, 3 REGB, 4 the seed ROM and 5 the square-root ROM, addressed by the value of REGB.
    Writes: REGWR takes the previous word's result, a store (SHFTSRC = 3) and an RE write (FIFOEN) take the result two words back. Branches:
    conditions 1 and 5 always, 2 and 6 never, 3, 4, 7 and 8 when the selected line (LINES) of the word two back is high.
    """
    HELD = False                                   # select 4 as a register held by RESEN (a reading the known answers do not exclude)
    ZERO4 = False                                  # select 4 as the constant zero (likewise)
    MPYB6 = 'alu'                                  # multiplier B select 6: 'alu' the previous ALU result, 'mult' the previous multiplier output

    def __init__(self, M, const, slots=None, bus=0):
        self.M, self.sh, self.ram0, self.ram1, self.bus = M, dict(enumerate(const)), dict(slots or {}), {}, bus
        self.state, self.held = {}, 0
        self.regs, self.hist, self.re, self.stores, self.addr = [0] * 16, [], [], [], 0

    @staticmethod
    def rom(sel, rb):
        """Multiplier B select 4 / 5: the seed / square-root ROM output, addressed by REGB: seven mantissa bits 22:16, or the exponent
        low bit and six mantissa bits (bits 23:17). The value sits in bits 22:16; the other bits are not fixed by any known answer."""
        return (SEED[rb >> 16 & 0x7f] if sel == 4 else SQRT[rb >> 17 & 0x7f]) << 16

    def src(self, d, sel, side):
        h = self.hist
        return {0: lambda: self.ram0.get(d['ram0'], 0), 1: lambda: self.ram1.get(d['ram1'], 0),
                3: lambda: self.regs[d['regc' if side == 'A' else 'regd']], 4: lambda: (0 if self.ZERO4 else self.held if self.HELD else h[-1][0] if h else 0),
                5: lambda: self.sh.get(d['tgt'], 0) if d['ctl'] == 0x3f else self.state.get(d['tgt'] or self.addr, 0), 6: lambda: h[-1][0] if h else 0,
                7: lambda: h[-1][2] if h else 0}.get(sel, lambda: 0)()

    def run(self, a, steps=400, force=None):
        """Run from word a. force maps a branch word (conditions 3, 4, 7, 8) to a taken flag and replaces the decoded line."""
        stalled = False; self.seq = []
        for _ in range(steps):
            if a not in self.M: break
            w = self.M[a]; d = dec(w)
            d.update(ram0=field(w, 24, 7), ram1=field(w, 31, 6), regc=field(w, 8, 4), regd=field(w, 12, 4), rega=field(w, 0, 4), regb=field(w, 4, 4),
                     regwr=field(w, 20, 4), regf=field(w, 86, 2), brc=field(w, 51, 8), shft=field(w, 84, 2), busel=field(w, 71, 1),
                     mop=field(w, 43, 2), mpya=field(w, 59, 3), mpyb=field(w, 62, 3), alua=field(w, 65, 3), alub=field(w, 68, 3),
                     ram1dest=field(w, 77, 3), resen=field(w, 73, 1))
            h = self.hist
            if d['ctl'] in ADDR and d['tgt']: self.addr = d['tgt']
            A, B = self.src(d, d['alua'], 'A'), self.src(d, d['alub'], 'B')
            r, fl = alu(d['alu'], A, B, d['brc'])
            fl.update(lt=S32(A) < S32(B), gt=S32(A) > S32(B))
            ma = {0: self.ram0.get(d['ram0'], 0), 1: self.ram1.get(d['ram1'], 0), 3: self.regs[d['rega']],
                  4: self.sh.get(d['tgt'], 0) if d['ctl'] == 0x3f else self.state.get(d['tgt'] or self.addr, 0),
                  6: h[-1][0] if h else 0, 7: h[-1][2] if h else 0}.get(d['mpya'], 0)
            rb = self.regs[d['regb']]
            mb = {0: self.ram0.get(d['ram0'], 0), 1: self.ram1.get(d['ram1'], 0), 3: rb, 4: self.rom(4, rb), 5: self.rom(5, rb),
                  6: (h[-1][0] if self.MPYB6 == 'alu' else h[-1][2]) if h else 0, 7: h[-1][2] if h else 0}.get(d['mpyb'], 0)
            mr, mf = mult(d['mop'], ma, mb); fl.update(mf)
            if d['busel']: r = mr if d['mpya'] or d['mpyb'] else self.bus
            if d['regf'] == 3 and h: self.regs[d['regwr']] = h[-1][0]
            if d['re'] is not None and len(h) > 1: self.re.append((a, d['re'], h[-2][0]))
            if d['shft'] == 3 and len(h) > 1: self.stores.append((a, self.addr, h[-2][0])); self.state[self.addr] = h[-2][0]; self.addr += 1
            if d['ram1dest'] == 1: self.ram1[d['ram1']] = self.ram0.get(d['ram0'], 0)
            h.append((r, fl, mr)); self.seq.append(a)
            if d['resen']: self.held = r
            if stalled: return
            c = d['cond']
            if c == 10 and not d['tgt']: stalled = True
            take = c in (1, 5) or (c in (3, 4, 7, 8) and (force[a] if force else len(h) > 2 and LINES[d['brc']](h[-3][1])))
            a = d['tgt'] if 1 <= c <= 8 and take else a + 1

def ints(s): return {int(x, 0) for x in s.split(',') if x}

def selftest(ide, prom=None, full=None, hq=None, promg=None):
    D = ide.read_bytes()
    gb = [i for _, i in find_images(D) if U['H'](i, 0) == 0x966e]
    diagb = max(gb, key=len)
    diag, C = load(diagb), constants(diagb)
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
    check('GeSeq: the BRCOND 0x60 branches 1383, 1400, 1407 (straight to the tail at 1438, past the shared store) are never taken',
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
    check('ALUB is never 5 (ALUA = 5 is the shared-word select)', all(field(w, 68, 3) != 5 for w in diag.values()))
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
    check('FpuCond: the constants index loaded before each of %d tests is the function number plus 27 (%d multiplier tests 16..19)' % (len(fn), len(nmul)),
          all(f == alu or 16 <= f <= 19 for _, f, alu in fn) and sorted(nmul) == [16, 17, 18, 19] and len(fn) == 45)
    # ALUA = 5 on a 0x3f word reads shared word C0[15:0], which the loader filled from the image's constants block: the "function + 27" is the
    # index, and the constant at it is the function number itself.
    check('constants block: the word at each of the %d function-number loads is the function number' % len(fn), all(C[f + 27] == f for _, f, _ in fn))
    check('constants block: the three failure-flag loads (words 1571 to 1573) hold 0x100, 0x200, 0x400, the flag index << 8 the host decodes',
          [C[dec(diag[a])['tgt']] for a in (1571, 1572, 1573)] == [0x100, 0x200, 0x400])
    check('constants block: GeSeqTest register 1 = C[0x1c] = 1; SeedRom and SqRom loop counts C[0x5d] = 128 (host stride 128)', C[0x1c] == 1 and C[0x5d] == 128
          and dec(diag[918])['tgt'] == dec(diag[934])['tgt'] == 0x5d)
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
    # Select 7 in Ram12Test's OR chain: each A = 7, B = 6 word follows an ISUB, so 7 is the previous OR two words back and 6 the difference.
    chain = [a for a in range(396, 914) if a in diag and field(diag[a], 65, 3) == 7 and field(diag[a], 68, 3) == 6]
    check('Ram12Test: %d OR words with ALUA = 7, ALUB = 6 each follow an ISUB (the accumulator is two words back)' % len(chain),
          len(chain) == 154 and all(dec(diag[a - 1])['alu'] == 41 for a in chain))
    # SeedRom and SqRom run the same words; the multiplier B select is the only field that differs beside constants indices, shift counts and targets.
    mb = [(916 + k, field(diag[916 + k], 62, 3), field(diag[932 + k], 62, 3)) for k in range(16) if field(diag[916 + k], 62, 3) != field(diag[932 + k], 62, 3)]
    check('SeedRom and SqRom differ in the multiplier B select only, at word 923: %s (the two ROM outputs)' % mb, mb == [(923, 4, 5)])
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
        # The control field says how C0[15:0] is used. 0x3f: an index into the constants block (253 entries in use); 0x31: a small shared-RAM
        # address; 0x32 and 0x33: a wide shared-RAM address (below 0x8000 words = 128 KiB), never with a condition; 0x34: a one-hot code.
        f3f = [dec(w)['tgt'] for w in F.values() if dec(w)['ctl'] == 0x3f and dec(w)['tgt']]
        w32 = [w for w in F.values() if dec(w)['ctl'] == 0x32]
        t32 = [dec(w)['tgt'] for w in w32]
        check('full ge7.bin: %d nonzero 0x3f fields all below 0xfc (max %#x); %d control 0x32 words, fields below 0x8000 (max %#x), %d not records, none with a condition'
              % (len(f3f), max(f3f), len(w32), max(t32), sum(t not in F for t in t32)),
              max(f3f) < 0xfc and len(w32) == 99 and max(t32) < 0x8000 and sum(t not in F for t in t32) == 8 and not any(dec(w)['cond'] for w in w32))
        u = [w for w in F.values() if dec(w)['ctl'] == 0x3f and dec(w)['tgt'] and not dec(w)['imm']]
        check('full ge7.bin: %d control 0x3f words carry a field that ALUA does not read; all have MPYA = 4' % len(u), len(u) == 556 and all(field(w, 59, 3) == 4 for w in u))
        w34 = [dec(w)['tgt'] for w in F.values() if dec(w)['ctl'] == 0x34]
        check('full ge7.bin: control 0x34 fields (%d words) are one-hot codes %s' % (len(w34), sorted(set(w34))), sorted(set(w34)) == [2, 4, 8, 16] and len(w34) == 81)
        # Every routine ends at a condition-10 stall: a routine start sits two words after a stall in 167 of 263 distinct HQ2 starts, and 251 of 263
        # reach a stall by falling through.
        if hq:
            Hq = {a: w[0] for a, _, w, _ in U['records'](hq.read_bytes())[2]}
            starts = sorted({w & 0xffff for w in Hq.values() if w >> 16 == 0xd8})
            st = lambda a: a in F and dec(F[a])['cond'] == 10 and not dec(F[a])['tgt']
            def fall(a):
                while a in F and not st(a) and a < 40000: a += 1
                return st(a)
            check('hq2.bin: %d distinct GE7 starts; %d sit two words after a stall; %d reach a stall by falling through' % (
                  len(starts), sum(st(a - 2) for a in starts), sum(fall(a) for a in starts)),
                  len(starts) == 263 and sum(st(a - 2) for a in starts) == 167 and sum(fall(a) for a in starts) == 251)
    # ---- data path (class Engine): the known answers run on the decoded model ----------------------------------------------------
    def eng(M, K, a, slots=None, steps=400, **kw):
        e = Engine(M, K, slots, **kw); e.run(a, steps); return e
    # FloatOps: x, y, operation in RAM0 slots 0..2; the dispatch (cond 7 on the equal flag, two words back) picks the arm and the
    # store takes the result two words back; IMPY keeps the low 24 bits only on the host side.
    ft = lambda f: struct.unpack('>I', struct.pack('>f', f))[0]
    cases = {1: (8, 3, 11), 2: (8, 3, 5), 3: (12, 13, 156), 4: (ft(1.5), ft(2.25), ft(3.75)), 5: (ft(2.25), ft(1.5), ft(0.75)), 6: (ft(1.5), ft(2.25), ft(3.375))}
    res = {op: eng(diag, C, 1533, {0: x, 1: y, 2: op}).stores for op, (x, y, _) in cases.items()}
    check('FloatOps data path: the six operations return 8+3, 8-3, 12*13, 1.5+2.25, 2.25-1.5, 1.5*2.25 in one store at 1550',
          all(res[op] == [(1550, 0, cases[op][2])] for op in cases))
    # FpuCond: 336 words with the decoded flags (zero, neg, pass, multiplier zero and neg; every cond 8 taken when its flag is clear):
    # no failure writer runs, the only store is the failure count 0 at 1899. 92 of 92 branches not taken.
    e = eng(diag, C, 1562)
    check('FpuCond data path: all 92 cond 8 tests leave their line low (zero 0x64, neg 0x63, pass 0x6b, multiplier 0x69/0x68); stores %s' % e.stores,
          e.stores == [(1899, 0, 0)] and len(e.hist) == 338)
    # SeedRom and SqRom: the loop (cond 7 on BRCOND 0x64, back to its head) runs 128 passes, one store each, the host's stride; the table values
    # themselves come from the ROM path, which the Engine does not model.
    sr, sq = eng(diag, C, 917, steps=2000), eng(diag, C, 933, steps=2000)
    check('SeedRom and SqRom data path: the loops run %d and %d passes, one store each (the host stride is 128)' % (len(sr.stores), len(sq.stores)),
          len(sr.stores) == len(sq.stores) == 128)
    # GeFifoTest: the five host words become a ten-pixel span: x start, y and x end biased by 0x800 and shifted left 11, colour words shifted.
    e = eng(diag, C, 989, {1: 100, 2: 150, 5: 255, 6: 0, 7: 0})
    want = [(0, 0x8000), (8, 0), (0x20, (100 + 0x800) << 11), (0x21, (150 + 0x800) << 11), (0x22, (110 + 0x800) << 11), (0x40, 255 << 11), (0x41, 0), (0x5f, 2), (0x42, 0)]
    check('GeFifoTest data path: RE writes %s; x end - x start = %d pixels' % ([(hex(a), hex(v)) for a, v in want[:5]], (want[4][1] - want[2][1]) >> 11),
          [(a, v) for _, a, v in e.re] == want and (want[4][1] - want[2][1]) >> 11 == 10)
    check('GeFifoTest constants: C[0x62] = 0x800 (bias), C[0x25] = 10 (span length), C[0x1d] = 2 (the value written to 0x5f)', C[0x62] == 0x800 and C[0x25] == 10 and C[0x1d] == 2)
    if prom:
        pb = U['cut'](prom.read_bytes(), 0x4a6f4); P5, PK = load(pb), constants(pb)
        e = Engine(P5, PK, {0: 100, 1: 200}); e.state[0x1d] = 0x112233; e.run(58)
        r = {a: v for _, a, v in e.re}
        check('PNT2I data path: RE 0x20 = x and 0x21 = y biased by 0x800 and shifted left 11, 0x5f = 2, 0x40 = the stored colour shifted left 11',
              r[0x20] == (100 + 0x800) << 11 and r[0x21] == (200 + 0x800) << 11 and r[0x5f] == 2 and r[0x40] == (0x112233 << 11) & 0xffffffff and r[0] == 0x8000 and r[8] == 0)
        e = eng(P5, PK, 51, {0: 0xabcdef}, bus=0xabcdef)
        e2 = eng(P5, PK, 107, {0: 100, 1: 200})
        check('COLOR stores the host word at shared 0x1d; CMOV2I stores x, y at 0x3c, 0x3d (the words DRAWCHAR reads back)', e.stores == [(57, 0x1d, 0xabcdef)] and e2.stores == [(113, 0x3c, 100), (114, 0x3d, 200)])
        ri, rd = {a: v for _, a, v in eng(P5, PK, 10, {0: 0}).re}, {a: v for _, a, v in eng(diag, C, 3, {0: 0}).re}
        com = [0x60, 0x61, 0x62, 0x64, 0x6d, 0x66, 0x72, 0x73, 0x74] + [a for a in range(0x46, 0x56) if a in ri]
        check('INIT writes the same value in both builds at %d of 0x60 to 0x74 and 0x46 to 0x55 (%s ...), though its constants-block indices differ by 0x2d'
              % (sum(ri.get(a) == rd.get(a) for a in com), ', '.join('%02x=%x' % (a, ri[a]) for a in (0x64, 0x66, 0x6d, 0x72, 0x73, 0x74))),
              all(ri.get(a) == rd.get(a) for a in com) and len(com) >= 9)
        nz = sorted(a for a in ri if ri[a] and ri[a] == rd.get(a))
        check('INIT: %d of the written values agree and are non-zero (%s); 0x6d, 0x73 and 0x74 do not fit a 16-bit immediate' % (len(nz), ' '.join('%02x' % a for a in nz)),
              nz == [0x60, 0x64, 0x66, 0x6d, 0x72, 0x73, 0x74] and all(ri[a] > 0xffff for a in (0x6d, 0x73, 0x74)))
    # ---- second pass (platforms/express/microcode.md, "The data path"): select 7, the ROM selects, the state namespace, branch senses ----
    class Sel7Back(Engine):                          # control: select 7 is the ALU result two words back
        def src(self, d, sel, side):
            return (self.hist[-2][0] if len(self.hist) > 1 else 0) if sel == 7 else super().src(d, sel, side)
    class SwapRom(Engine):                           # control: the two ROM selects exchanged
        rom = staticmethod(lambda sel, rb: Engine.rom(9 - sel, rb))
    class ShiftRom(Engine):                          # control: the seed ROM addressed one bit lower
        rom = staticmethod(lambda sel, rb: Engine.rom(sel, rb >> 1 if sel == 4 else rb))
    ti = D.find(struct.pack('>3I', 0x7f, 0x7e, 0x7c)); host = [list(struct.unpack('>128I', D[ti + o:ti + o + 512])) for o in (0, 512)]
    for cls, nm, fits in ((Engine, 'model', True), (Sel7Back, 'control, select 7 two words back', False), (SwapRom, 'control, ROM selects exchanged', False),
                          (ShiftRom, 'control, seed ROM address one bit low', False)):
        got = []
        for start in (917, 933):
            e = cls(diag, C); e.run(start, 2000); got.append([v for _, _, v in e.stores])
        check('SeedRom and SqRom data path, %s: the 128 + 128 stored words %s the host\'s tables' % (nm, 'equal' if fits else 'differ from'), (got == host) == fits)
    seqval = lambda e, a: e.hist[e.seq.index(a)][0]
    if prom:
        for xs, ys in (((150, 100), (200, 260)), ((100, 150), (260, 200))):
            e = Engine(P5, PK, {0: xs[0], 1: ys[0], 2: xs[1], 3: ys[1]}); e.run(69, 60)
            check('RECTI2D x = %s, y = %s: words 70, 73, 77, 80 (IMIN, IMAX, IMAX, IMIN) give xmin, xmax, ymax, ymin (select 7 = the multiplier pass of the RAM0 word)' % (xs, ys),
                  [seqval(e, a) for a in (70, 73, 77, 80)] == [min(xs), max(xs), max(ys), min(ys)])
        e = Sel7Back(P5, PK, {0: 150, 1: 200, 2: 100, 3: 260}); e.run(69, 60)
        check('RECTI2D with select 7 two words back does not give xmin (control)', seqval(e, 70) != 100)
        # RECTI2D separates select 4 = previous result from select 4 = register held by RESEN: with the first each RE3 value depends on one coordinate.
        def rdeps(held):
            cls = type('E', (Engine,), {'HELD': held}); base = {0: 100, 1: 200, 2: 150, 3: 260}
            def res(sl):
                e = cls(P5, PK, sl); e.state[0x1d] = 0x112233; e.run(69, 60); return [(a, v) for _, a, v in e.re]
            b = res(base)
            return b, {k: sorted(hex(a) for (a, x), (_, y) in zip(b, res({**base, k: base[k] + 7})) if x != y) for k in range(4)}
        b, dp = rdeps(False); b2, dh = rdeps(True)
        check('RECTI2D, select 4 = previous result: x1 -> 0x08 0x20, y1 -> 0x23 0x24, x2 -> 0x21, y2 -> 0x25; as a RESEN-held register y2 reaches %s' % dh[3],
              dp == {0: ['0x20', '0x8'], 1: ['0x23', '0x24'], 2: ['0x21'], 3: ['0x25']} and len(dh[3]) == 3)
        v = dict(b)
        check('RECTI2D values: 0x20 = 200.0, 0x21 = 300.0 | 1, 0x25 = 520.0, 0x24 = 0x23 = 398.0, 0x00 = 0x5f = 0, 0x08 = 100 (floats are twice xmin, xmax, ymax and ymin - 1)',
              (b2f(v[0x20]), v[0x21], b2f(v[0x25]), b2f(v[0x24]), v[0x24] == v[0x23], v[0], v[0x5f], v[8]) == (200.0, f2b(300.0) | 1, 520.0, 398.0, True, 0, 0, 100))
    check('Ram12Test: each of the %d ALUA = 7 words follows an ISUB word with multiplier A select 6 and MPASSA (the multiplier passes the OR accumulator on)' % len(chain),
          all(field(diag[a - 1], 59, 3) == 6 and field(diag[a - 1], 43, 2) == 2 for a in chain))
    # GeSeqTest's BRCOND 0x60 and 0x62 branches of conditions 3, 4 and 8 follow the same ISUB x - x pattern and see identical ALU flags at stages 0 to 2,
    # yet cond 3 must fire on 0x62 and none of the other five must. No truth value per line and polarity per condition fits.
    want = {1369: 1, 1375: 1, 1383: 0, 1387: 1, 1394: 0, 1396: 0, 1400: 0, 1403: 0, 1407: 0, 1410: 0, 1412: 1, 1423: 1, 1431: 1}
    g = Engine(diag, C); g.run(1354, 200, force=want)
    check('GeSeq forced path: the 13 outcomes of the table end at 1441 and store once, at 1421', g.seq[-1] == 1441 and [x[0] for x in g.stores] == [1421])
    vec = lambda a, k: (lambda f: (f['eq'], f['zero'], f['neg'], f['lt'], f['gt']))(g.hist[g.seq.index(a) - k][1])
    same = all(len({vec(a, k) for a in grp}) == 1 for grp in ((1383, 1400, 1407), (1387, 1403, 1410)) for k in range(3))
    sol = [(l60, l62, p3, p4, p8) for l60, l62, p3, p4, p8 in itertools.product((0, 1), repeat=5)
           if l60 != p3 and l62 == p3 and l60 != p8 and l62 != p8 and l60 != p4 and l62 != p4]
    check('GeSeq: 1383, 1400, 1407 (conds 3, 8, 4 on 0x60) and 1387, 1403, 1410 (on 0x62) have identical eq / zero / neg / lt / gt flags at stages 0 to 2, and no line value '
          'with condition polarity fits the outcomes (%d solutions)' % len(sol), same and not sol)
    if full:
        K = constants(full.read_bytes())
        st, rd = {}, {}
        for a, w in F.items():
            d = dec(w)
            if d['ctl'] in (0x11, 0x12, 0x13) and d['tgt'] and field(w, 84, 2) == 3: st.setdefault(d['tgt'], []).append(a)
            if d['ctl'] == 0x3f and d['tgt'] and (d['imm'] or field(w, 59, 3) == 4): rd.setdefault(d['tgt'], []).append(a)
        both = sorted(set(st) & set(rd))
        check('state namespace: %d store words with an explicit address (control 0x11 to 0x13, SHFTSRC 3) name %d addresses, %d also read as constants through control 0x3f '
              '(K[0x41] = 0.5: %d reads, %d stores; K[0x8d] = 5: %d reads, %d stores; K[0x3d]: %d reads, %d stores)'
              % (sum(map(len, st.values())), len(st), len(both), len(rd[0x41]), len(st[0x41]), len(rd[0x8d]), len(st[0x8d]), len(rd[0x3d]), len(st[0x3d])),
              (sum(map(len, st.values())), len(st), len(both)) == (293, 126, 44) and K[0x41] == 0x3f000000 and K[0x8d] == 5
              and (len(rd[0x41]), len(st[0x41]), len(rd[0x8d]), len(st[0x8d]), len(rd[0x3d]), len(st[0x3d])) == (111, 1, 66, 55, 17, 6))
    # ---- seventh pass: the pixel-DMA routines (host side: pix_dma, gr2_shramre3dma, gr2_stridedma, gr2_re3dma) --------------------------------------------
    # The host sends the direction flag and x0, y0, x1, y1 (HQ2 slots 9, 11, 56 read them into RAM0 slots 8, 1, 2, 3, 4), then a DMA descriptor whose length
    # is (x1 - x0 + 1) words by (y1 - y0 + 1) rows. The three routines (GE7 1208, 1294, 1250) form width * height with IMPY (REGA times the previous ALU result,
    # MPYA = 3, MPYB = 6) and take it back through select 7 (IRSUB with 1: width * height - 1) as the count they store. Host cases: gr2_shramre3dma moves 1024
    # words into the 32 x 32 rectangle (100, 100) to (131, 131), gr2_stridedma's first phase 441 (0x1b9) words into (10, 10) to (30, 30), gr2_re3dma one row of 0x500.
    dma = ((1208, 1234), (1294, 1320), (1250, 1277))
    host = (((100, 100, 131, 131), 1024), ((10, 10, 30, 30), 441), ((0, 37, 0x4ff, 37), 0x500), ((7, 3, 20, 12), 14 * 10))
    def count(cls, st, wd, rect, flag=1):
        e = cls(diag, C); e.ram0 = {8: flag, 1: rect[0], 2: rect[1], 3: rect[2], 4: rect[3]}; e.run(st, 120)
        return [v for w, _, v in e.stores if w == wd], e
    class MultB(Engine): MPYB6 = 'mult'
    # The same routine's RE3 writes put the host rectangle at 0x20 (x0), 0x21 (x1, bit 0 set), 0x24 (y0 - 1) and 0x25 (y1), each biased by 0x800 and shifted left 11; the flag only picks 0x67
    # (0x180000 for flag 1, a write; 0x100000 for flag 0, a readback; 0x67 is cleared at the end) and the path (1243 or 1236). The host's pixel compare puts the rectangle there, so this is the edge-register role of the rectangle.
    def rect_re(flag, r, cls=Engine):
        e = cls(diag, C); e.ram0 = {8: flag, 1: r[0], 2: r[1], 3: r[2], 4: r[3]}; e.run(1208, 120); d = {}; [d.setdefault(a, v) for _, a, v in e.re]; return d, e.seq
    bias = lambda v: (v + 0x800) << 11
    rr, sq = rect_re(1, (100, 200, 131, 231)); rw, sw = rect_re(0, (100, 200, 131, 231))
    check('pixel DMA 1208: RE3 0x20 = x0, 0x21 = x1 | 1, 0x24 = y0 - 1, 0x25 = y1 (biased, << 11), 0x23 = 0x200000; flag 1 sets 0x67 to 0x180000 and takes 1243, flag 0 sets 0x100000 and takes 1236',
          all(r[a] == v for r in (rr, rw) for a, v in ((0x20, bias(100)), (0x21, bias(131) | 1), (0x24, bias(199)), (0x25, bias(231)), (0x23, 0x200000)))
          and (rr[0x67], rw[0x67]) == (0x180000, 0x100000) and 1243 in sq and 1236 not in sq and 1236 in sw and 1243 not in sw)
    ok_n = {cls.__name__: sum(count(cls, st, wd, r)[0][:1] == [n - 1] for st, wd in dma for r, n in host) for cls in (Engine, MultB)}
    check('DMA routines 1208, 1294, 1250: the stored count is width * height - 1 for the host rectangles (%d of %d); with multiplier B select 6 as the previous multiplier output it is right in %d'
          % (ok_n['Engine'], len(dma) * len(host), ok_n['MultB']), ok_n['Engine'] == 12 and ok_n['MultB'] == 0)
    e = count(Engine, 1294, 1320, host[0][0])[1]
    check('DMA routine 1294: the word stored after the count is C[0xee] = 0xff, the shared word where the host put the 1024 words (gr2_shramre3dma fills words 255 on)',
          [(w, v) for w, _, v in e.stores] == [(1320, 0x3ff), (1321, 0xff)] and C[0xee] == 0xff)
    mpy = [(a, field(diag[a + 1], 68, 3), field(diag[a], 59, 3), field(diag[a], 62, 3), field(diag[a], 43, 2)) for a in (1231, 1274, 1317)]
    check('DMA routines: the multiply words 1231, 1274, 1317 are IMPY with MPYA = 3, MPYB = 6 and the next word reads select 7: %s' % mpy, all(m[1:] == (7, 3, 6, 0) for m in mpy))
    # Select 4: three readings (previous ALU result, a register held by RESEN, the constant zero) pass the same known answers.
    def known(cls):
        r = {op: cls(diag, C, {0: x, 1: y, 2: op}) for op, (x, y, _) in cases.items()}
        for op, e in r.items(): e.run(1533, 400)
        o = [e.stores == [(1550, 0, cases[op][2])] for op, e in r.items()]
        e = cls(diag, C); e.run(1562, 400); o.append(e.stores == [(1899, 0, 0)] and len(e.hist) == 338)
        got = []
        for start in (917, 933):
            e = cls(diag, C); e.run(start, 2000); got.append([v for _, _, v in e.stores])
        o.append(got == host_tables)
        e = cls(diag, C, {1: 100, 2: 150, 5: 255, 6: 0, 7: 0}); e.run(989, 400)
        o.append([(a, v) for _, a, v in e.re] == [(0, 0x8000), (8, 0), (0x20, (100 + 0x800) << 11), (0x21, (150 + 0x800) << 11), (0x22, (110 + 0x800) << 11), (0x40, 255 << 11), (0x41, 0), (0x5f, 2), (0x42, 0)])
        for st, wd in dma: o.append(count(cls, st, wd, host[0][0])[0][:1] == [1023])
        return all(o)
    host_tables = [list(struct.unpack('>128I', D[ti + o:ti + o + 512])) for o in (0, 512)]
    class Held4(Engine): HELD = True
    class Zero4(Engine): ZERO4 = True
    check('select 4 as the previous ALU result, as a RESEN-held register and as the constant zero all pass the known answers (FloatOps, FpuCond, SeedRom, SqRom, GeFifoTest, the DMA counts)',
          known(Engine) and known(Held4) and known(Zero4))
    if prom:
        e = Engine(P5, PK, {8: 1, 1: 100, 2: 200, 3: 131, 4: 231}); e.run(245, 120)
        check('console image: the pixel-DMA routine at 245 (the same words as GE7 1294) stores the count 1023 for the 32 x 32 rectangle', [v for w, _, v in e.stores] == [0x3ff] and e.seq.index(268) < e.seq.index(271))
        zr = {}
        e = Zero4(P5, PK, {0: 100, 1: 200, 2: 150, 3: 260}); e.state[0x1d] = 0x112233; e.run(69, 60); zr = {a: v for _, a, v in e.re}
        check('RECTI2D with select 4 = zero: 0x20 = 100.0 (xmin), 0x21 = 150.0 | 1 (xmax), 0x25 = 260.0 (ymax), 0x24 = 199.0 (ymin - 1), 0x23 = 0.0: the pixel-DMA routine\'s edge registers, as floats, with no doubling',
              (b2f(zr[0x20]), zr[0x21], b2f(zr[0x25]), b2f(zr[0x24]), zr[0x23]) == (100.0, f2b(150.0) | 1, 260.0, 199.0, 0))
    if full and hq:
        Hq2 = {a: w[0] for a, _, w, _ in U['records'](hq.read_bytes())[2]}
        st2 = sorted({w & 0xffff for w in Hq2.values() if w >> 16 == 0xd8})
        def lead(a):                                  # the first word of a routine that reads select 4 for real work, with no RESEN word before it
            res = False
            for _ in range(60):
                d = dec(F[a]) if a in F else None
                if d is None or (d['cond'] == 10 and not d['tgt']): return False
                w = F[a]
                if not (dec(w)['alu'] == 4 and field(w, 65, 3) == 4 and field(w, 68, 3) == 4) and (field(w, 65, 3) == 4 or field(w, 68, 3) == 4): return not res
                res |= bool(field(w, 73, 1))
                if 1 <= d['cond'] <= 8 and d['tgt']: return False
                a += 1
            return False
        n4 = sum(lead(a) for a in st2)
        check('full ge7.bin: %d of %d HQ2 routine starts read select 4 for real work before any RESEN word, so under a held register or a previous result '
              'they depend on what ran before (history-dependent); the zero reading that would avoid this is refuted below' % (n4, len(st2)), (n4, len(st2)) == (185, 263))
    # ---- eighth pass: the right edge of the pixel-DMA routines and the Z-plane DMA (host: gr2_chkzplanes, pix_dma_zb, the 4.0.5G PROM's copy of pix_dma) ----
    # Each routine computes ((x1 + 0x800) << 11) | 1, parks it in register 15 and reads it back later; the read word's result reaches the RE3 write 0x21 only
    # through select 4. With select 4 as the constant zero that value is lost: 0x21 = 0 whatever x1 is, and no RE3 write depends on x1.
    def dwrites(cls, st, flag, x1):
        e = cls(diag, C); e.ram0 = {8: flag, 1: 100, 2: 100, 3: x1, 4: 131}; e.run(st, 120)
        return {a: v for _, a, v in e.re}, e
    rd15 = lambda w: any(field(w, a, 3) == 3 and field(w, b, 4) == 15 for a, b in ((65, 8), (68, 12)))
    wr15 = lambda w: field(w, 20, 4) == 15 and field(w, 86, 2) == 3
    shape = [([a for a in range(st, st + 45) if wr15(diag[a])], [a for a in range(st, st + 45) if rd15(diag[a])]) for st, _ in dma]
    check('DMA routines 1208, 1250, 1294: register 15 is written once (start + 17) and read once (start + 26) in each of 1208, 1294, 1250: %s' % shape,
          shape == [([1225], [1234]), ([1311], [1321]), ([1268], [1277])])
    edge = {}
    for nm, cls in (('previous', Engine), ('held', Held4), ('zero', Zero4)):
        edge[nm] = [(dwrites(cls, st, fl, 131)[0][0x21], dwrites(cls, st, fl, 131)[0] == dwrites(cls, st, fl, 140)[0]) for st, _ in dma for fl in (1, 0)]
    check('DMA routines, both flags: 0x21 = ((x1 + 0x800) << 11) | 1 and moves with x1 under select 4 = previous result and = RESEN-held register; as the constant zero 0x21 = 0 and no RE3 write depends on x1 '
          '(the right edge never reaches RE3: the zero reading is refuted for these routines)',
          all(v == bias(131) | 1 and not same for nm in ('previous', 'held') for v, same in edge[nm]) and all(v == 0 and same for v, same in edge['zero']))
    # 1250 (HQ2 slot 56, the host's pix_dma_zb) sets RE3 0x6b to the constant C[0x1d] = 2 before the transfer. The host's gr2_chkzplanes sends 1 to slot 52 (+0x400d0) before writing
    # Z rows and 0 after, and 2 to slot 53 (+0x400d4) before reading them back and 0 after; the slot 52 routine (GE7 1161) and slot 53 routine (GE7 1199) take that word from the bus.
    def tok(st, v):
        e = Engine(diag, C, {0: v}, bus=v); e.run(st, 60); return {a: x for _, a, x in e.re}
    t52, t52z, t53, t53z = tok(1161, 1), tok(1161, 0), tok(1199, 2), tok(1199, 0)
    check('Z-plane tokens: slot 52 with 1 writes 0x60 = 0, 0x61 = 0xffffffff, 0x65 = 0x40, 0x66 = 0; with 0 the pair swaps (0x60 = 0xffffffff, 0x61 = 0) and 0x65 = 0; slot 53 writes 0x6b = the host word (2, then 0)',
          (t52[0x60], t52[0x61], t52[0x65], t52[0x66]) == (0, 0xffffffff, 0x40, 0) and (t52z[0x60], t52z[0x61], t52z[0x65]) == (0xffffffff, 0, 0) and (t53[0x6b], t53z[0x6b]) == (2, 0) and C[0x1d] == 2)
    z1, z0 = (dwrites(Engine, 1250, fl, 131)[1] for fl in (1, 0))
    zz = dwrites(Zero4, 1250, 0, 131)[1]
    sixb = lambda e: [v for _, a, v in e.re if a == 0x6b]
    check('GE7 1250: RE3 0x6b = 2 first; at the end 0 on the write path (flag 1) and, on the readback path (flag 0), the right-edge word 0x441801 for select 4 = previous result (0 for zero)', sixb(z1) == [2, 0] and sixb(z0) == [2, bias(131) | 1] and sixb(zz) == [2, 0])
    # The 4.0.5G PROM carries the diagnostic's pix_dma as an unreferenced "CPU to bitplanes DMA test" (0xbfc066e8): rows of 256 words at y = 0 and y = 1023, written with
    # a1 = 0 (flag 1) and read back with a1 = 2 (flag 0), sent through slot 9, which its own console image does not handle. Its console images are the 4.0.5D ones.
    if prom and promg:
        pg = promg.read_bytes()
        same = U['cut'](pg, 0x4d294) == U['cut'](prom.read_bytes(), 0x49840) and U['cut'](pg, 0x4e148) == pb
        ok2 = True
        for y in (0, 1023):
            for fl in (1, 0):
                e = Engine(P5, PK, {8: fl, 1: 0, 2: y, 3: 255, 4: y}); e.run(245, 120)
                r = {a: v for _, a, v in e.re}
                ok2 &= ([v for _, _, v in e.stores] == [255] and r[0x20] == bias(0) and r[0x21] == bias(255) | 1 and r[0x24] == bias(y - 1) & M32 and r[0x25] == bias(y) and r[0x67] == 0)
        check('PROM 4.0.5G: its two console images equal the 4.0.5D ones; its pix_dma rows (0, y) to (255, y) at y = 0 and 1023 give the count 255 and the same edge registers on the console routine at 245 (y0 - 1 = -1 wraps in the bias)',
              same and ok2)
    return ok

def main():
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == 'selftest':
        sys.exit(0 if selftest(*[Path(x) for x in a[:5]]) else 1)
    M = load(open(a[0], 'rb').read())
    opt = lambda k, dflt='': a[a.index(k) + 1] if k in a else dflt
    if cmd == 'run':
        e = Engine(M, constants(open(a[0], 'rb').read()), {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in opt('--slot').split(',') if x)}, int(opt('--bus', '0'), 0))
        e.run(int(a[1]), int(opt('--steps', 400)))
        for w, ad, v in e.re: print('%d re %#04x %#010x' % (w, ad, v))
        for w, ad, v in e.stores: print('%d store %#06x %#010x' % (w, ad, v))
        return
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
