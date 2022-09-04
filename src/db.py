import sqlite3


class Database:
    __connection = sqlite3.connect('../resources/user_data.db', check_same_thread=False)
    
    # creates db, restarts if force = True
    def init(self, force=False):

        if force:
            conn = self.__connection
            cur = conn.cursor()

            try:
                cur.execute('DROP TABLE user_data')
                cur.execute('DROP TABLE order_data')
                cur.execute('DROP TABLE item_data')
            except:
                print('error dropping')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    address     TEXT NOT NULL
                )
                ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS order_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    side        TEXT,
                    amount      INTEGER,
                    price       INTEGER,
                    item        TEXT,
                    credentials TEXT,
                    verified    BOOLEAN
                )
                ''')

            cur.execute('''
                            CREATE TABLE IF NOT EXISTS item_data (
                                id          INTEGER NOT NULL PRIMARY KEY,
                                item        TEXT,
                                item_type   TEXT
                            )
                            ''')

            conn.commit()
            print('dropped')

    # moves order which is the first in the list to the verified orders table
    def verify_first_unverified(self, order_id):
        conn = self.__connection
        c_market = conn.cursor()
        c_market.execute(f'UPDATE order_data SET verified = True WHERE Id = "{order_id}" ')
        conn.commit()

    def update_price(self, order_id, new_price):
        conn = self.__connection
        c_market = conn.cursor()
        c_market.execute(f'UPDATE order_data SET price = {new_price} WHERE Id = "{order_id}"')
        conn.commit()

    def update_credentials(self, order_id, new_creds):
        conn = self.__connection
        c_market = conn.cursor()
        c_market.execute(f'UPDATE order_data SET credentials = "{new_creds}" WHERE Id = "{order_id}"')
        conn.commit()


    # returns True if address for a given user_id is known, false otherwise
    def find_user_address(self, user_id):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"SELECT user_id, address FROM user_data WHERE user_id = '{user_id}'")
        if len(c.fetchall()) > 0:
            return True
        else:
            return False

    # function called when the order placed isnt fulfilled, deletes the order from unverified table
    def delete_first_unverified(self, order_id):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f'DELETE FROM order_data WHERE Id = "{order_id}"')
        conn.commit()

    # txt file with items -> array
    def read_items(self):
        conn_v = self.__connection
        c_v = conn_v.cursor()
        c_v.execute(
            "SELECT item FROM item_data")
        return c_v.fetchall()

    # returns all orders for user_id, including unverified
    def find_orders_user(self, user_id: int):
        conn_v = self.__connection
        c_v = conn_v.cursor()
        c_v.execute(
            f"SELECT id, side, amount, item, price, verified FROM order_data WHERE user_id = '{user_id}' ORDER BY item")
        return c_v.fetchall()

    # appends address to a user
    def add_address(self, user_id: int, address: str):
        conn = self.__connection
        c = conn.cursor()
        c.execute('INSERT INTO user_data (user_id, address) VALUES (?, ?)', (user_id, address))
        conn.commit()

    # user_ud -> address
    def return_address(self, user_id: int):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"SELECT address FROM user_data WHERE user_id == '{user_id}'")
        return c.fetchone()


    def remove_address(self, user_id: int):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"DELETE FROM user_data WHERE user_id == '{user_id}'")
        conn.commit()

    # returns account credential for an unverified order with id = Id
    def return_credentials(self, Id: int):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"SELECT credentials FROM order_data WHERE id == '{Id}'")
        return c.fetchone()


    def return_order(self, Id: int):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"SELECT user_id, item, side, amount, price, credentials FROM order_data WHERE id == '{Id}'")
        return c.fetchone()

    # inserts _order into unverified table
    def add_order(self, _order: dict, verified: bool):
        conn = self.__connection
        c = conn.cursor()

        c.execute('INSERT INTO order_data (user_id, item, side, amount, price, credentials, verified) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (_order['user_id'], _order['item'], _order['side'], _order['amount'], _order['price'],
                   _order['credentials'], verified))

        conn.commit()


    def get_best_offers(self, item: str):
        conn = self.__connection
        c = conn.cursor()

        print(item)
        c.execute(
            f'SELECT item, side, amount, price FROM order_data WHERE side = "buy" AND item = "{item}" AND verified = 1 ORDER BY price DESC LIMIT 5')
        best_buy_orders = c.fetchall()
        print(best_buy_orders)

        c.execute(
            f'SELECT item, side, amount, price FROM order_data WHERE side = "sell" AND item = "{item}" AND verified = 1 ORDER BY price ASC LIMIT 5')
        best_sell_orders = c.fetchall()

        return best_buy_orders, best_sell_orders


    # takes item string as input, returns best sell order: tuple (id, amount) for given item from confirmed offers
    def find_best_sell_offer(self, item: str):
        conn = self.__connection
        c = conn.cursor()

        c.execute(
            f'SELECT id, price, amount FROM order_data WHERE item = "{item}" AND side = "sell" AND verified = 1 AND price = (SELECT MIN(price) FROM order_data WHERE side = "sell" AND verified = 1 AND item = "{item}")')

        sell_offers = c.fetchone()

        if sell_offers:
            return sell_offers
        return None

    # takes item string as input, returns best buy order: tuple (id, amount) for given item from confirmed offers
    def find_best_buy_offer(self, item: str):
        conn = self.__connection
        c = conn.cursor()

        c.execute(
            f'SELECT id, price, amount FROM order_data WHERE item = "{item}" AND verified = 1 AND price = (SELECT MAX(price) FROM order_data WHERE side = "buy" AND verified = 1 AND item = "{item}") AND side = "buy"')
        buy_offers = c.fetchone()
        if buy_offers:
            return buy_offers
        return None

    def remove_id(self, _id: int):
        conn = self.__connection
        c = conn.cursor()
        c.execute(f"DELETE FROM order_data WHERE Id = '{_id}'")
        conn.commit()

    # True if finds item False otherwise
    def find_item(self, item: str):
        items = self.read_items()
        for it in items:
            if it == item:
                return True
        return False

    def create_item(self, item, item_type):
        conn = self.__connection
        c = conn.cursor()
        c.execute('INSERT INTO item_data (item, item_type) VALUES (?, ?)', (item, item_type))

        conn.commit()

    def find_unverified(self):
        conn = self.__connection
        c = conn.cursor()
        c.execute(
            f'SELECT id, user_id, item, side, amount, price, credentials  FROM order_data WHERE verified = False')
        sell_offers = c.fetchall()
        return sell_offers
