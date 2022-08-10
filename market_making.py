from db import *


def find_best_sell_offer(item: str):
    conn = get_connection_verified()
    c = conn.cursor()
    # c_market.execute('SELECT user_id, side, amount, item FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
    c.execute(
        f"SELECT id, amount FROM verified_data WHERE item = '{item}' AND amount = (SELECT MIN(amount) FROM verified_data WHERE side = 'SELL') AND side = 'SELL'")
    sell_offers = c.fetchall()
    return sell_offers[0]


def find_best_buy_offer(item: str):
    conn = get_connection_verified()
    c = conn.cursor()
    # c_market.execute('SELECT user_id, side, amount, item FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
    c.execute(
        f"SELECT id, amount FROM verified_data WHERE item = '{item}' AND amount = (SELECT MAX(amount) FROM verified_data WHERE side = 'BUY') AND side = 'BUY'")
    buy_offers = c.fetchall()
    return buy_offers[0]


def conduct_trade(item: str):
    conn = get_connection_verified()
    c = conn.cursor()
    sell_offer = find_best_sell_offer(item)
    buy_offer = find_best_buy_offer(item)

    id_sell = sell_offer[0]
    id_buy = buy_offer()[0]
    price_sell = sell_offer[1]
    price_buy = buy_offer[1]

    if price_buy >= price_sell:
        trade(id_sell, id_buy)

        c.execute(f"DELETE FROM verified_data WHERE Id = '{id_sell}'")
        c.execute(f"DELETE FROM verified_data WHERE Id = '{id_buy}'")

        c.commit()


def trade(id_sell, id_buy):
    print('exchanged')


def market_making():
    while True:
        for item in read_items():
            conduct_trade(item)
