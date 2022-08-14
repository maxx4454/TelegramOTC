from resources.config import *
from resources.keyboards import *
from utils import Utils

from db import Database
from web3_module import Bsc

bot = telebot.TeleBot(TOKEN)
bt = Buttons()

db = Database()
db.init()


class Order:
    _order = {}

    # Админка
    def admin(self, user_id):
        s = ''
        orders = db.find_unverified()
        for i in range(len(orders)):
            s += f'{i + 1} - {str(orders[i])}\n'
        bot.send_message(user_id, s)
        bot.send_message(user_id, 'Напиши номер ордера который хочешь изменить или 0 чтобы вернуться', reply_markup=telebot.types.ReplyKeyboardRemove())

    def admin_manage(self, user_id, msg):
        orders = db.find_unverified()
        if msg == '0':
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        else:
            order_id = int(msg) - 1
            bot.send_message(user_id, str(orders[order_id]))
            bot.send_message(user_id, 'Выбери действие', reply_markup=buttons_verify)

    def verify_order(self, user_id, msg):
        if msg == bt.verify:
            # верифицирует ордер
            bot.send_message(user_id, 'Ордер верифицирован')
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        if msg == bt.decline:
            # отклоняет ордер
            bot.send_message(user_id, 'Ордер отклонен')
            bot.send_message(user_id, 'Главное меню', reply_markup=main)


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

    # Обрабатывает нажатие на кнопку мои ордера
    def get_my_orders(self, user_id):
        s = ''
        orders = db.find_active_orders(user_id)
        for i in range(len(orders)):
            s += f'{i+1} - {str(orders[i])}\n'
        bot.send_message(user_id, s)
        bot.send_message(user_id, 'Напиши номер ордера который хочешь изменить или 0 чтобы вернуться', reply_markup=telebot.types.ReplyKeyboardRemove())

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
            bot.send_message(user_id, 'Главное меню', reply_markup=main)

    def change_price(self, user_id, msg):
        new_price = int(msg)
        # меняет цену в ордере на new_price
        bot.send_message(user_id, f'Цена на указанный ордер изменена на {new_price}')
        bot.send_message(user_id, 'Главное меню', reply_markup=main)


    # Название item
    def get_type(self, user_id, msg):
        self._order['type'] = msg
        bot.send_message(user_id,
                         'Теперь напиши название самого товара',
                         reply_markup=telebot.types.ReplyKeyboardRemove()
                         )

    def get_item(self, user_id, msg):
        self._order['item'] = msg
        bot.send_message(user_id, Utils.print_best_offers(db.get_best_offers(msg)))
        bot.send_message(user_id, 'Сколько штук?')

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

        if msg == bt.no:
            bot.send_message(user_id, 'Давай разбираться что не так',
                             reply_markup=telebot.types.ReplyKeyboardRemove())

    def confirm_order(self, user_id, msg):
        if self._order['side'] == 'buy':
            self.confirm_payment(user_id, msg)
        else:
            self.confirm_credentials(user_id, msg)


    def confirm_payment(self, user_id, tx_id):
        payment = self._order['price'] * self._order['amount']
        if Bsc.check_deposit(payment, tx_id):
            db.add_to_verified(self._order)
            bot.send_message(user_id, 'ордер выставлен')
            bot.send_message(user_id, 'Главное меню', reply_markup=main)
        else:
            bot.send_message(user_id, 'что-то не так. пиши админу')

    def confirm_credentials(self, user_id, msg):
        self._order['credentials'] = msg
        db.add_to_unverified(self._order)
        self.admin_request_verify(msg, self._order['type'], self._order['item'])

    def admin_request_verify(self, creds, item_type, item):
        admin_id = 585587478
        bot.send_message(admin_id, 'go verify')

    # def admin_verification(self):
    #     admin_id = 585587478
    #     unverified_list = db.find_unverified()
    #     if len(unverified_list) > 0:
    #         for unverified_order in unverified_list:
    #             print(unverified_order)
    #             reply_text = ''
    #             address_t = db.return_address(unverified_order[1])
    #             credentials = db.return_credentials(unverified_order[0])
    #             print(address_t[0])
    #
    #             reply_text += str(address_t[0])
    #             reply_text += "\n"
    #             reply_text += str(unverified_order)
    #             reply_text += "\n"
    #             reply_text += str(credentials)
    #             bot.send_message(admin_id, reply_text,
    #                              reply_markup=telebot.types.ReplyKeyboardRemove())
    #
    #     else:
    #         bot.send_message(admin_id, 'Давай разбираться что не так')





