
from web3 import Web3

from web3utils.hex import is_empty_hex
from web3utils.utils import WrapCallable


class EthContractSugar:

    def __init__(self, original_contract):
        self.contract = original_contract

    def __call__(self, *args, **kwargs):
        contract = self.contract(*args, **kwargs)
        if isinstance(contract, WrapCallable) or isinstance(contract, ContractSugar):
            # contract already wrapped
            return contract
        elif type(contract) == type:
            # contract still needs to be initialized, wrap afterwards
            return WrapCallable(contract, ContractSugar)
        else:
            return ContractSugar(contract)


class ContractSugar:
    """
    Call Ethereum contracts more succinctly

    A few important changes:
     * auto-convert hex strings to bytes
     * quicker method calls like `contract.owner()` instead of `contract.call().owner()`
     * Instead of returning `"0x000..."` on empty results, return `None`
     * contract equality is entirely based on the address

    Often, one Ethereum contract will output a hex string, which you want to use as an input to
    another contract, but these need to be formatted as bytes. This class will automatically format
    hex strings into bytes for you. If you already have arguments in the form of bytes, just confirm
    that it is type `bytes` instead of type `string`. This is one reason that web3utils only
    supports Python 3.

    Short contract calls will be assumed to be read-only (equivalent to .call() in web3.py),
    unless it is modified first.

    Note that this will *not* prevent you from calling a method that tries to alter state.
    That state change will just never be sent to the rest of the network.

    You can modify a call like so:

    ```
    contract.withdraw(amount, transact={'from': eth.accounts[1], 'gas': 100000, ...})
    ```

    Which is equivalent to this web3.py approach:


    ```
    contract.transact({'from': eth.accounts[1], 'gas': 100000, ...}).withdraw(amount)
    ```
    """

    def __init__(self, contract):
        self.__contract = contract

    def __getattr__(self, attr):
        return ContractMethod(self.__contract, attr)

    def __eq__(self, other):
        if not isinstance(other, ContractSugar):
            return False
        if not hasattr(self.__contract, 'address'):
            return False
        if not hasattr(other.__contract, 'address'):
            return False
        return self.__contract.address == other.__contract.address


class ContractMethod:

    def __init__(self, contract, function):
        self.__contract = contract
        self.__function = function

    def __call__(self, *args, **kwargs):
        contract_function = self.__prepared_function(**kwargs)
        args = map(self.__tobytes, args)
        result = contract_function(*args)
        if is_empty_hex(result):
            return None
        else:
            return result

    def __prepared_function(self, **kwargs):
        if not kwargs:
            modifier, modifier_dict = 'call', {}
        elif len(kwargs) == 1:
            modifier, modifier_dict = kwargs.popitem()
        else:
            raise ValueError("Only use one keyword argument at a time, eg~ transact or call")
        contract_modifier_func = getattr(self.__contract, modifier)
        return getattr(contract_modifier_func(modifier_dict), self.__function)

    def __tobytes(self, candidate):
        if isinstance(candidate, str):
            if not candidate.startswith('0x'):
                raise TypeError("Cannot call %s with %r, convert to bytes or hex string first" % (
                    (self.__prepared_function, candidate)))
            return Web3.toAscii(candidate)
        return candidate
