
import pytest
from unittest.mock import Mock

from web3utils import ProxyEth, DefaultedWeb3
from web3utils.web3proxies import Web3ConfigException

PROVIDER_LIVE = Mock(isConnected=lambda: True)
PROVIDER_DOWN = Mock(isConnected=lambda: False)

def test_ethproxy_passthrough():
    web3 = Mock()
    eth = ProxyEth(web3)
    eth.getBlock('latest')
    web3.eth.getBlock.assert_called_once_with('latest')

def test_ethproxy_laziness(untouchable):
    # ProxyEth should not touch web3 during initialization (to avoid making calls to a bad provider)
    eth = ProxyEth(untouchable)

@pytest.mark.parametrize(
        'providers,selected',
        (
            ([], None),
            ([PROVIDER_DOWN], None),
            ([PROVIDER_DOWN, PROVIDER_LIVE], PROVIDER_LIVE),
            ([PROVIDER_LIVE, Mock(spec=[], set_spec=[])], PROVIDER_LIVE),
        ),
        ids=['empty', 'all_down', 'one_live', 'shortcut_eval']
    )
def test_first_provider(providers, selected):
    web3 = DefaultedWeb3()
    assert web3._first_connection(providers) == selected

def test_web3_providers_missing(mocker):
    '''
    If you can't detect any providers, and provider is not manually set,
    raise exception on attribute access
    '''
    mocker.patch.object(DefaultedWeb3, '_DEFAULT_PROVIDERS', [])
    web3 = DefaultedWeb3()
    with pytest.raises(Web3ConfigException):
        web3.sha3('0xDEAD')

def test_sha3_bytes(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda path: True)
    web3 = DefaultedWeb3()
    sha = web3.sha3(b'eth', encoding='bytes')
    assert type(sha) == bytes
    assert web3.toHex(sha) == '0x4f5b812789fc606be1b3b16908db13fc7a9adf7ca72641f84d75b47069d3d7f0'

def test_sha3_argument_detection(mockweb3):
    mockweb3.sha3(b'parrot')
    mockweb3._proxyto.sha3.assert_called_once_with(b'parrot', encoding='bytes')
