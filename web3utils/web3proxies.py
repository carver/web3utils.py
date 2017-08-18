
import codecs
import os

from web3 import Web3, IPCProvider, HTTPProvider
from web3.providers import ipc

from web3utils.contracts import EthContractSugar


class DefaultedWeb3:
    '''
    This provides easy global access without initializing the Web3 Provider.

    Also, it adds a bit of sugar around contracts. If you want the original
    web3.py-style contracts, use `web3.eth.original_contract(abi=...)`
    instead of `web3.eth.contract(abi=...)`
    '''

    _DEFAULT_PROVIDERS = [IPCProvider(), HTTPProvider('http://127.0.0.1:8545/')]

    def __init__(self):
        self._proxyto = Web3(None)
        provider = self._first_connection(self._DEFAULT_PROVIDERS)
        self.setProvider(provider)

    def _first_connection(self, providers):
        for provider in providers:
            if provider.isConnected():
                return provider

    def __getattr__(self, attr):
        'all other attributes should be proxied through to the real web3'
        if attr != 'setProvider':
            self.__assert_proxy()
        return getattr(self._proxyto, attr)

    def __assert_proxy(self):
        if not self._proxyto.currentProvider:
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
