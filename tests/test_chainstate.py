
import pytest
from unittest.mock import Mock

from web3utils import web3
from web3utils.chainstate import isfresh, stalecheck, StaleBlockchain


@pytest.fixture
def square(mockweb3):
    @stalecheck(mockweb3, days=2)
    def _square(x):
        return x*x
    return _square


@pytest.fixture
def now():
    return 3141592653


class Block():
    def __init__(self, _timestamp):
        self.timestamp = _timestamp
        self.number = 123


def test_is_not_fresh_with_no_block():
    assert not isfresh(None, 1)


def test_is_not_fresh(mocker, now):
    mocker.patch('time.time', return_value=now)
    SECONDS_ALLOWED = 2 * 86400
    stale = Block(now - SECONDS_ALLOWED - 1)
    assert not isfresh(stale, SECONDS_ALLOWED)


def test_is_fresh(mocker, now):
    mocker.patch('time.time', return_value=now)
    SECONDS_ALLOWED = 2 * 86400
    stale = Block(now - SECONDS_ALLOWED)
    assert isfresh(stale, SECONDS_ALLOWED)


def test_stalecheck_pass(mocker, square):
    mocker.patch('web3utils.chainstate.isfresh', return_value=True)
    assert square(3) == 9


def test_stalecheck_fail(mocker, square):
    mocker.patch('web3utils.chainstate.isfresh', return_value=False)
    with pytest.raises(StaleBlockchain):
        square(3)


def test_stalecheck_runtime_disabled(mocker, mockweb3, square):
    mocker.patch('web3utils.chainstate.isfresh', return_value=False)
    assert square(3, assertfresh=False) == 9


def test_stalecheck_calls_isfresh_with_block_and_time(mockweb3, mocker):
    freshspy = mocker.patch('web3utils.chainstate.isfresh', return_value=True)
    block = Mock()
    mockweb3.eth.getBlock.return_value = block

    @stalecheck(mockweb3, days=3)
    def true():
        return True

    assert true()
    freshspy.assert_called_once_with(block, 86400 * 3)
