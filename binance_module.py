import logging

from binance.spot import Spot as Client
from binance.lib.utils import config_logging


class Deposits:
    def __init__(self):
        self.key = 'GQHP7JzHIyCINjBDI9H9S12VYtIm5lZvhV6Bxjp0ypRnkYm073Mll88YWomTZXI4'
        self.secret = 'Fa5cVO90wPEiIPqhRUuWVIfVCQ4Bx23qbUr1LP7bKIzbEQQ4cnZRF9GZmCwiPAN6'
        self.address = '0xad0625b44debf3a1b76acec973fb051ee8b2fa5f'
        self.spot_client = Client(self.key, self.secret, show_header=True)

    @staticmethod
    def withdraw(self, amount: int, address):
        print(self.spot_client.withdraw(coin="BUSD", amount=amount, address=address))

    @staticmethod
    def check_deposit(self, amount: int, tx_id):
        last_deposits = self.spot_client.deposit_history()['data']
        for last_deposit in last_deposits:
            amount_equal = float(last_deposit['amount']) == float(amount)
            coin_equal = last_deposit['coin'] == 'BUSD'
            addr_correct = last_deposit['address'] == self.address
            tx_id_equal = last_deposit['txId'] == tx_id
            transfer_successful = int(last_deposit['status']) == 1

            if amount_equal and coin_equal and addr_correct and tx_id_equal and transfer_successful:
                return True

        return False
