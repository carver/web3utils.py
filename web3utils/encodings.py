
import codecs

from web3 import Web3


def emptybytes(num_bytes=32):
    return b'\0' * num_bytes


def emptyhex(num_bytes=32):
    return "0x" + "00" * num_bytes


def is_empty_hex(value):
    if not isinstance(value, str):
        return False
    if not value.startswith('0x'):
        return False
    noprefix = value[2:]
    return noprefix == '0' * len(noprefix)


def hex2bytes(hex_str):
    if isinstance(hex_str, str):
        return Web3.toAscii(hex_str)
    return hex_str
