

def emptyhex(digits=64):
    return "0x" + "0" * digits

def is_empty_hex(value):
    if not isinstance(value, str):
        return False
    if not value.startswith('0x'):
        return False
    value = value[2:]
    return value == '0' * len(value)

EMPTY_ADDR = emptyhex(40)
EMPTY_SHA = emptyhex(64)
