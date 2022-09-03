import logging

import web3.exceptions
from web3 import Web3, HTTPProvider
from resources.config import *


class Bsc:
    private = '203366f5550c5131ccdb3094f8ab6d81874e56028ce01641f7301feebc6bc47a'
    public = '0xeBf029D90D2b0396cF1d12275bbB51E34D3F6DCB'
    w3 = Web3(HTTPProvider('https://bsc-dataseed1.binance.org:443'))

    @classmethod
    def withdraw(cls, amount: int, address):
        try:

            usdc = cls.w3.toChecksumAddress("0xBA5Fe23f8a3a24BEd3236F05F2FcF35fd0BF0B5C")
            abi = [{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint8","name":"decimals","type":"uint8"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bool","name":"mintable","type":"bool"},{"internalType":"address","name":"owner","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"mintable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]
            usdc_contract = cls.w3.eth.contract(usdc, abi=abi)
            nonce = cls.w3.eth.getTransactionCount(cls.public)
            print("building the tx")
            print(amount, address[0])
            tx_to_swap = usdc_contract.functions.transfer(
                cls.w3.toChecksumAddress(address[0]), amount * 10**18
            ).buildTransaction({
                "nonce": nonce,
                "from": cls.w3.toChecksumAddress(cls.public),
                "gas": 47_000,
                "gasPrice": int(cls.w3.eth.gas_price * 1.05),
                "value": 0
            })
            # sign tx
            signed_tx = cls.w3.eth.account.signTransaction(tx_to_swap, cls.private)
            cls.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        except Exception as e:
            print(e)

    @classmethod
    def check_deposit(cls, amount: int, tx_id):
        try:
            tx = cls.w3.eth.get_transaction(tx_id)
            usdc = cls.w3.toChecksumAddress(cls.w3.toChecksumAddress("0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"))
            amount *= 10 ** 18
            receipt = cls.w3.eth.getTransactionReceipt(tx_id)
            
            if not receipt['status']:
                return False
                
            if tx['to'] == usdc:
                methodID = tx['input'][:10]
                addr = cls.w3.toChecksumAddress(tx['input'][34:74])
                amount_tx = int(tx['input'][74:138], 16)

                if methodID == '0xa9059cbb' and addr == cls.w3.toChecksumAddress(cls.public) and amount_tx >= amount:
                    return True
            return False
        except web3.exceptions.TransactionNotFound:
            return False
