import logging
import time
import blocksec2go
from blocksec2go.comm.pyscard import open_pyscard
from eth_account._utils.transactions import (
    encode_transaction,
    serializable_unsigned_transaction_from_dict
)
 
import web3_utils
 
 
class Security2GoSigner:
    def __init__(self, key_id):
        self.reader = None
        self.key_id = key_id
        self.logger = logging.getLogger('security2go')
        self.pub_key = None
        self._init()
 
    def _init(self):
        while self.reader is None:
            try:
                self.reader = open_pyscard()
            except Exception as details:
                self.logger.debug(details)
                if "No reader found" != str(details) and "No card on reader" != str(details):
                    self.logger.error(details)
                    raise Exception(f"Reader error: {details}")
                self.logger.info('Reader or card not found. Retrying in 1 second...')
                time.sleep(1)
 
        blocksec2go.select_app(self.reader)
        self.pub_key = self._get_pub_key()
        self.logger.info('Initialized security2go')
 
    def get_address(self):
        return web3_utils.address_from_public_key(self.pub_key)
 
    def sign_transaction(self, raw_transaction, chain_id):
        transaction = serializable_unsigned_transaction_from_dict(raw_transaction)
        transaction_hash = transaction.hash()
        self.logger.debug(f'Signing transaction with hash {transaction_hash.hex()}')
        signature = self._generate_signature_der(transaction_hash)
 
        r, s = web3_utils.sigdecode_der(signature)
        v = web3_utils.get_v(r, s, transaction_hash, self.pub_key, chain_id)
        encoded_transaction = encode_transaction(transaction, vrs=(v, r, s))
 
        return encoded_transaction
 
    def _generate_signature_der(self, data):
        _, _, signature = blocksec2go.generate_signature(
            self.reader, self.key_id, data
        )
        self.logger.debug('generated signature')
        return signature
 
    def _get_pub_key(self):
        _, _, pub_key = blocksec2go.get_key_info(self.reader, self.key_id)
        self.logger.debug('read public key')
        return pub_key[1:]  # remove the '0x04' prefix