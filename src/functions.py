from market_making import *

bt = Buttons()

db.init()


class Order:
    _order = {}
    _adm_order = {}
    _change_order_id = 0

    # Обрабатывает нажатие на кнопку мои ордера
    def get_my_orders(self, user_id):
        buy_orders = ''
        sell_orders = ''
        unverified_orders = ''
        orders = db.find_active_orders(user_id)
        unverified = [] # должен быть массив из неверифицированных ордеров
        if len(orders) != 0:
            for index, order in enumerate(orders):
                if order in unverified:
                    unverified += f'{index + 1} - Тип_товар: {order[3]}, Количество: {str(order[2])}, Цена: {str(order[4])}\n'
                else:
                    if order[1] == 'buy':
                        buy_orders += f'{index + 1} - Тип_товар: {order[3]}, Количество: {str(order[2])}, Цена: {str(order[4])}\n'
                    else:
                        sell_orders += f'{index + 1} - Тип_товар: {order[3]}, Количество: {str(order[2])}, Цена: {str(order[4])}\n'
            bot.send_message(user_id, '<b>Твои ордера на покупку:</b>\n\n' + buy_orders, parse_mode='html')
            bot.send_message(user_id, '<b>Твои <i>верифицированные</i> ордера на продажу:</b>\n\n' + sell_orders, parse_mode='html')
            bot.send_message(user_id, '<b>Твои <i>неверифицированные</i> ордера на продажу:</b>\n\n' + sell_orders, parse_mode='html')
            bot.send_message(user_id, 'Напиши номер ордера (число слева) который хочешь изменить или 0 чтобы вернуться',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
        else:
            bot.send_message(user_id, 'У тебя нет активных ордеров')
            bot.send_message(user_id, 'Главное меню', reply_markup=main)

    def manage(self, user_id, msg):
        orders = db.find_active_orders(user_id)
        if msg == '0':
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        else:
            order_id = int(msg) - 1
            self._change_order_id = order_id
            bot.send_message(user_id,
                             f'{order_id} - Тип_товар: {orders[order_id][3]}, Количество: {str(orders[order_id][2])}, Цена: {str(orders[order_id][4])}\n')
            bot.send_message(user_id, 'Что ты хочешь изменить в этом ордере?', reply_markup=buttons_manage)

    def change_order(self, user_id, msg):
        if msg == bt.change_price:
            bot.send_message(user_id, 'Напиши новую желаемую цену', reply_markup=telebot.types.ReplyKeyboardRemove())
        if msg == bt.cancel_order:
            # отменяет ордер
            bot.send_message(user_id, 'Ордер отменен')

    def change_price(self, user_id, msg):
        new_price = int(msg)
        # меняет цену в ордере на new_price
        bot.send_message(user_id, f'Цена на указанный ордер изменена на {new_price}')

    # Обрабатывает нажатие на кнопку покупки
    def buy(self, user_id):
        bot.send_message(user_id, 'Какой тип продукта тебя интересует', reply_markup=buttons_types)
        self._order['side'] = 'buy'
        self._order['user_id'] = user_id
        self._order['credentials'] = None

    # Обрабатывает нажатие на кнопку продажи
    def sell(self, user_id):
        bot.send_message(user_id, 'Какой тип продукта тебя интересует', reply_markup=buttons_types)
        self._order['side'] = 'sell'
        self._order['user_id'] = user_id

    # Тип item
    def get_type(self, user_id, msg):
        self._order['type'] = msg
        bot.send_message(user_id,
                         'Теперь напиши название самого товара',
                         reply_markup=telebot.types.ReplyKeyboardRemove()
                         )

    # Название item
    def get_item(self, user_id, msg):
        self._order['item'] = self._order['type'] + '_' + msg
        best_offers_string = Utils.print_best_offers(db.get_best_offers(msg))
        if db.find_item(self._order['item']):
            bot.send_message(user_id, 'best offers: ' + "\n" + best_offers_string)
            bot.send_message(user_id, 'Сколько штук?')
            return True
        else:
            bot.send_message(user_id, 'Ордеров на такой товар еще нет, ты уверен что правильно написал название?', reply_markup=buttons_check)
            return False

    # Количество item
    def get_amount(self, user_id, msg):
        self._order['amount'] = Utils.input_int(msg)
        bot.send_message(user_id, 'Сколько стоит?')

    # Цена item
    def get_price(self, user_id, msg):
        self._order['price'] = Utils.input_int(msg)

    def request_confirm_order(self, user_id):
        bot.send_message(user_id,
                         'Твой ордер:\n\n'
                         f'Действие: {self._order["side"]}\n'
                         f'Тип: {self._order["type"]}\n'
                         f'Товар: {self._order["item"]}\n'
                         f'Количество: {self._order["amount"]}\n\n'
                         f'Цена: {self._order["price"]}\n'
                         'Все верно?', reply_markup=buttons_check)

    def check(self, user_id, msg):
        if self._order['side'] == 'buy':
            bot.send_message(user_id,
                             f'Теперь переведи {self._order["price"] * self._order["amount"]} usdc в сети bep20 на адрес {ADM_WALLET}\n'
                             f'После этого отправить id транзакции (чтобы мы могли идентифировать что деньги пришли именно от тебя) когда она подтвердится',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            return 'buy'
        else:
            bot.send_message(user_id,
                             'Отлично! Добавим твой ордер в базу\nОтправь файл формата .txt со всеми credentials по указанным товарам, каждый товар на отдельной строке',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            return 'sell'

    def get_credentials(self, user_id, msg):
        try:
            file_info = bot.get_file(msg.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = '../resources/credentials/' + msg.document.file_name
            f_name = str(msg.document.file_name)
            assert f_name[len(f_name)-4:] == ".txt"

            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            with open(src, 'r') as f:
                credentials = f.read()
            # credentials - строка с содержимым файла
            self.confirm_credentials(user_id, credentials)
        except AssertionError:
            bot.send_message(user_id, 'Не текстовый файл, начни снова')

    def confirm_order(self, user_id, msg):
        if self._order['side'] == 'buy':
            self.confirm_payment(user_id, msg)
        else:
            self.confirm_credentials(user_id, msg)

    def confirm_payment(self, user_id, tx_id):
        payment = int(self._order['price']) * int(self._order['amount'])
        if Bsc.check_deposit(payment, tx_id):
            db.add_to_verified(self._order)
            bot.send_message(user_id, 'ордер выставлен')
        else:
            bot.send_message(user_id, 'что-то не так. пиши админу')

    def confirm_credentials(self, user_id, msg):
        self._order['credentials'] = msg
        db.add_to_unverified(self._order)
        self.admin_request_verify(user_id)

    def admin_request_verify(self, user_id):
        admins = ADMIN
        for admin_id in admins:
            bot.send_message(admin_id, 'go verify')
        bot.send_message(user_id, 'wait for verification', reply_markup=main)

    def create_item(self):
        db.create_item(self._order['item'], self._order['type'])

    # Админка
    def admin(self, user_id):
        s = ''
        orders = db.find_unverified()
        if len(orders) != 0:
            for index, order in enumerate(orders):
                s += f'{index + 1} - {str(order)}\n'
            bot.send_message(user_id, s)
            bot.send_message(user_id, 'Напиши номер ордера который хочешь изменить или 0 чтобы вернуться',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
        else:
            bot.send_message(user_id, 'Нет необработанных ордеров')
            bot.send_message(user_id, 'Главное меню', reply_markup=main)

    def admin_manage(self, user_id, msg):
        orders = db.find_unverified()
        if msg == '0':
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        else:
            order_id = int(msg) - 1
            bot.send_message(user_id, str(orders[order_id]))
            self._adm_order = orders[order_id]
            bot.send_message(user_id, 'Выбери действие', reply_markup=buttons_verify)

    def verify_order(self, user_id, msg):
        if msg == bt.verify:
            # верифицирует ордер
            db.verify_first_unverified(self._adm_order[0])
            bot.send_message(self._adm_order[1], 'Ордер верифицирован')
            bot.send_message(user_id, 'Скинь файл .txt с новыми credentials')

        if msg == bt.decline:
            # отклоняет ордер
            db.delete_first_unverified(self._adm_order[0])
            bot.send_message(self._adm_order[1], 'Ордер отклонен')

        # Обрабатывает нажатие на кнопку мой адресс

    def get_my_address(self, user_id):
        if db.return_address(user_id):
            bot.send_message(user_id, f'Твой адресс: {db.return_address(user_id)[0]}')
        else:
            bot.send_message(user_id, 'Ты еще не говорил мне свой адресс\nНажми на кнопку Редактировать адресс',
                             reply_markup=main)

    # Обрабатывает нажатие на кнопку редактировать адресс
    def edit_address(self, user_id):
        if db.return_address(user_id):
            bot.send_message(user_id, f'Твой текущий адресс: {db.return_address(user_id)[0]}')
            bot.send_message(user_id, 'Введи новый адрес сети bep20:')
        else:
            bot.send_message(user_id, 'Введи свой адрес сети bep20:',
                             reply_markup=telebot.types.ReplyKeyboardRemove())

    def get_new_address(self, user_id, msg):
        if Utils.input_address(msg):
            db.remove_address(user_id)
            db.add_address(user_id, msg)
            bot.send_message(user_id, 'Твой адрес изменен', reply_markup=main)
        else:
            bot.send_message(user_id, 'Неверный формат', reply_markup=main)

    def get_new_credentials(self, user_id, msg):
        file_info = bot.get_file(msg.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = '../resources/new_credentials/' + msg.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        with open(src, 'r') as f:
            new_credentials = f.read()
        # new_credentials - строка с содержимым файла
        bot.send_message(user_id, 'Главное меню', reply_markup=main)
