
import pytest

from web3utils import web3
from web3utils.chainstate import stalecheck, StaleBlockchain


@stalecheck(web3, days=2)
def square(x):
    return x*x


class Block():
    def __init__(self, _timestamp):
        self.timestamp = _timestamp
        self.number = 123


@pytest.fixture
def nowblock():
    return Block(3141592653)


@pytest.fixture
def freshblock(nowblock):
    return Block(nowblock.timestamp - 86400 * 2)


@pytest.fixture
def staleblock(nowblock):
    return Block(nowblock.timestamp - 86400 * 2 - 1)


def test_stalecheck_runtime_disabled():
    assert square(3, assertfresh=False) == 9


def test_stalecheck_passes_when_fresh(mockweb3, nowblock, freshblock, mocker):
    mocker.patch('time.time', return_value=nowblock.timestamp)
    mockweb3.eth.getBlock.return_value = freshblock

    @stalecheck(mockweb3, days=2)
    def true():
        return True

    assert true()


def test_stalecheck_raises_when_old(mockweb3, nowblock, staleblock, mocker):
    mocker.patch('time.time', return_value=nowblock.timestamp)
    mockweb3.eth.getBlock.return_value = staleblock

    #pytest.set_trace()

    @stalecheck(mockweb3, days=2)
    def true():
        return True

    with pytest.raises(StaleBlockchain):
        true()
