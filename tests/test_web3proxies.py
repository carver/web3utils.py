
import pytest
from unittest.mock import Mock

from web3 import IPCProvider, KeepAliveRPCProvider

from web3utils import ProxyEth, DefaultedWeb3
from web3utils.web3proxies import RPC_PORT, Web3ConfigException


def test_ethproxy_passthrough():
    web3 = Mock()
    eth = ProxyEth(web3)
    eth.getBlock('latest')
    web3.eth.getBlock.assert_called_once_with('latest')

def test_ethproxy_laziness(untouchable):
    # ProxyEth should not touch web3 during initialization (to avoid making calls to a bad provider)
    eth = ProxyEth(untouchable)

def test_web3_ipc_default(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda path: True)
    web3 = DefaultedWeb3()
    assert type(web3._requestManager.provider) == IPCProvider

def test_web3_rpc_fallback(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda path: False)
    conn = Mock(laddr=(None,RPC_PORT))
    monkeypatch.setattr('psutil.net_connections', lambda: [conn])
    web3 = DefaultedWeb3()
    assert type(web3._requestManager.provider) == KeepAliveRPCProvider

def test_web3_set_provider_manually(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('psutil.net_connections', lambda: [])
    provider = Mock()
    provider.make_request.return_value = {'result': '0xbeef'}
    web3 = DefaultedWeb3()
    web3.setProvider(provider)
    assert web3._requestManager.provider == provider
    # shouldn't raise exception:
    sha = web3.sha3('')
    # using the new provider:
    assert web3.toHex(sha) == '0xbeef'

def test_web3_providers_missing(monkeypatch):
    '''
    If you can't detect any providers, and provider is not manually set,
    raise exception on attribute access
    '''
    monkeypatch.setattr('os.path.exists', lambda path: False)
    monkeypatch.setattr('psutil.net_connections', lambda: [])
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
