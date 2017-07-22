
from .contracts import ContractSugar, CONTRACT_ENCODING  # noqa
from .web3proxies import DefaultedWeb3, ProxyEth, sweeten_contracts

web3 = sweeten_contracts(DefaultedWeb3())

eth = ProxyEth(web3)

STRING_ENCODING = CONTRACT_ENCODING
