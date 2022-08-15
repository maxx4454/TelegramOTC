from resources.config import *
from resources.keyboards import *
from utils import Utils

from db import Database
from web3_module import Bsc
from market_making import *

bot = telebot.TeleBot(TOKEN)
bt = Buttons()

db.init()


class Order:
    _order = {}
    _adm_order = {}

    # Обрабатывает нажатие на кнопку мои ордера
    def get_my_orders(self, user_id):
        s = ''
        orders = db.find_active_orders(user_id)
        for i in range(len(orders)):
            s += f'{i + 1} - {str(orders[i])}\n'
        bot.send_message(user_id, s)
        bot.send_message(user_id, 'Напиши номер ордера который хочешь изменить или 0 чтобы вернуться',
                         reply_markup=telebot.types.ReplyKeyboardRemove())

    def manage(self, user_id, msg):
        orders = db.find_active_orders(user_id)
        if msg == '0':
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        else:
            order_id = int(msg) - 1
            bot.send_message(user_id, str(orders[order_id]))
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

    # Название item
    def get_type(self, user_id, msg):
        self._order['type'] = msg
        bot.send_message(user_id,
                         'Теперь напиши название самого товара',
                         reply_markup=telebot.types.ReplyKeyboardRemove()
                         )

    def get_item(self, user_id, msg):
        self._order['item'] = self._order['type'] + '_' + msg
        best_offers_string = Utils.print_best_offers(db.get_best_offers(msg))
        if db.find_item(self._order['item']):
            bot.send_message(user_id, 'best offers: ' + "\n" + best_offers_string)
            bot.send_message(user_id, 'Сколько штук?')
            return True
        else:
            bot.send_message(user_id, 'u sure everything fine with the name? follow guidelines plz? TYPE "YES" if fine')
            return False

    def get_amount(self, user_id, msg):
        self._order['amount'] = Utils.input_int(msg)
        bot.send_message(user_id, 'Сколько стоит?')

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
        if msg == bt.yes:
            bot.send_message(user_id,
                             'Отлично! Добавим твой ордер в базу\ncredentials or Напиши в чат tx_id когда транзакция подтвердится',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            return True

        if msg == bt.no:
            bot.send_message(user_id, 'Давай разбираться что не так',
                             reply_markup=telebot
                             .types.ReplyKeyboardRemove())
            return False

    def confirm_order(self, user_id, msg):
        if self._order['side'] == 'buy':
            self.confirm_payment(user_id, msg)
        else:
            self.confirm_credentials(user_id, msg)

    def confirm_payment(self, user_id, tx_id):
        payment = int(self._order['price']) * int(self._order['amount'])
        if Bsc.check_deposit(payment, tx_id):
            db.add_to_verified(self._order)
            bot.send_message(user_id, 'ордер выставлен', reply_markup=main)
        else:
            bot.send_message(user_id, 'что-то не так. пиши админу')

    def confirm_credentials(self, user_id, msg):
        self._order['credentials'] = msg
        db.add_to_unverified(self._order)
        self.admin_request_verify(user_id)

    def admin_request_verify(self, user_id):
        admin_id = 892338763
        bot.send_message(admin_id, 'go verify')
        bot.send_message(user_id, 'wait for verification')

    def create_item(self):
        db.create_item(self._order['item'], self._order['type'])

    # Админка
    def admin(self, user_id):
        s = ''
        orders = db.find_unverified()
        for i in range(len(orders)):
            s += f'{i + 1} - {str(orders[i])}\n'
        bot.send_message(user_id, s)
        bot.send_message(user_id, 'Напиши номер ордера который хочешь изменить или 0 чтобы вернуться',
                         reply_markup=telebot.types.ReplyKeyboardRemove())

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

    # def get_new_credentials(self, ):

    # Обрабатывает нажатие на кнопу мой адресс
    def get_my_address(self, user_id):
        if db.return_address(user_id):
            bot.send_message(user_id, f'Твой адресс: {db.return_address(user_id)}')
        else:
            bot.send_message(user_id, 'Ты еще не говорил мне свой адресс\nНажми на кнопку Редактировать адресс',
                             reply_markup=main)

    # Обрабатывает нажатие на кнопку редактировать адресс
    def edit_address(self, user_id):
        if db.return_address(user_id):
            bot.send_message(user_id, f'Твой текущий адресс: {db.return_address(user_id)}')
            bot.send_message(user_id, 'Введи новый адрес сети bep20:')
        else:
            bot.send_message(user_id, 'Введи свой адрес сети bep20:',
                             reply_markup=telebot.types.ReplyKeyboardRemove())

    def get_new_address(self, user_id, msg):
        db.remove_address(user_id)
        if Utils.input_address(msg):
            db.add_address(user_id, msg)
        else:
            bot.send_message(user_id, 'wrong format try again', reply_markup=main)

        bot.send_message(user_id, 'Твой адресс изменен', reply_markup=main)
