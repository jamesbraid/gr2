"""generated from devices/xmap5/registers.toml by defs-gen - do not edit, change the source
defs-gen 4
input sha256 16b6070bb233d1af1da4ef209d70365aa464954f82eda820d7ca338b5819fb36
XMAP5 multimode colour mapper (five per Express board)"""

UNIT = 'xmap5'
REGISTERS = {'misc': {'offset': 0, 'access': 'w', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'inferred'}, 'mode': {'offset': 4, 'access': 'w', 'width': 32, 'count': 1, 'stride': 4, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'clut': {'offset': 8, 'access': 'w', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'crc': {'offset': 12, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'unknown'}, 'addrlo': {'offset': 16, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'addrhi': {'offset': 20, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'bytecount': {'offset': 24, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'unknown'}, 'fifostatus': {'offset': 28, 'access': 'r', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {'MODE_WORD': {'width': 32, 'grade': 'inferred'}}
FIELDS = {'misc': {}, 'mode': {}, 'clut': {}, 'crc': {}, 'addrlo': {}, 'addrhi': {}, 'bytecount': {}, 'fifostatus': {'overflow': (2, 2), 'room': (1, 1), 'busy': (0, 0)}, 'MODE_WORD': {'pix_page': (31, 27), 'pix_mode': (26, 24), 'overlay_enable': (23, 20), 'alt_video': (19, 18), 'pd_mode': (17, 16), 'popup_flags': (15, 14), 'aux_page': (13, 9), 'underlay_enable': (8, 8), 'popup_mode': (7, 0)}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'BOOT_MODE_WORD_DID0': {'value': 2181038080, 'count': 1, 'stride': 1}, 'CHIP_COUNT': {'value': 5, 'count': 1, 'stride': 1}, 'CLUT_ENTRIES': {'value': 8192, 'count': 1, 'stride': 1}, 'MODE_ENTRIES': {'value': 32, 'count': 1, 'stride': 1}, 'TEXTPORT_CLUT_BASE': {'value': 4096, 'count': 1, 'stride': 1}, 'WINDOW_SIZE': {'value': 32, 'count': 1, 'stride': 1}}
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
