
from toolz import compose

from web3utils.hex import is_empty_hex


# default is utf-8: https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI#argument-encoding
CONTRACT_ENCODING = 'utf-8'


class EthContractSugar:

    def __init__(self, original_contract):
        if isinstance(original_contract, EthContractSugar):
            self.contract = original_contract.contract
        else:
            self.contract = original_contract

    def __call__(self, *args, **kwargs):
        contract = self.contract(*args, **kwargs)
        if type(contract) == type:
            # contract still needs to be initialized, wrap afterwards
            return compose(ContractSugar, contract)
        else:
            return ContractSugar(contract)


class ContractSugar:
    """
    Call Ethereum contracts more succinctly

    Several important changes:
     * quicker method calls like `contract.owner()` instead of `contract.call().owner()`
     * encode all method argument strings as utf-8
     * instead of returning `"0x000..."` on empty results, return `None`

    Short contract calls will be assumed to be read-only (equivalent to .call() in web3.py),
    unless it is modified first.

    Note that this will *not* prevent you from calling a method that tries to alter state.
    That state change will just never be sent to the rest of the network as a transaction.

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
        if isinstance(contract, ContractSugar):
            self._web3py_contract = contract._web3py_contract
        else:
            self._web3py_contract = contract

    def __getattr__(self, attr):
        return ContractMethod(self._web3py_contract, attr)


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
            try:
                candidate = bytes(candidate, encoding=CONTRACT_ENCODING)
            except UnicodeEncodeError as unicode_exc:
                raise TypeError("Cannot call %s with %r. Convert to bytes or a %s string first" % (
                    (self.__prepared_function, candidate, CONTRACT_ENCODING))) from unicode_exc
        return candidate
