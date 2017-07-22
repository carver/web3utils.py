
import pytest
from unittest.mock import Mock, MagicMock

from web3utils import sweeten_contracts, DefaultedWeb3

@pytest.fixture()
def untouchable():
    return Mock(spec=[], set_spec=[])

@pytest.fixture()
def provider():
    noop = Mock()
    noop.make_request.return_value = {'result': ''}
    return noop

@pytest.fixture()
def mockweb3(provider):
    web3 = sweeten_contracts(DefaultedWeb3())
    web3.setProvider(provider)
    web3._proxyto = MagicMock()
    return web3
