from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from web3 import Web3, HTTPProvider
from django.conf import settings
import json
from shop.management.commands.confirm_sessions import Command as ConfirmSessionsCommand
from shop.models import Session
from shop.utils import transaction_data_hasher, transaction_hasher, receipt_to_r_s_v, is_valid_receipt, decode_contract_call
from eth_utils import keccak, encode_hex, decode_hex, to_checksum_address, big_endian_to_int

from ethereum.abi import (
    decode_abi,
    normalize_name as normalize_abi_method_name,
    method_id as get_abi_method_id)
from ethereum.utils import encode_int, zpad, decode_hex


w3 = Web3(HTTPProvider(settings.ETHERUM_NETWORK_ADDRESS))
owner_address = w3.eth.accounts[0]
client_address = w3.eth.accounts[1]
w3.eth.defaultAccount = owner_address
with open(settings.COMPILED_CONTRACT_PATH, 'r') as f:
    contract_data = json.load(f)
StateChannel = w3.eth.contract(abi=contract_data['abi'], bytecode=contract_data['bytecode'])
tx_hash = StateChannel.constructor().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
contract_address = tx_receipt.contractAddress
contract = w3.eth.contract(
    address=contract_address,
    abi=contract_data['abi'],
)


class ConfirmSessionTest(TestCase):
    @patch('shop.management.commands.confirm_sessions.settings.ETHERUM_CONTRACT_ADDRESS', contract_address)
    @patch('shop.management.commands.confirm_sessions.settings.ETHERUM_OWNER_ADDRESS', owner_address)
    @patch('shop.management.commands.confirm_sessions.w3', w3)
    def test_confirm_session_positive(self):
        etherum_address = client_address
        session_id = '0x3129042299270b945ba819991b82d07285772951e5e99060e044e1eb09cf5f34'
        value = 0
        tx = contract.functions.startSession(session_id).transact({'from': etherum_address, 'value': w3.toWei('2', 'ether')})
        w3.eth.waitForTransactionReceipt(tx)
        msg = transaction_data_hasher(value, session_id)
        receipt = encode_hex(w3.eth.sign(etherum_address, msg))

        Session.objects.create(
            session_id=session_id[2:],
            etherum_address=etherum_address[2:],
            receipt=receipt[2:],
            receipt_value=value,
            expires=timezone.now() + timezone.timedelta(hours=12),
            tx_hash=encode_hex(tx)[2:]
        )
        self.assertFalse(Session.objects.all().first().confirmed)
        ConfirmSessionsCommand().confirm_sessions()
        self.assertTrue(Session.objects.all().first().confirmed)

    @patch('shop.management.commands.confirm_sessions.settings.ETHERUM_CONTRACT_ADDRESS', contract_address)
    @patch('shop.management.commands.confirm_sessions.settings.ETHERUM_OWNER_ADDRESS', owner_address)
    @patch('shop.management.commands.confirm_sessions.w3', w3)
    def test_confirm_session_negative(self):
        etherum_address = client_address
        session_id = '0x3129042299270b945ba819991b82d07285772951e5e99060e044e1eb09cf5f64'
        value = 0
        tx = contract.functions.startSession(session_id).transact({'from': etherum_address, 'value': w3.toWei('2', 'ether')})
        w3.eth.waitForTransactionReceipt(tx)
        msg = transaction_data_hasher(value, session_id)
        receipt = encode_hex(w3.eth.sign(etherum_address, msg))

        Session.objects.create(
            session_id=session_id[2:],
            etherum_address=etherum_address[2:],
            receipt=receipt[2:],
            receipt_value=value,
            expires=timezone.now() + timezone.timedelta(hours=12),
            tx_hash=encode_hex(tx)[2:-1] + 'b'
        )
        self.assertFalse(Session.objects.all().first().confirmed)
        ConfirmSessionsCommand().confirm_sessions()
        self.assertFalse(Session.objects.all().first().confirmed)
