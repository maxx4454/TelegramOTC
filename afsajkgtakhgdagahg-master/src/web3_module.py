import logging
from web3 import Web3, HTTPProvider


class Bsc:
    private = ''
    public = '0xad0625b44debf3a1b76acec973fb051ee8b2fa5f'
    w3 = Web3(HTTPProvider('https://bsc-dataseed1.binance.org:443'))


    @classmethod
    def withdraw(cls, amount: int, address):
        print(cls.spot_client.withdraw(coin="BUSD", amount=amount, address=address))

    @classmethod
    def check_deposit(cls, amount: int, tx_id):
        tx = cls.w3.eth.get_transaction(tx_id)
        tx_receipt = cls.w3.eth.get_transaction_receipt(tx_id)

        amount_equal = float(tx.value / 10**9) == float(amount)
        addr_correct = last_deposit['address'] == cls.address
        tx_id_equal = last_deposit['txId'] == tx_id
        transfer_successful = int(last_deposit['status']) == 1

        if amount_equal and coin_equal and addr_correct and tx_id_equal and transfer_successful:
            return True

        return False
