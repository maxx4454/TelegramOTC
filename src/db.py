import sqlite3


class Database:
    __connection_user = sqlite3.connect('./resources/user_data.db', check_same_thread=False)
    __connection_market = sqlite3.connect('./resources/market_data.db', check_same_thread=False)
    __connection_verified = sqlite3.connect('./resources/verified_data.db', check_same_thread=False)

    # creates db, restarts if force = True
    def init(self, force=False):

        if force:
            conn_user = self.__connection_user
            conn_market = self.__connection_market
            conn_verified = self.__connection_verified

            cur_user = conn_user.cursor()
            cur_market = conn_market.cursor()
            cur_verified = conn_verified.cursor()

            if force:
                cur_user.execute('DROP TABLE user_data')
            cur_user.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    address     TEXT NOT NULL
                )
                ''')

            if force:
                cur_market.execute('DROP TABLE order_data')
            cur_market.execute('''
                CREATE TABLE IF NOT EXISTS order_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    side        TEXT,
                    amount      INTEGER,
                    price       INTEGER,
                    item        TEXT,
                    credentials TEXT
                )
                ''')

            if force:
                # pass
                cur_verified.execute('DROP TABLE verified_data')
                cur_verified.execute('DROP TABLE item_data')
            cur_verified.execute('''
                CREATE TABLE IF NOT EXISTS verified_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    side        TEXT,
                    amount      INTEGER,
                    price       INTEGER,
                    item        TEXT,
                    credentials TEXT
                )
                ''')
            cur_verified.execute('''
                            CREATE TABLE IF NOT EXISTS item_data (
                                id          INTEGER NOT NULL PRIMARY KEY,
                                item        TEXT,
                                item_type   TEXT
                            )
                            ''')

            conn_user.commit()
            conn_verified.commit()
            conn_market.commit()

            print('dropped')

    # moves order which is the first in the list to the verified orders table
    def verify_first_unverified(self, order_id):
        conn_verified = self.__connection_verified
        c_verified = conn_verified.cursor()
        conn_market = self.__connection_market
        c_market = conn_market.cursor()

        c_market.execute(
            f'SELECT user_id, side, amount, price, item, credentials FROM order_data WHERE Id = "{order_id}" ')
        temp = c_market.fetchone()
        print(temp)
        c_verified.execute(
            'INSERT INTO verified_data (user_id, side, amount, price, item, credentials) VALUES (?, ?, ?, ?, ?, ?)',
            (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5]))
        c_market.execute(f'DELETE FROM order_data WHERE Id = "{order_id}"')

        conn_verified.commit()
        conn_market.commit()

    # returns True if address for a given user_id is known, false otherwise
    def find_user_address(self, user_id):
        conn = self.__connection_user
        c = conn.cursor()
        c.execute(f"SELECT user_id, address FROM user_data WHERE user_id = '{user_id}'")
        if len(c.fetchall()) > 0:
            return True
        else:
            return False

    # function called when the order placed isnt fulfilled, deletes the order from unverified table
    def delete_first_unverified(self, order_id):
        conn = self.__connection_market
        c = conn.cursor()
        c.execute(f'DELETE FROM order_data WHERE Id = "{order_id}"')
        conn.commit()

    # txt file with items -> array
    def read_items(self):
        conn_v = self.__connection_verified
        c_v = conn_v.cursor()
        c_v.execute(
            "SELECT item FROM item_data")
        return c_v.fetchall()

    # returns all orders for user_id, including unverified
    def find_active_orders(self, user_id: int):
        list = []
        conn_v = self.__connection_verified
        c_v = conn_v.cursor()
        c_v.execute(
            f"SELECT id, side, amount, item, price FROM verified_data WHERE user_id = '{user_id}' ORDER BY item")
        res1 = c_v.fetchall()
        conn = self.__connection_market
        c = conn.cursor()
        c.execute(f"SELECT id, side, amount, item, price FROM order_data WHERE user_id = '{user_id}' ORDER BY item")
        res2 = c.fetchall()
        for item in res1:
            list.append(item)
        for item in res2:
            list.append(item)
        return list

    # returns lisst of all unverified orders
    def find_unverified(self):
        list = []
        conn = self.__connection_market
        c = conn.cursor()
        c.execute('SELECT id, user_id, side, amount, item, credentials FROM order_data ORDER BY id')
        res = c.fetchall()
        for row in res:
            list.append(row)
        return list

    # appends address to a user
    def add_address(self, user_id: int, address: str):
        conn = self.__connection_user
        c = conn.cursor()
        c.execute('INSERT INTO user_data (user_id, address) VALUES (?, ?)', (user_id, address))
        conn.commit()

    # user_ud -> address
    def return_address(self, user_id: int):
        conn = self.__connection_user
        c = conn.cursor()
        c.execute(f"SELECT address FROM user_data WHERE user_id == '{user_id}'")
        res = c.fetchone()

        return res

    def remove_address(self, user_id: int):
        conn = self.__connection_user
        c = conn.cursor()
        c.execute(f"DELETE FROM user_data WHERE user_id == '{user_id}'")
        conn.commit()

    # returns account credential for an unverified order with id = Id
    def return_credentials(self, Id: int):
        conn = self.__connection_market
        c = conn.cursor()
        c.execute(f"SELECT credentials FROM order_data WHERE id == '{Id}'")
        res = c.fetchall()
        # надо сделать проверку если адресов дали несколько и вообще не давать записывать несколько от одного юзера
        if len(res) > 0:
            return res[0]
        return None

    # inserts _order into unverified table
    def add_to_unverified(self, _order: dict):
        conn = self.__connection_market
        c = conn.cursor()

        c.execute('INSERT INTO order_data (user_id, item, side, amount, price, credentials) VALUES (?, ?, ?, ?, ?, ?)',
                  (_order['user_id'], _order['item'], _order['side'], _order['amount'], _order['price'],
                   _order['credentials']))

        conn.commit()

    # inserts _order into unverified table
    def add_to_verified(self, _order: dict):
        conn = self.__connection_verified
        c = conn.cursor()

        c.execute(
            'INSERT INTO verified_data (user_id, item, side, amount, price, credentials) VALUES (?, ?, ?, ?, ?, ?)',
            (_order['user_id'], _order['item'], _order['side'], _order['amount'], _order['price'],
             _order['credentials']))

        conn.commit()

    def get_best_offers(self, item: str):
        conn = self.__connection_verified
        c = conn.cursor()
        c.execute(
            f'SELECT item, side, amount, price FROM verified_data WHERE side = "buy" AND item = "{item}" ORDER BY price DESC LIMIT 5')
        best_buy_orders = c.fetchall()

        c.execute(
            f'SELECT item, side, amount, price FROM verified_data WHERE side = "sell" AND item = "{item}" ORDER BY price ASC LIMIT 5')
        best_sell_orders = c.fetchall()

        return best_buy_orders, best_sell_orders

    # takes item string as input, returns best sell order: tuple (id, amount) for given item from confirmed offers
    def find_best_sell_offer(self, item: str):
        conn = self.__connection_verified
        c = conn.cursor()
        # c_market.execute('SELECT user_id, side, amount, item FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
        c.execute(
            f'SELECT id, price, amount FROM verified_data WHERE item = "{item}" AND price = (SELECT MIN(price) FROM verified_data WHERE side = "SELL") AND side = "SELL"')
        sell_offers = c.fetchone()
        if sell_offers:
            return sell_offers[0]
        return None

    # takes item string as input, returns best buy order: tuple (id, amount) for given item from confirmed offers
    def find_best_buy_offer(self, item: str):
        conn = self.__connection_verified
        c = conn.cursor()
        # c_market.execute('SELECT user_id, side, amount, item FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
        c.execute(
            f'SELECT id, price, amount FROM verified_data WHERE item = "{item}" AND price = (SELECT MAX(price) FROM verified_data WHERE side = "BUY") AND side = "BUY"')
        buy_offers = c.fetchone()
        if buy_offers:
            return buy_offers[0]
        return None

    def remove_id(self, _id: int):
        conn = self.__connection_verified
        c = conn.cursor()
        c.execute(f"DELETE FROM verified_data WHERE Id = '{_id}'")
        conn.commit()

    # True if finds item False otherwise
    def find_item(self, item: str):
        items = self.read_items()
        for it in items:
            if it == item:
                return True
                # conn = self.__connection_verified
                # c = conn.cursor()
                # c.execute(f"SELECT side, amount, price FROM verified_data WHERE item = '{item}' ORDER BY side")
                # res = c.fetchall()
                # return res
        return False

    def create_item(self, item, item_type):
        conn = self.__connection_verified
        c = conn.cursor()
        c.execute('INSERT INTO item_data (item, item_type) VALUES (?, ?)', (item, item_type))

        conn.commit()
