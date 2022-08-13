import sqlite3


class Database:
    __connection_user = sqlite3.connect('user_data.db', check_same_thread=False)
    __connection_market = sqlite3.connect('market_data.db', check_same_thread=False)
    __connection_verified = sqlite3.connect('verified_data.db', check_same_thread=False)

    # creates db, restarts if force = True
    def Database(self, force: bool = False):
        if force:
            conn_user = self.__connection_user
            conn_market = self.__connection_market
            conn_verified = self.__connection_verified

            cur_user = conn_user.cursor()
            cur_market = conn_market.cursor()
            cur_verified = conn_verified.cursor()

            if force:
                cur_user.execute('DROP TABLE IF EXISTS user_data')
            cur_user.execute('''
                CREATE TABLE IF NOT EXISTS user_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    address     TEXT NOT NULL
                )
                ''')

            if force:
                cur_market.execute('DROP TABLE IF EXISTS order_data')
            cur_market.execute('''
                CREATE TABLE IF NOT EXISTS order_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    side        TEXT,
                    amount      INTEGER,
                    item        TEXT,
                    credentials TEXT
                )
                ''')

            if force:
                cur_verified.execute('DROP TABLE IF EXISTS verified_data')
            cur_verified.execute('''
                CREATE TABLE IF NOT EXISTS verified_data (
                    id          INTEGER NOT NULL PRIMARY KEY,
                    user_id     INTEGER NOT NULL,
                    side        TEXT,
                    amount      INTEGER,
                    item        TEXT,
                    credentials TEXT
                )
                ''')

            conn_user.commit()
            conn_verified.commit()
            conn_market.commit()

    # moves order which is the first in the list to the verified orders table
    def verify_first_unverified(self):
        conn_verified = self.__connection_verified
        c_verified = conn_verified.cursor()
        conn_market = self.__connection_market
        c_market = conn_market.cursor()

        c_market.execute(
            'SELECT user_id, side, amount, item, credentials FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
        temp = c_market.fetchall()
        print(temp)
        c_verified.execute(
            'INSERT INTO verified_data (user_id, side, amount, item, credentials) VALUES (?, ?, ?, ?, ?)',
            (temp[0][0], temp[0][1], temp[0][2], temp[0][3], temp[0][4]))
        c_market.execute('DELETE FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')

        conn_verified.commit()
        conn_market.commit()

        return True

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
    def delete_first_unverified(self):

        conn = self.__connection_market
        c = conn.cursor()
        c.execute('DELETE FROM order_data WHERE id = (SELECT MIN(id) FROM order_data)')
        conn.commit()
        # for row in res:
        #     if item in row[object]:
        #         list.append(row)
        return True

    # returns all orders for given item
    # TODO: po-pidorski wa och cdelano nado cmortet polnoe sovpadenie
    def find_item(self, item: str):
        items = self.read_items()
        for i in items:
            if item in i:
                conn = self.__connection_verified
                c = conn.cursor()
                c.execute(f"SELECT side, amount FROM verified_data WHERE item = '{i}' ORDER BY side")
                res = c.fetchall()
                return res
        return None

    # txt file with items -> array
    def read_items(self):
        arr = list()
        with open('items.txt', 'r') as file:
            arr = file.read().split('\n')
        return arr

    # returns all orders for user_id, including unverified
    def find_active_orders(self, user_id: int):
        list = []
        conn_v = self.__connection_verified
        c_v = conn_v.cursor()
        c_v.execute(f"SELECT id, side, amount, item FROM verified_data WHERE user_id = '{user_id}' ORDER BY item")
        res1 = c_v.fetchall()
        conn = self.__connection_market
        c = conn.cursor()
        c.execute(f"SELECT id, side, amount, item FROM order_data WHERE user_id = '{user_id}' ORDER BY item")
        res2 = c.fetchall()
        list.append(res1)
        list.append(res2)
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
        res = c.fetchall()

        return res

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
    def add_params(self, _order: dict):
        conn = self.__connection_market
        c = conn.cursor()

        c.execute('INSERT INTO order_data (user_id, item, side, amount, price, credentials) VALUES (?, ?, ?, ?, ?, ?)',
                  (_order['user_id'], _order['item'], _order['side'], _order['amount'], _order['price'],
                   _order['credentials']))

        conn.commit()
