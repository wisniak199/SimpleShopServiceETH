from django.core.management.base import BaseCommand, CommandError
from shop.models import Session
from django.utils import timezone
from django.conf import settings
from shop.utils import receipt_to_r_s_v, transaction_hasher
import json
from web3 import Web3, HTTPProvider
from eth_utils import int_to_big_endian, decode_hex


w3 = Web3(HTTPProvider(settings.ETHERUM_NETWORK_ADDRESS))
with open(settings.COMPILED_CONTRACT_PATH, 'r') as f:
    contract_data = json.load(f)

class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.contract = w3.eth.contract(
            address=settings.ETHERUM_CONTRACT_ADDRESS,
            abi=contract_data['abi']
        )


    def cash_receipt(self, receipt, receipt_value, session_id, etherum_address):
        r, s, v = receipt_to_r_s_v(receipt)
        h = transaction_hasher(receipt_value, session_id)
        r = int_to_big_endian(r)
        s = int_to_big_endian(s)
        session_id = decode_hex(session_id)
        self.contract.functions.endSession(h, v, r, s, receipt_value, session_id).call({'from': settings.ETHERUM_OWNER_ADDRESS})


    def handle(self):
        for session in Session.objects.filter(expires__lt=timezone.now()):
            self.cash_receipt('0x' + session.receipt, session.receipt_value, '0x' + session.session_id, '0x'+session.etherum_address)
            session.delete()
