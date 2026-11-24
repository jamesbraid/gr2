"""generated from devices/hq2/registers.toml by defs-gen - do not edit, change the source
defs-gen 3
input sha256 6b0209a7be7eb709d083d2295da39a130cc6e09c73033c65727cd369f60a2e2f
HQ2 command engine: FIFO window, microstore and host registers"""

UNIT = 'hq2'
REGISTERS = {'fifo_window': {'offset': 262144, 'access': 'w', 'width': 32, 'count': 32768, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ucode_store': {'offset': 393216, 'access': 'rw', 'width': 32, 'count': 8192, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'attr_jump': {'offset': 434176, 'access': 'rw', 'width': 32, 'count': 16, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'status': {'offset': 434240, 'access': 'r', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'numge': {'offset': 434244, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fin1': {'offset': 434248, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fin2': {'offset': 434252, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'dmasync': {'offset': 434256, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fifo_full_timeout': {'offset': 434260, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fifo_empty_timeout': {'offset': 434264, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fifo_full': {'offset': 434268, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fifo_empty': {'offset': 434272, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ge7_load_ucode': {'offset': 434276, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'gedma': {'offset': 434280, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'hq_gepc': {'offset': 434284, 'access': 'r', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'inferred'}, 'gepc': {'offset': 434288, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'intr': {'offset': 434292, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'inferred'}, 'unstall': {'offset': 434296, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'probe_word': {'offset': 434300, 'access': 'r', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 3735928559, 'grade': 'established'}, 'refresh': {'offset': 434304, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'fin3_netbsd': {'offset': 434432, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'unknown'}, 'finish3': {'offset': 438272, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {}
FIELDS = {'fifo_window': {}, 'ucode_store': {}, 'attr_jump': {}, 'status': {'version': (31, 23), 'ge_ptr': (22, 20), 'ge_ctr': (19, 16), 'zero': (15, 14), 'fifo_lowater': (13, 13), 'fifo_count': (12, 6), 'fifo_overflow': (5, 5), 'dma_sync_src': (4, 3), 'finish_flag1': (2, 2), 'finish_flag2': (1, 1), 'finish_flag3': (0, 0)}, 'numge': {}, 'fin1': {}, 'fin2': {}, 'dmasync': {}, 'fifo_full_timeout': {}, 'fifo_empty_timeout': {}, 'fifo_full': {}, 'fifo_empty': {}, 'ge7_load_ucode': {}, 'gedma': {}, 'hq_gepc': {}, 'gepc': {}, 'intr': {}, 'unstall': {}, 'probe_word': {}, 'refresh': {}, 'fin3_netbsd': {}, 'finish3': {}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'FIFO_DEPTH_LIMIT': {'value': 63, 'count': 1, 'stride': 1}, 'FIFO_FULL_INIT': {'value': 40, 'count': 1, 'stride': 1}, 'FIFO_SPACE_CHECK': {'value': 35, 'count': 1, 'stride': 1}, 'PROBE_WORD': {'value': 3735928559, 'count': 1, 'stride': 1}}
TESTS = []


def decode(name, value):
    """Field name -> value for a register or word."""
    return {f: (value >> lo) & ((1 << (hi - lo + 1)) - 1) for f, (hi, lo) in FIELDS[name].items()}


def encode(name, **fields):
    v = 0
    for f, x in fields.items():
        hi, lo = FIELDS[name][f]
        if x >> (hi - lo + 1):
            raise ValueError('%s.%s: %d does not fit' % (name, f, x))
        v |= x << lo
    return v


def describe(name, value):
    """decode, with enum labels where the field has an enum."""
    out = {}
    for f, x in decode(name, value).items():
        e = ENUMS.get(FIELD_ENUM.get('%s.%s' % (name, f)))
        out[f] = e.get(x, x) if e else x
    return out


def selftest():
    for name, value, expect in TESTS:
        got = decode(name, value)
        for f, want in expect.items():
            assert got[f] == want, (name, hex(value), f, got[f], want)
    return len(TESTS)


if __name__ == '__main__':
    print('%s: %d vectors ok' % (UNIT, selftest()))
