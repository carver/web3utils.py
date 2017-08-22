
import pytest

from web3utils.encodings import hex2bytes, emptyhex

def test_hex_to_bytes_already_bytes():
    assert hex2bytes(b'\x11\x11') == b'\x11\x11'

def test_hex_to_bytes():
    assert hex2bytes('0x1111') == b'\x11\x11'

@pytest.mark.parametrize(
        ('num_bytes, expected'),
        (
            (1, '0x00'),
            (20, '0x0000000000000000000000000000000000000000'),
            (32, emptyhex()),
        )
    )
def test_emptyhex(num_bytes, expected):
    assert emptyhex(num_bytes) == expected
