
import pytest
from unittest.mock import Mock

from web3utils.contracts import ContractSugar, ContractMethod, EthContractSugar

def test_autoconvert_hex_to_bytes():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method('0x636172766572')
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(b'carver')

def test_autoconvert_hex_to_bytes():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method(b'carver')
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(b'carver')

def test_cannot_convert_nonhex_string():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    with pytest.raises(TypeError):
        sweet_method('636172766572')

def test_contract_call_default():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method()
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with()

def test_contract_custom_transact():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method(transact={'holy': 1})
    contract.transact.assert_called_once_with({'holy': 1})
    contract.transact().grail.assert_called_once_with()

def test_contract_returns_none():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    contract.call().grail.return_value = '0x0000'
    assert sweet_method() is None

def test_eth_contract_passthrough():
    contract = Mock()
    onelump = EthContractSugar(contract)
    assert onelump.contract == contract
    twolumps = EthContractSugar(onelump)
    assert twolumps.contract == contract

def test_contract_sugar_passthrough():
    contract = Mock()
    onelump = ContractSugar(contract)
    assert onelump._web3py_contract == contract
    twolumps = ContractSugar(onelump)
    assert twolumps._web3py_contract == contract
