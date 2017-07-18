
import os

from psutil import net_connections

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
        self.__proxyto = None
        provider_type = self.__guess_provider_type()
        if provider_type:
            self.setProvider(provider_type())

    def setProvider(self, provider):
        if self.__proxyto:
            self.__proxyto.setProvider(provider)
        else:
            self.__proxyto = Web3(provider)

    def __guess_provider_type(self):
        if os.path.exists(ipc.get_default_ipc_path()):
            return IPCProvider
        elif any(len(conn.laddr) > 1 and conn.laddr[1] == RPC_PORT for conn in net_connections()):
            return KeepAliveRPCProvider
        return None

    def __getattr__(self, attr):
        'all other attributes should be proxied through to the real web3'
        if not self.__proxyto:
            raise Web3ConfigException(
                    "Could not auto-detect provider, set with web3.setProvider() first")
        return getattr(self.__proxyto, attr)


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
