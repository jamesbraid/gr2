"""generated from devices/clock/registers.toml by defs-gen - do not edit, change the source
defs-gen 3
input sha256 467273ff471ddf2134ff68f52c6be88c8ce534408f7b0b63cc8677a1cd2e2738
Express board configuration ports and pixel clock control"""

UNIT = 'clock'
REGISTERS = {'port0': {'offset': 442368, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'port1': {'offset': 442372, 'access': 'rw', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'port2': {'offset': 442376, 'access': 'r', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'port3': {'offset': 442380, 'access': 'r', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}, 'data': {'offset': 442400, 'access': 'w', 'width': 8, 'count': 1, 'stride': 1, 'space': None, 'reset': 'unknown', 'grade': 'established'}}
WORDS = {}
FIELDS = {'port0': {'monitor_code_rev4': (7, 4), 'board_rev_n': (3, 0)}, 'port1': {'z_present_rev4': (5, 5), 'depth24_rev4': (4, 4), 'no_z_rev3': (3, 2), 'low2': (1, 0)}, 'port2': {'backend_rev_n': (3, 2), 'monitor_code_hi': (1, 0)}, 'port3': {'slot_c_empty': (5, 4), 'slot_b_empty': (3, 2), 'slot_a_empty': (1, 0)}, 'data': {'last': (1, 1), 'bit': (0, 0)}}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'BOARD_REV_SPLIT': {'value': 4, 'count': 1, 'stride': 1}, 'COMMAND_BYTES_REV3': {'value': 17, 'count': 1, 'stride': 1}, 'EXTRA_BYTE_REV3': {'value': 165, 'count': 1, 'stride': 1}, 'LOAD_REV3': {'value': 64, 'count': 1, 'stride': 1}, 'SEL_60HZ': {'value': 1, 'count': 1, 'stride': 1}, 'SEL_72HZ': {'value': 2, 'count': 1, 'stride': 1}, 'SEL_OTHER': {'value': 4, 'count': 1, 'stride': 1}, 'SEL_REV4': {'value': 7, 'count': 1, 'stride': 1}, 'SERIAL_BYTES_REV4': {'value': 7, 'count': 1, 'stride': 1}}
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
