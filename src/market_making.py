from db import Database
db = Database()


class MarketMaking():
    # gets best sell and buy offer for a given item and commits a trade when SELL_PRICE <= BUY_PRICE
    def conduct_trade(self, item: str):
        sell_offer = db.find_best_sell_offer(item)
        buy_offer = db.find_best_buy_offer(item)

        id_sell = sell_offer[0]
        id_buy = buy_offer()[0]
        price_sell = sell_offer[1]
        price_buy = buy_offer[1]

        if price_buy >= price_sell:
            self.trade(id_sell, id_buy)

            db.remove_id(id_sell)
            db.remove_id(id_sell)

    # TODO: should exchange cash and product between participants of the deal
    def trade(self, id_sell, id_buy):
        print('exchanged')

    # runs continuously
    # loops through all traded items and conducts trades if they are available
    def market_making(self):
        while True:
            for item in db.read_items():
                self.conduct_trade(item)
