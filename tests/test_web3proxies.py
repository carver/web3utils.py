
import os

from web3.providers import ipc

from web3utils import ProxyEth, DefaultedWeb3

from tests.utilities import Echo, Untouchable


def test_ethproxy_passthrough():
    web3 = Echo("web3")
    eth = ProxyEth(web3)
    assert str(eth.camelot) == "web3.eth.camelot", "Failed to pass through to web3.eth"


def test_ethproxy_laziness():
    # ProxyEth should not touch web3 during initialization (to avoid making calls to a bad provider)
    # Untouchable with raise an exception if getaddr is called
    eth = ProxyEth(Untouchable())


def test_web3_provider(monkeypatch):
    # test type(web3._requestManager.provider) == web3.providers.ipc.IPCProvider
    # after monkeypatching os.path.exists() => true
    monkeypatch.setattr(os.path, 'exists', lambda path: True)
    web3 = DefaultedWeb3()
    assert type(web3._requestManager.provider) == ipc.IPCProvider
