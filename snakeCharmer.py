import json
from dotenv import load_dotenv
from security2go import Security2GoSigner
from web3.auto import w3
from web3_utils import sign_and_send_transaction
from eth_account import Account
from altimu import Altimu
import time
import os
 
class EnvironmentManager:
    def __init__(self):
        load_dotenv()
 
    def getenv_or_raise(self, key):
        value = os.getenv(key)
        if value is None:
            raise Exception(f'{key} variable not found in the env')
        return value
 
class ContractManager:
 
    def __init__(self, w3, envman):
        with open('abi.json') as f:
            abi = json.load(f)
            contract_address = env_manager.getenv_or_raise('CONTRACT_ADDRESS')
            self.contract = w3.eth.contract(address=contract_address, abi=abi)
 
    def get_contract(self):
        return self.contract
 
    def get_start_delivery(self):
        return self.contract.get_function_by_name('start_delivery')
 
    def get_contractor(self):
        contractor_func = self.contract.get_function_by_name('contractor')
        return contractor_func().call()
     
    def get_final_payment(self):
        payment_func = self.contract.get_function_by_name('final_payment')
        return payment_func().call()
     
    def has_ended(self):
        ended_func = self.contract.get_function_by_name('ended')
        return ended_func().call()
 
    def get_store_measurements(self):
        return self.contract.get_function_by_name('store_measurements')
 
    def start_delivery(self, signer, w3):
        start_func = self.get_start_delivery()
        tx = signer.sign_send_and_wait(start_func, w3)
        print("Delivery started, hash:", tx)
 
    def store_measurements(self, value, time, signer, w3):
        store_func = self.get_store_measurements()
        tx = signer.sign_send_and_wait(store_func, w3, value, time)
        print("Delivery started, hash:", tx)
     
class Signer:
 
    def __init__(self, key_id=1):
        self.signer = Security2GoSigner(key_id=1)
        self.address = self.signer.get_address()
 
    def sign_send_and_wait(self, func, w3, value=None, time=None):
        nonce = w3.eth.getTransactionCount(self.address)
        if(value is None):
            raw_tx = func().buildTransaction({'nonce': nonce, 'gasPrice': 0, 'gas': 210000, 'from': self.address})
        else:
            raw_tx = func(value, time).buildTransaction({'nonce': nonce, 'gasPrice': 0, 'gas': 210000, 'from': self.address})
        tx = sign_and_send_transaction(w3, self.signer, self.address, raw_tx, nonce)
        w3.eth.waitForTransactionReceipt(tx)
        return tx
 
env_manager = EnvironmentManager()
signer = Signer()
 
if not w3.isConnected():
    raise Exception(f'web3 connection failed')
 
alt = Altimu()
alt.configure()
 
contract_manager = ContractManager(w3, env_manager)
 
while contract_manager.get_contractor() == '0x0000000000000000000000000000000000000000':
    print("Waiting for a contractor to accept the conditions")
    time.sleep(10.0)
 
contract_manager.start_delivery(signer, w3)
 
while not contract_manager.has_ended():
    now = int(time.time())
    x = int(alt.read_temperature()*1000)
    print("Temperature:", x, "Time:", now)
    contract_manager.store_measurements(x, now, signer, w3)
    time.sleep(10.0)
 
print("The delivery has ended, final payment:", contract_manager.get_final_payment())
alt.close_connection()