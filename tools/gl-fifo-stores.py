#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["capstone", "pyelftools"]
# ///
"""gl-fifo-stores.py ELF PROCS [64] : per function, the tracked stores to the FIFO window, grouped into commands.
A command = a run of stores to one non-data slot followed by the data-port (slot 479) stores that follow.
Prints "function<TAB>slot<TAB>words". Straight-line reading of a function body: a loop gives a lower bound, branches
that store on different paths add up, and consecutive stores to one slot count as one command (a repeated dispatch
shows as a multiple). PROCS is retools/tools/mdebug.py --procs output when its addresses are absolute (5.3 and 6.5 n32),
or one "address<TAB>name" line per exported function otherwise. The optional 64 reads MIPS-III (n32) code."""
import sys, collections
from elftools.elf.elffile import ELFFile
from capstone import *
from capstone.mips import *
elf = ELFFile(open(sys.argv[1], 'rb'))
procs = sorted((int(l.split('\t')[0], 16), l.split('\t')[1].strip()) for l in open(sys.argv[2]) if l.strip())
mode = CS_MODE_MIPS64 if len(sys.argv) > 3 and sys.argv[3] == '64' else CS_MODE_MIPS32
md = Cs(CS_ARCH_MIPS, mode | CS_MODE_BIG_ENDIAN); md.detail = True
text = elf.get_section_by_name('.text'); data = text.data(); base = text['sh_addr']; end = base + len(data)
STORES = {'sw', 'swc1', 'sd', 'sdc1', 'sh', 'sb', 's.s', 'usw', 'swl', 'swr'}
out = collections.defaultdict(list)
for i, (addr, name) in enumerate(procs):
    if not base <= addr < end: continue
    nxt = procs[i + 1][0] if i + 1 < len(procs) else end
    regs = {}; seq = []
    for ins in md.disasm(data[addr - base:nxt - base], addr):
        m = ins.mnemonic; ops = ins.operands
        rn = lambda o: ins.reg_name(o.reg)
        try:
            if m == 'lui': regs[rn(ops[0])] = ops[1].imm << 16
            elif m in ('ori', 'addiu', 'addi', 'daddiu') and len(ops) == 3:
                s = 0 if rn(ops[1]) == 'zero' else regs.get(rn(ops[1]))
                if s is None: regs.pop(rn(ops[0]), None)
                else: regs[rn(ops[0])] = ((s | ops[2].imm) if m == 'ori' else (s + ops[2].imm)) & 0xffffffff
            elif m == 'move' and len(ops) == 2:
                s = regs.get(rn(ops[1]))
                if s is None: regs.pop(rn(ops[0]), None)
                else: regs[rn(ops[0])] = s
            elif m in STORES and len(ops) >= 2 and ops[1].type == MIPS_OP_MEM:
                b = ins.reg_name(ops[1].mem.base)
                if b in regs:
                    a = (regs[b] + ops[1].mem.disp) & 0xffffffff
                    if 0x40000 <= a < 0x60000: seq.append((a >> 2) & 0x1ff)
            elif ops and ops[0].type == MIPS_OP_REG and not m.startswith(('b', 'j', 's', 'm', 'n')):
                regs.pop(rn(ops[0]), None)
            if m in ('jal', 'jalr', 'bal'):
                for k in ('v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','t8','t9'): regs.pop(k, None)
        except Exception: pass
    # group
    cmds = []; cur = None
    for sl in seq:
        if sl == 479 and cur is not None: cur[1] += 1
        elif cur is not None and sl == cur[0]: cur[1] += 1
        else:
            cur = [sl, 1]; cmds.append(cur)
    for sl, n in cmds: print(f"{name}\t{sl}\t{n}")
