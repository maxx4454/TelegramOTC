import telebot
from config import *
import telebot
from config import *
from buttons import Buttons
from keyboards import *

from db import Database


bot = telebot.TeleBot(TOKEN)
bt = Buttons()


db = Database()


class Order:
    _order = {}

    # Обрабатывает нажатие на кнопку просмотра своих ордеров
    # def orders(self, chat_id, user_id):
    #     buy_orders = db.take_buy_orders(user_id).fetchone()
    #     sell_orders = db.take_sell_orders(user_id).fetchone()
    #     bot.send_message(chat_id,
    #     '*Ордера*\n\n'
    #
    #     f'*{chicken.name}*\n'
    #     f'Количество: {all_animals[0]}\n'
    #     f'Добыли: {all_products[0]} 🥚\n\n'
    #
    #     f'*{sheep.name}*\n'
    #     f'Количество: {all_animals[1]}\n'
    #     f'Добыли: {all_products[1]} 💭\n\n'
    #
    #     f'*{cow.name}*\n'
    #     f'Количество: {all_animals[2]}\n'
    #     f'Добыли: {all_products[2]} 🥛\n\n'
    #
    #     f'*{pig.name}*\n'
    #     f'Количество: {all_animals[3]}\n'
    #     f'Добыли: {all_products[3]} 🥩\n\n',
    #
    #     parse_mode='Markdown'
    #     )

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


    # Название item
    def get_type(self, user_id, msg):
        self._order['type'] = msg
        bot.send_message(user_id,
                         'Теперь напиши название самого товара',
                         reply_markup=telebot.types.ReplyKeyboardRemove()
                         )

    def get_item(self, user_id, msg):
        self._order['item'] = msg
        bot.send_message(user_id, 'Сколько штук?')

    def get_amount(self, user_id, msg):
        self._order['amount'] = msg
        bot.send_message(user_id, 'Сколько стоит?')

    def get_price(self, user_id, msg):
        self._order['price'] = msg

    def confirm_order(self, user_id):
        bot.send_message(user_id,
                         'Твой ордер:\n\n'
                         f'Действие: {self._order["side"]}\n'
                         f'Тип: {self._order["type"]}\n'
                         f'Товар: {self._order["item"]}\n'
                         f'Количество: {self._order["amount"]}\n\n'
                         f'Цена: {self._order["price"]}\n'
                         'Все верно?', reply_markup=buttons_check)

    def check(self, user_id, msg):
        if msg == 'Да':
            bot.send_message(user_id, 'Отлично! Добавим твой ордер в базу',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
            db.add_params(self._order)
            
        if msg == 'Нет':
            bot.send_message(user_id, 'Давай разбираться что не так',
                             reply_markup=telebot.types.ReplyKeyboardRemove())
