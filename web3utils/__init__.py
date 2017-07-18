
from .contracts import ContractSugar  # noqa
from .web3proxies import DefaultedWeb3, ProxyEth, sweeten_contracts

web3 = sweeten_contracts(DefaultedWeb3())

eth = ProxyEth(web3)
