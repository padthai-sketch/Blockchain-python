# Import neccessary libraries
import subprocess
import json
import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.gas_strategies.time_based import medium_gas_price_strategy
from eth_account import Account
from constants import *
from dotenv import load_dotenv
load_dotenv()

# Import Mnemonic key from an environment variable
mnemonic = os.getenv('MNEMONIC', 'fame size ladder slide betray silver bless wreck raise nose spider metal')

# Create functions that derives the wallet keys 
def derive_wallets(mnemonic, coin, numderive):
    command = f'./derive -g --mnemonic="{mnemonic}" --cols=all --coin={coin} --numderive={numderive} --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    keys = json.loads(output)
    return keys

# Store three constants in 'coins' variable 
coins = {
    ETH: derive_wallets(mnemonic, ETH, 3),
    BTCTEST: derive_wallets(mnemonic, BTCTEST, 3),
    BTC: derive_wallets(mnemonic, BTC, 3)
} 

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

private_key = os.getenv("PRIVATE_KEY")

# Initiate the private keys for ETH and BTCTEST 
keys = {}
for coin in coins:
    keys[coin]= derive_wallets(mnemonic, coin, numderive=3)

eth_priv_key = keys['eth'][0]['privkey']
btc_test_priv_key = keys['btc-test'][0]['privkey']

print(f" ETH Private Key: {eth_priv_key}")
print(f" BTC Test Private Key: {btc_test_priv_key}")

# Define function to convert the privkey string to an account object
def priv_key_to_account(coin, priv_key):
    private_key = os.getenv("PRIVATE_KEY")
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# Create function that contains all metadata needed for transaction
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": eth_account.address, "to": recipient, "value": amount}
    )
        return {
            "from": eth_account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_account.address)}
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create function to sign the transaction
eth_account = priv_key_to_account(ETH, derive_wallets(mnemonic, ETH, 6)[0]['privkey'])
btc_test_account = priv_key_to_account(BTCTEST,btc_test_priv_key)

def send_tx(coin, account, to, amount):
    tx = create_tx(coin, account, recipient, amount)
    
    if coin == ETH:
        signed_tx = eth_account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(result.hex())
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    elif coin == BTCTEST:
        tx_btc_test = create_tx(coin, account, recipient, amount)
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed)
