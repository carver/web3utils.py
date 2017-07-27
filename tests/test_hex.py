

from web3utils.hex import hex2bytes

def test_hex_to_bytes_already_bytes():
    assert hex2bytes(b'\x11\x11') == b'\x11\x11'

def test_hex_to_bytes():
    assert hex2bytes('0x1111') == b'\x11\x11'

