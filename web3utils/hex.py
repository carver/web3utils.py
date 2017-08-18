
import codecs

from web3 import Web3


def emptybytes(digits=64):
    non_prefixed = emptyhex(digits)[2:]
    return codecs.decode(non_prefixed, 'hex')


def emptyhex(digits=64):
    return "0x" + "0" * digits


def is_empty_hex(value):
    if not isinstance(value, str):
        return False
    if not value.startswith('0x'):
        return False
    return value == emptyhex(len(value) - 2)


def hex2bytes(hex_str):
    if isinstance(hex_str, str):
        return Web3.toAscii(hex_str)
    return hex_str


EMPTY_ADDR = emptyhex(40)
EMPTY_ADDR_BYTES = emptybytes(40)
EMPTY_SHA3 = emptyhex(64)
EMPTY_SHA3_BYTES = emptybytes(64)
