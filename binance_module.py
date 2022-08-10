import logging

from binance.spot import Spot as Client
from binance.lib.utils import config_logging

key = 'GQHP7JzHIyCINjBDI9H9S12VYtIm5lZvhV6Bxjp0ypRnkYm073Mll88YWomTZXI4'
secret = 'Fa5cVO90wPEiIPqhRUuWVIfVCQ4Bx23qbUr1LP7bKIzbEQQ4cnZRF9GZmCwiPAN6'
spot_client = Client(key, secret, show_header=True)


def withdraw(amount: int, address):
    print(spot_client.withdraw(coin="BUSD", amount=amount, address=address))


def check_deposit(amount: int, tx_id):
    address = '0xad0625b44debf3a1b76acec973fb051ee8b2fa5f'
    last_deposit = spot_client.deposit_history()['data'][0]
    print(last_deposit)
    if float(last_deposit['amount']) == float(amount) and last_deposit['coin'] == 'BUSD' and last_deposit[
        'address'] == add0ress and int(last_deposit['status']) == 1 and last_deposit['txId'] == tx_id:
        return True
    else:
        return False
