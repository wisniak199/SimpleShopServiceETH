from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from web3 import Web3, HTTPProvider
from django.conf import settings
import json
from shop.management.commands.cash_sessions import Command as CashSessionsCommand
from shop.models import Session
from shop.utils import transaction_data_hasher, transaction_hasher, receipt_to_r_s_v, is_valid_receipt
from eth_utils import keccak, encode_hex, decode_hex, to_checksum_address, big_endian_to_int


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


class CashSessionTest(TestCase):
    @patch('shop.management.commands.cash_sessions.settings.ETHERUM_CONTRACT_ADDRESS', contract_address)
    @patch('shop.management.commands.cash_sessions.settings.ETHERUM_OWNER_ADDRESS', owner_address)
    @patch('shop.management.commands.cash_sessions.w3', w3)
    def test_cash_session(self):
        etherum_address = client_address
        session_id = '0x3129042299270b945ba819991b82d07285772951e5e99060e044e1eb09cf5f64'
        value = 1
        event_filter = contract.events.StartSession.createFilter(fromBlock=0)

        tx = contract.functions.startSession(session_id).transact({'from': etherum_address, 'value': w3.toWei('2', 'ether')})
        w3.eth.waitForTransactionReceipt(tx)
        msg = transaction_data_hasher(value, session_id)
        receipt = encode_hex(w3.eth.sign(etherum_address, msg))
        print(event_filter.get_all_entries())

        Session.objects.create(
            session_id=session_id[2:],
            etherum_address=etherum_address[2:],
            receipt=receipt[2:],
            receipt_value=value,
            expires=timezone.now() - timezone.timedelta(hours=1)
        )
        CashSessionsCommand().handle()
        self.assertEqual(Session.objects.all().count(), 0)
