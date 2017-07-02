
import os

from psutil import net_connections
from web3 import Web3, IPCProvider, KeepAliveRPCProvider
from web3.providers import ipc


class DefaultedWeb3(object):
    def __init__(self):
        self.__provider = self.__guess_provider()
        self.__proxyto = Web3(self.__provider()) if self.__provider else None

    def setProvider(self, provider):
        if self.__proxyto:
            self.__proxyto.setProvider(provider)
        else:
            self.__proxyto = Web3(provider())

    def __guess_provider(self):
        if os.path.exists(ipc.get_default_ipc_path()):
            return IPCProvider
        elif any(len(conn.laddr) > 1 and conn.laddr[1] == 8545 for conn in net_connections()):
            return KeepAliveRPCProvider
        return None

    def __getattr__(self, attr):
        'all other attributes should be proxied through to the real web3'
        if not self.__proxyto:
            raise Exception("Could not auto-detect provider, set with web3.setProvider() first")
        return getattr(self.__proxyto, attr)


class ProxyEth(object):
    def __init__(self, web3):
        self.__proxyweb3 = web3

    def __getattr__(self, attr):
        if not self.__proxyweb3 or not hasattr(self.__proxyweb3, 'eth'):
            raise Exception("web3 was not correctly initialized")
        return getattr(self.__proxyweb3.eth, attr)
