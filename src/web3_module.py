import logging

import web3.exceptions
from web3 import Web3, HTTPProvider


class Bsc:
    private = ''
    public = ''
    w3 = Web3(HTTPProvider('https://bsc-dataseed1.binance.org:443'))

    @classmethod
    def withdraw(cls, amount: int, address):
        try:
            usdc = cls.w3.toChecksumAddress("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d")
            abi = [{"inputs":[{"internalType":"address","name":"logic","type":"address"},{"internalType":"address","name":"admin","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"previousAdmin","type":"address"},{"indexed":False,"internalType":"address","name":"newAdmin","type":"address"}],"name":"AdminChanged","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"implementation","type":"address"}],"name":"Upgraded","type":"event"},{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"admin","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newAdmin","type":"address"}],"name":"changeAdmin","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"implementation","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"}],"name":"upgradeTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"upgradeToAndCall","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]
            usdc_contract = cls.w3.eth.contract(usdc, abi=abi)
            nonce = cls.w3.eth.getTransactionCount(cls.public)
            print("building the tx")

            tx_to_swap = usdc_contract.functions.transfer(
                cls.w3.toChecksumAddress(address), amount * 10**18
            ).buildTransaction({
                "nonce": nonce,
                "from": cls.w3.toChecksumAddress(cls.public),
                "gas": 47_000,
                "gasPrice": int(cls.w3.eth.gas_price * 1.05),
                "value": 0
            })
            # sign tx
            signed_tx = cls.w3.eth.account.signTransaction(tx_to_swap, cls.private)
            cls.w3.eth.sendRawTransaction(signed_tx)

        except Exception as e:
            print(e)

    @classmethod
    def check_deposit(cls, amount: int, tx_id):
        try:
            tx = cls.w3.eth.get_transaction(tx_id)
            usdc = cls.w3.toChecksumAddress("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d")
            amount *= 10 ** 18
            if tx['to'] == usdc:
                # print('found somme')
                methodID = tx['input'][:10]
                addr = cls.w3.toChecksumAddress(tx['input'][34:74])
                amount_tx = int(tx['input'][74:138], 16)

                if methodID == '0xa9059cbb' and addr == cls.w3.toChecksumAddress(cls.public) and amount_tx >= amount:
                    return True
            return False
        except web3.exceptions.TransactionNotFound:
            return False
