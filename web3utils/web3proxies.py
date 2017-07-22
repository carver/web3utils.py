
import codecs
import os

import psutil

from web3 import Web3, IPCProvider, KeepAliveRPCProvider
from web3.providers import ipc

from web3utils.contracts import EthContractSugar

RPC_PORT = 8545


class DefaultedWeb3:
    '''
    This provides easy global access without initializing the Web3 Provider.

    Also, it adds a bit of sugar around contracts. If you want the original
    web3.py-style contracts, use `web3.eth.original_contract(abi=...)`
    instead of `web3.eth.contract(abi=...)`
    '''
    def __init__(self):
        self._proxyto = None
        provider_type = self.__guess_provider_type()
        if provider_type:
            self.setProvider(provider_type())

    def setProvider(self, provider):
        if self._proxyto:
            self._proxyto.setProvider(provider)
        else:
            self._proxyto = Web3(provider)

    def __guess_provider_type(self):
        if os.path.exists(ipc.get_default_ipc_path()):
            return IPCProvider
        elif self.__found_rpc():
            return KeepAliveRPCProvider
        return None

    def __getattr__(self, attr):
        'all other attributes should be proxied through to the real web3'
        self.__assert_proxy()
        return getattr(self._proxyto, attr)

    def __found_rpc(self):
        conns = psutil.net_connections()
        return any(len(conn.laddr) > 1 and conn.laddr[1] == RPC_PORT for conn in conns)

    def __assert_proxy(self):
        if not self._proxyto:
            raise Web3ConfigException(
                    "Could not auto-detect provider, set with web3.setProvider() first")

    def sha3(self, value, **kwargs):
        self.__assert_proxy()
        if isinstance(value, (bytes, bytearray)) and 'encoding' not in kwargs:
            kwargs['encoding'] = 'bytes'
        sha_hex = self._proxyto.sha3(value, **kwargs)
        if isinstance(sha_hex, str):
            return codecs.decode(sha_hex[2:], 'hex')
        else:
            return sha_hex


def sweeten_contracts(web3):
    if not isinstance(web3.eth.contract, EthContractSugar):
        web3.eth.original_contract = web3.eth.contract
        web3.eth.contract = EthContractSugar(web3.eth.original_contract)
    return web3


class ProxyEth:
    def __init__(self, web3):
        self.__proxyweb3 = web3

    def __getattr__(self, attr):
        if not self.__proxyweb3 or not hasattr(self.__proxyweb3, 'eth'):
            raise Web3ConfigException("web3 was not correctly initialized")
        return getattr(self.__proxyweb3.eth, attr)


class Web3ConfigException(Exception):
    pass
