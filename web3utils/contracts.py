
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

    You can modify a call in two ways:

    ```
    # more pythonic, but longer -- the preferred style
    contract.withdraw.transact({from: eth.accounts[1]}).withargs(web3.toWei(1, 'ether'))
    # short-hand
    contract.withdraw.transact({from: eth.accounts[1]})(web3.toWei(1, 'ether'))
    ```

    All the modifier functions work just as if you had called it using the web3.py style, eg:


    ```
    contract.transact({from: eth.accounts[1]}).withdraw(web3.toWei(1, 'ether'))
    ```

    Note that modified calls are actually *longer* than the core web3.py (or in short-hand, uglier).

    If you are mostly using transactions, or heavily modified calls, you're probably best off using
    contracts without the sugar (the original web3.py style). But if you're using a read-heavy
    pattern, and it is not caller dependent, then this sugar can be much more convenient.
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
        self.__prepared_call = PreparedContractMethod(contract.call(), function)

    def __call__(self, *args):
        return self.__prepared_call.withargs(*args)

    def __getattr__(self, attr):
        return ContractCallModifier(attr, self.__contract, self.__function)


class ContractCallModifier:

    def __init__(self, modifier, contract, function):
        self.__bound_modifier = getattr(contract, modifier)
        self.__function = function

    def __call__(self, *args, **kwargs):
        modified = self.__bound_modifier(*args, **kwargs)
        return PreparedContractMethod(modified, self.__function)


class PreparedContractMethod:

    def __init__(self, prepared_contract, function):
        self.__prepared_function = getattr(prepared_contract, function)

    def withargs(self, *args):
        args = map(self.__tobytes, args)
        result = self.__prepared_function(*args)
        if is_empty_hex(result):
            return None
        else:
            return result

    __call__ = withargs

    def __tobytes(self, candidate):
        if isinstance(candidate, str):
            if not candidate.startswith('0x'):
                raise TypeError("Cannot call %s with %r as str, convert to bytes or hex first" % (
                    (self.__prepared_function, candidate)))
            return Web3.toAscii(candidate)
        return candidate
