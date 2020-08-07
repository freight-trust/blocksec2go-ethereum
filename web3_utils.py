import ecdsa
from web3 import Web3
 
generator = ecdsa.SECP256k1.generator
 
def sigdecode_der(sig):
    n = generator.order()
    return ecdsa.util.sigdecode_der(sig, n)
 
 
def find_recovery_id(r, s, hash, pub_key):
    vk = ecdsa.VerifyingKey.from_string(pub_key, curve=ecdsa.SECP256k1)
    sig = ecdsa.ecdsa.Signature(r, s)
    hash_number = ecdsa.util.string_to_number(hash)
    public_keys = sig.recover_public_keys(hash_number, generator)
    vk_point = vk.pubkey.point
    if public_keys[0].point == vk_point:
        return 0
    elif public_keys[1].point == vk_point:
        return 1
    return None
 
 
def address_from_public_key(public_key):
    pk_hash = Web3.keccak(public_key)
    address_bytes = pk_hash[-20:]
    address = address_bytes.hex()
    return Web3.toChecksumAddress(address)
 
 
def get_v(r, s, unsigned_transaction_hash, pub_key, chain_id):
    recovery_id = find_recovery_id(r, s, unsigned_transaction_hash, pub_key)
    return 35 + recovery_id + (chain_id * 2)
 
 
def sign_and_send_transaction(web3, signer, address, raw_transaction, nonce):
    raw_transaction["nonce"] = nonce
    if 'from' in raw_transaction:
        del raw_transaction['from']
 
    chain_id = web3.eth.chainId
    signed_transaction = signer.sign_transaction(
        raw_transaction, chain_id
    )
 
    tx_hash = web3.eth.sendRawTransaction(signed_transaction)
 
    return tx_hash.hex()