"""generated from devices/vc1-express/registers.toml by defs-gen - do not edit, change the source
defs-gen 3
input sha256 25734a17818e96cd0d8d228db9bbafb76b5aba73b4daabd22058b0bf5bc47127
VC1 video timing, cursor and display-ID controller on the Express board"""

UNIT = 'vc1_express'
REGISTERS = {'command': {'offset': 442432, 'access': 'rw', 'width': 16, 'count': 1, 'stride': 2, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'xmapmode': {'offset': 442436, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'unknown'}, 'sram': {'offset': 442440, 'access': 'rw', 'width': 16, 'count': 1, 'stride': 2, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'testreg': {'offset': 442444, 'access': 'r', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'addrlo': {'offset': 442448, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'addrhi': {'offset': 442452, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'sysctl': {'offset': 442456, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {}
FIELDS = {'command': {}, 'xmapmode': {}, 'sram': {}, 'testreg': {'revision': (2, 0)}, 'addrlo': {}, 'addrhi': {}, 'sysctl': {'video': (7, 7), 'genlock': (6, 6), 'cursor_display': (5, 5), 'cursor': (4, 4), 'did': (3, 3), 'core': (2, 2), 'timing': (1, 1), 'interrupt': (0, 0)}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'CURSOR_X_THRESHOLD': {'value': 32, 'count': 1, 'stride': 1}, 'REG_BLACKOUT': {'value': 96, 'count': 1, 'stride': 1}, 'REG_CURSOR_EP': {'value': 32, 'count': 1, 'stride': 1}, 'REG_CURSOR_MODE': {'value': 38, 'count': 1, 'stride': 1}, 'REG_CURSOR_X': {'value': 34, 'count': 1, 'stride': 1}, 'REG_CURSOR_Y': {'value': 36, 'count': 1, 'stride': 1}, 'REG_DID_DIV': {'value': 68, 'count': 1, 'stride': 1}, 'REG_DID_END': {'value': 66, 'count': 1, 'stride': 1}, 'REG_DID_EP': {'value': 64, 'count': 1, 'stride': 1}, 'REG_REVISION': {'value': 5, 'count': 1, 'stride': 1}, 'REG_VID_ENABLE': {'value': 20, 'count': 1, 'stride': 1}, 'REG_VID_EP': {'value': 0, 'count': 1, 'stride': 1}, 'SRAM_CURSOR_FRAME_TABLE': {'value': 2304, 'count': 1, 'stride': 1}, 'SRAM_CURSOR_GLYPH': {'value': 2560, 'count': 1, 'stride': 1}, 'SRAM_CURSOR_LINE_LIST': {'value': 1024, 'count': 1, 'stride': 1}, 'SRAM_DID_FRAME_TABLE': {'value': 2816, 'count': 1, 'stride': 1}, 'SRAM_DID_LINE_DEFAULT': {'value': 5120, 'count': 1, 'stride': 1}, 'SRAM_FRAME_TABLE': {'value': 2048, 'count': 1, 'stride': 1}, 'SRAM_INTERLACED': {'value': 2544, 'count': 1, 'stride': 1}, 'SRAM_LINE_LIST': {'value': 0, 'count': 1, 'stride': 1}, 'SRAM_SCREENWIDTH': {'value': 2546, 'count': 1, 'stride': 1}, 'SYSCTL_CURSOR_DISPLAY': {'value': 32, 'count': 1, 'stride': 1}, 'SYSCTL_GENSYNC': {'value': 64, 'count': 1, 'stride': 1}, 'SYSCTL_LOAD': {'value': 3, 'count': 1, 'stride': 1}, 'SYSCTL_VC1_DID': {'value': 12, 'count': 1, 'stride': 1}}
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
