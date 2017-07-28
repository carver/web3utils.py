
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
                candidate = candidate.encode(CONTRACT_ENCODING)
            except UnicodeEncodeError as unicode_exc:
                raise TypeError("Cannot call %s with %r. Convert to bytes or a %s string first" % (
                    (self.__prepared_function, candidate, CONTRACT_ENCODING))) from unicode_exc
        return candidate


def dict_copy(func):
    "copy dict args, to avoid modifying caller's copy"
    def proxy(*args, **kwargs):
        new_args = []
        new_kwargs = {}
        for var in kwargs:
            if isinstance(kwargs[var], dict):
                new_kwargs[var] = dict(kwargs[var])
            else:
                new_kwargs[var] = kwargs[var]
        for arg in args:
            if isinstance(arg, dict):
                new_args.append(dict(arg))
            else:
                new_args.append(arg)
        return func(*new_args, **new_kwargs)
    return proxy
