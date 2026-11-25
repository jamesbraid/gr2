"""generated from devices/ge7/registers.toml by defs-gen - do not edit, change the source
defs-gen 3
input sha256 e30b0fdf775c51b8fdeab63c9fca6fbdcc7b0ebfdb6d0844c750cd3ef14767df
GE7 geometry engines: host window and microcode load registers"""

UNIT = 'ge7'
REGISTERS = {'shared_ram': {'offset': 0, 'access': 'rw', 'width': 32, 'count': 32767, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ucode_ready': {'offset': 131068, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'slot0_ram': {'offset': 425984, 'access': 'rw', 'width': 32, 'count': 248, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'inferred'}, 'ucode_d0': {'offset': 426976, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ucode_d1': {'offset': 426980, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ucode_d2': {'offset': 426984, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ucode_d3': {'offset': 426988, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'revision': {'offset': 426996, 'access': 'rw', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'slot_ram': {'offset': 427008, 'access': 'rw', 'width': 32, 'count': 1792, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {}
FIELDS = {'shared_ram': {}, 'ucode_ready': {}, 'slot0_ram': {}, 'ucode_d0': {}, 'ucode_d1': {}, 'ucode_d2': {}, 'ucode_d3': {'stored': (6, 0)}, 'revision': {'rev': (7, 5)}, 'slot_ram': {}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {}
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
