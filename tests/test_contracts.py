
import pytest
from unittest.mock import Mock

from web3utils.contracts import ContractSugar, ContractMethod, EthContractSugar

def test_encode_arguments_as_utf8():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method('Ö')
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(b'O\xcc\x88')

def test_hex_is_nothing_special():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method('0x636172766572')
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(b'0x636172766572')

def test_bytes_passthrough():
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method(b'carver')
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(b'carver')

def test_bytes_passthrough():
    encoded = bytes('Ö', encoding='utf-8')
    contract = Mock()
    sweet_method = ContractMethod(contract, 'grail')
    sweet_method(encoded)
    contract.call.assert_called_once_with({})
    contract.call().grail.assert_called_once_with(encoded)

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
