"""generated from devices/bt457/registers.toml by defs-gen - do not edit, change the source
defs-gen 3
input sha256 e70d1735c70ebfb40a10bdbfae82173a37248264f8277909d1c208d56f73f0dc
Brooktree Bt457 RAMDAC as wired on the Express board (three chips, one per colour)"""

UNIT = 'bt457'
REGISTERS = {'addr': {'offset': 0, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'palette': {'offset': 4, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'ctrl': {'offset': 8, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'overlay': {'offset': 12, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {'COMMAND': {'width': 8, 'grade': 'established'}}
FIELDS = {'addr': {}, 'palette': {}, 'ctrl': {}, 'overlay': {}, 'COMMAND': {'mux_select': (7, 7), 'ram_enable': (6, 6), 'blink_rate': (5, 4), 'overlay1_blink': (3, 3), 'overlay0_blink': (2, 2), 'overlay1_display': (1, 1), 'overlay0_display': (0, 0)}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'ADDR_BLINK_MASK': {'value': 5, 'count': 1, 'stride': 1}, 'ADDR_COMMAND': {'value': 6, 'count': 1, 'stride': 1}, 'ADDR_READ_MASK': {'value': 4, 'count': 1, 'stride': 1}, 'ADDR_TEST': {'value': 7, 'count': 1, 'stride': 1}, 'INIT_COMMAND': {'value': 193, 'count': 1, 'stride': 1}, 'INIT_READ_MASK': {'value': 0, 'count': 1, 'stride': 1}, 'OVERLAY_ENTRIES': {'value': 4, 'count': 1, 'stride': 1}, 'PALETTE_ENTRIES': {'value': 256, 'count': 1, 'stride': 1}, 'UNBLANK_READ_MASK': {'value': 255, 'count': 1, 'stride': 1}}
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
