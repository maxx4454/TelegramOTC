from db import Database
from resources.config import *
from resources.keyboards import *
from utils import Utils

from db import Database
from web3_module import Bsc

db = Database()

bot = telebot.TeleBot(TOKEN)


class MarketMaking():
    # gets best sell and buy offer for a given item and commits a trade when SELL_PRICE <= BUY_PRICE
    def conduct_trade(self, item: str):
        try:
            sell_offer = db.find_best_sell_offer(item)
            buy_offer = db.find_best_buy_offer(item)
            if sell_offer and buy_offer:
                id_sell = sell_offer[0]
                id_buy = buy_offer()[0]
                price_sell = sell_offer[1]
                price_buy = buy_offer[1]

                if price_buy >= price_sell:
                    self.trade(id_sell, id_buy, item)


        except Exception as e:
            print(e)

    # TODO: should exchange cash and product between participants of the deal
    def trade(self, id_sell, id_buy, item):
        type, item_name = item.split('_')
        buy_order = db.return_order(id_buy)
        sell_order = db.return_order(id_sell)
        amount_buy = buy_order[3]
        amount_sell = sell_order[3]

        # >= and send creds
        if type == "allocation (locked tokens)":
            if amount_buy == amount_sell:
                self.simple_trade(buy_order, sell_order, id_buy, id_sell)

        #
        elif type == "whitelist":
            self.simple_trade(buy_order, sell_order, id_buy, id_sell)


        elif type == "social network account":
            self.simple_trade(buy_order, sell_order, id_buy, id_sell)

        # тут как на бирже надо
        elif type == "unlocked tokens (nft, testnet, etc)":
            self.simple_trade(buy_order, sell_order, id_buy, id_sell)

        elif type == "other":
            self.simple_trade(buy_order, sell_order, id_buy, id_sell)

        else:
            print("wrong type")

    def simple_trade(self, buy_order, sell_order, id_buy, id_sell):
        try:
            amount_buy = buy_order[3]
            amount_sell = sell_order[3]
            addr_sell = db.return_address(sell_order[0])
            deal_amount = min(amount_sell, amount_buy)
            leftovers = max(amount_sell, amount_buy) - min(amount_sell, amount_buy)

            # TODO: прооверка что длина крдс = amount
            creds = sell_order[5].split('\n')
            creds_order = creds[:deal_amount]

            creds_left = Utils.generate_creds_string(creds, deal_amount)

            Bsc.withdraw(buy_order[4] * deal_amount, addr_sell)
            bot.send_message(buy_order[0], creds_order)
            bot.send_message(sell_order[0], f'ur shit sold: {sell_order[1]}')

            print('exchanged')

            db.remove_id(id_sell)
            db.remove_id(id_buy)

            if leftovers > 0:
                if amount_buy > amount_sell:
                    amount_buy -= amount_sell
                    _order = {'user_id': buy_order[0], 'item': buy_order[1], 'side': 'buy', 'amount': amount_buy,
                              'price': buy_order[4], 'credentials': None}
                    db.add_to_verified(_order)
                else:
                    amount_sell -= amount_buy
                    _order = {'user_id': sell_order[0], 'item': sell_order[1], 'side': 'sell', 'amount': amount_sell,
                              'price': sell_order[4], 'credentials': creds_left}

                    bot.send_message(buy_order[0], 'Сделка прошла успешна, отправляю твой товар')
                    with open('../resources/new_credentials/new.txt', 'w') as file:
                        file.write('') # строка с новыми credentials
                    bot.send_document(buy_order[0], file)

                    db.add_to_verified(_order)

            print('db work finished')
        except Exception as e:
            print(e)

    # runs continuously
    # loops through all traded items and conducts trades if they are available
    def market_making(self):
        while True:
            for item in db.read_items():
                self.conduct_trade(item)
