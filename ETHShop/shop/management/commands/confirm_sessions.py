from django.core.management.base import BaseCommand, CommandError
from shop.models import Session
from django.utils import timezone
from django.conf import settings
from shop.utils import receipt_to_r_s_v, transaction_hasher
import json
from web3 import Web3, HTTPProvider
from eth_utils import int_to_big_endian, decode_hex
import time


w3 = Web3(HTTPProvider(settings.ETHERUM_NETWORK_ADDRESS))
with open(settings.COMPILED_CONTRACT_PATH, 'r') as f:
    contract_data = json.load(f)

class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.contract = w3.eth.contract(
            address=w3.toChecksumAddress(settings.ETHERUM_CONTRACT_ADDRESS),
            abi=contract_data['abi']
        )


    def handle(self, *args, **kwargs):
        event_filter = self.contract.events.StartSession.createFilter(fromBlock=0)
        while True:
            print(event_filter.get_all_entries())
            time.sleep(5)
