from web3 import Web3
from ethereum.utils import ecrecover_to_pub
from eth_utils import keccak, encode_hex, decode_hex, to_checksum_address, big_endian_to_int


def ecrecover(h, v, r, s):
    pub = ecrecover_to_pub(h, v, r, s)
    addr = keccak(pub)[-20:]
    addr = encode_hex(addr)
    addr = to_checksum_address(addr)
    return addr


def transaction_data_hasher(value, session_id):
    value_hash = Web3.soliditySha3(['uint256'], [value])
    hashed_transaction = Web3.toBytes(Web3.soliditySha3(['bytes'], [Web3.toBytes(value_hash) + decode_hex(session_id)]))
    return hashed_transaction


def transaction_hasher(value, session_id):
    hashed_transaction = transaction_data_hasher(value, session_id)
    assert(len(hashed_transaction) == 32)
    msg = str.encode('\x19Ethereum Signed Message:\n32') + hashed_transaction
    return Web3.toBytes(Web3.soliditySha3(['bytes'], [msg]))


def receipt_to_r_s_v(receipt):
    assert(len(receipt) == 132)
    r = '0x' + receipt[2:66]
    r = decode_hex(r)
    r = big_endian_to_int(r)

    s = '0x' + receipt[66:130]
    s = decode_hex(s)
    s = big_endian_to_int(s)

    v = int('0x' + receipt[130:132], 16)
    if v not in [27, 28]:
        v += 27

    return r, s, v


def is_valid_receipt(receipt, etherum_address, session_id, receipt_value):
    """
    All parameters are strings representing hexes starting from 0x
    """
    r, s, v = receipt_to_r_s_v(receipt)
    h = transaction_hasher(receipt_value, session_id)
    decoded_address = ecrecover(h, v ,r , s)
    return decoded_address == etherum_address
