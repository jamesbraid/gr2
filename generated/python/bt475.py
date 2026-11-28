"""generated from devices/bt475/registers.toml by defs-gen - do not edit, change the source
SPDX-License-Identifier: BSD-3-Clause
defs-gen 5
input sha256 e092e289cdf7071aaa43ac066a8157c9ebaf1861cc18de50147bf970a5c6e882
Brooktree Bt475 and Bt477 RAMDAC: datasheet port map only, no Express use found"""

UNIT = 'bt475'
REGISTERS = {}
WORDS = {}
FIELDS = {}
ENUMS = {}
FIELD_ENUM = {}
CONSTANTS = {'SEL_ADDR_READ': {'value': 3, 'count': 1, 'stride': 1}, 'SEL_ADDR_WRITE': {'value': 0, 'count': 1, 'stride': 1}, 'SEL_COMMAND': {'value': 6, 'count': 1, 'stride': 1}, 'SEL_OVERLAY_DATA': {'value': 5, 'count': 1, 'stride': 1}, 'SEL_OVERLAY_READ': {'value': 7, 'count': 1, 'stride': 1}, 'SEL_OVERLAY_WRITE': {'value': 4, 'count': 1, 'stride': 1}, 'SEL_PALETTE': {'value': 1, 'count': 1, 'stride': 1}, 'SEL_READ_MASK': {'value': 2, 'count': 1, 'stride': 1}}
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
