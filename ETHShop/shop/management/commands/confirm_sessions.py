from django.core.management.base import BaseCommand, CommandError
from shop.models import Session
from django.utils import timezone
from django.conf import settings
from shop.utils import receipt_to_r_s_v, transaction_hasher, decode_contract_call
import json
import logging
from web3 import Web3, HTTPProvider
from eth_utils import int_to_big_endian, decode_hex, encode_hex
import time


w3 = Web3(HTTPProvider(settings.ETHERUM_NETWORK_ADDRESS))
with open(settings.COMPILED_CONTRACT_PATH, 'r') as f:
    contract_data = json.load(f)


logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    def __init__(self):
        super(Command, self).__init__()
        self.contract = w3.eth.contract(
            address=w3.toChecksumAddress(settings.ETHERUM_CONTRACT_ADDRESS),
            abi=contract_data['abi']
        )

    def valid_tx(self, session, tx):
        if tx['from'].lower() != '0x' + session.etherum_address.lower():
            logging.info('Session id: %s failed because %s != %s', '0x' + session.session_id, tx['from'], '0x' + session.etherum_address)
            return False
        if tx['to'].lower() != settings.ETHERUM_CONTRACT_ADDRESS.lower():
            logging.info('Session id: %s failed because %s != %s', '0x' + session.session_id, tx['to'], settings.ETHERUM_CONTRACT_ADDRESS)
            return False

        function_name, args = decode_contract_call(contract_data['abi'], tx['input'])
        if function_name != 'startSession':
            logging.info('Session id: %s failed because %s != %s', '0x' + session.session_id, function_name, 'startSession')
            return False
        if len(args) != 1:
            logging.info('Session id: %s failed because %s != %s', '0x' + session.session_id, str(len(args)), '1')
            return False
        session_id = encode_hex(args[0]).lower()
        if session_id != '0x' + session.session_id.lower():
            logging.info('Session id: %s failed because %s != %s', '0x' + session.session_id, session_id, '0x' + session.session_id)
            return False
        return True


    def confirm_sessions(self):
        for session in Session.objects.filter(confirmed=False, expires__gt=timezone.now()):
            tx = w3.eth.getTransaction(decode_hex('0x' + session.tx_hash))
            if tx:
                if self.valid_tx(session, tx):
                    session.confirmed = True;
                else:
                    session.expires = timezone.now() - timezone.timedelta(hours=1)
                session.save()


    def handle(self, *args, **kwargs):
        while True:
            self.confirm_sessions()
            time.sleep(5)
