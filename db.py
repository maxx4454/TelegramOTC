import sqlite3

__connection_user = None
__connection_verified = None
__connection_market = None


def get_connection_user():
    global __connection_user
    if __connection_user is None:
        __connection_user = sqlite3.connect('user_data.db', check_same_thread=False)
    return __connection_user


def get_connection_market():
    global __connection_market
    if __connection_market is None:
        __connection_market = sqlite3.connect('market_data.db', check_same_thread=False)
    return __connection_market


def get_connection_verified():
    global __connection_verified
    if __connection_verified is None:
        __connection_verified = sqlite3.connect('verified_data.db', check_same_thread=False)
    return __connection_verified


def init_db(force: bool = False):
    conn_user = get_connection_user()
    conn_market = get_connection_market()
    conn_verified = get_connection_verified()

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


def verify_first_unverified():
    conn_verified = get_connection_verified()
    c_verified = conn_verified.cursor()
    conn_market = get_connection_market()
    c_market = conn_market.cursor()

    c_market.execute('SELECT user_id, side, amount, item, credentials FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')
    temp = c_market.fetchall()
    print(temp)
    c_verified.execute('INSERT INTO verified_data (user_id, side, amount, item, credentials) VALUES (?, ?, ?, ?, ?)', (temp[0][0], temp[0][1], temp[0][2],  temp[0][3], temp[0][4]))
    c_market.execute('DELETE FROM order_data WHERE Id = (SELECT MIN(Id) FROM order_data)')

    conn_verified.commit()
    conn_market.commit()

    return True


def find_user_address(user_id):
    conn = get_connection_user()
    c = conn.cursor()
    c.execute(f"SELECT user_id, address FROM user_data WHERE user_id = '{user_id}'")
    if len(c.fetchall()) > 0:
        return True
    else:
        return False


def delete_first_unverified():

    conn = get_connection_market()
    c = conn.cursor()
    c.execute('DELETE FROM order_data WHERE id = (SELECT MIN(id) FROM order_data)')
    conn.commit()
    # for row in res:
    #     if item in row[object]:
    #         list.append(row)
    return True


def find_item(item: str):
    items = read_items()
    for i in items:
        if item in i:
            conn = get_connection_verified()
            c = conn.cursor()
            c.execute(f"SELECT side, amount FROM verified_data WHERE item = '{i}' ORDER BY side")
            res = c.fetchall()
            return res
    return None




def read_items():
    arr = list()
    with open('items.txt', 'r') as file:
        arr = file.read().split('\n')
    return arr


def find_active_orders(user_id: int):
    list = []
    conn_v = get_connection_verified()
    c_v = conn_v.cursor()
    c_v.execute(f"SELECT id, side, amount, item FROM verified_data WHERE user_id = '{user_id}' ORDER BY item")
    res1 = c_v.fetchall()
    conn = get_connection_market()
    c = conn.cursor()
    c.execute(f"SELECT id, side, amount, item FROM order_data WHERE user_id = '{user_id}' ORDER BY item")
    res2 = c.fetchall()
    list.append(res1)
    list.append(res2)
    return list


def find_unverified():
    list = []
    conn = get_connection_market()
    c = conn.cursor()
    c.execute('SELECT id, user_id, side, amount, item, credentials FROM order_data ORDER BY id')
    res = c.fetchall()
    for row in res:
        list.append(row)
    return list


def add_address(user_id: int, address: str):
    conn = get_connection_user()
    c = conn.cursor()
    c.execute('INSERT INTO user_data (user_id, address) VALUES (?, ?)', (user_id, address))
    conn.commit()


def return_address(user_id: int):
    conn = get_connection_user()
    c = conn.cursor()
    c.execute(f"SELECT address FROM user_data WHERE user_id == '{user_id}'")
    res = c.fetchall()

    return res


def return_credentials(Id: int):
    conn = get_connection_market()
    c = conn.cursor()
    c.execute(f"SELECT credentials FROM order_data WHERE id == '{Id}'")
    res = c.fetchall()
    # надо сделать проверку если адресов дали несколько и вообще не давать записывать несколько от одного юзера
    if len(res) > 0:
        return res[0]
    return None


def add_params(user_id: int, params: list):
    conn = get_connection_market()
    c = conn.cursor()
    if len(params) == 4:
        c.execute('INSERT INTO order_data (user_id, item, side, amount, credentials) VALUES (?, ?, ?, ?, ?)', (user_id, params[0], params[1], params[2], params[3]))
    else:
        c.execute('INSERT INTO order_data (user_id, item, side, amount, credentials) VALUES (?, ?, ?, ?, ?)',
                  (user_id, params[0], params[1], params[2], None))
    conn.commit()


if __name__ == "__main__":
    init_db()


