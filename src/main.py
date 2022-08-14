from src.functions import *
from src.db import Database
from resources.config import *

order = Order()
db = Database()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! <b>Это бот для OTC.</b>\n\n'
                     'Здесь ты можешь безопасно покупать и продавать товары со вторички\n'
                     'Выбери действие, которое тебя интересует',
                     parse_mode='html', reply_markup=main
                     )

@bot.message_handler(commands=['admin'])
def admin(message):
    if str(message.from_user.id) in ADMIN:
        bot.send_message(message.chat.id, 'Админ панель')
        order.admin(message.chat.id)
        bot.register_next_step_handler(message, admin_manage)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа')
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=main)



# если нажал купить
@bot.message_handler(func=lambda message: message.text == bt.buy)
def buy(message):
    order.buy(message.chat.id)
    bot.register_next_step_handler(message, get_type)


# если нажал продать
@bot.message_handler(func=lambda message: message.text == bt.sell)
def sell(message):
    order.sell(message.chat.id)
    bot.register_next_step_handler(message, get_type)


# если нажал мои ордера
@bot.message_handler(func=lambda message: message.text == bt.my_orders)
def orders(message):
    order.get_my_orders(message.chat.id)
    bot.register_next_step_handler(message, manage_orders)

# если нажал мой адресс
@bot.message_handler(func=lambda message: message.text == bt.my_address)
def my_adress(message):
    order.get_my_address(message.chat.id)

# если нажал редактировать адресс
@bot.message_handler(func=lambda message: message.text == bt.edit_address)
def edit_address(message):
    order.edit_address(message.chat.id)
    bot.register_next_step_handler(message, get_new_address)


@bot.message_handler(content_types=['text'])
def get_new_address(message):
    order.get_new_address(message.chat.id, message.text)

def get_type(message):
    order.get_type(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_item)


def get_item(message):
    order.get_item(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_amount)


def get_amount(message):
    order.get_amount(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_price)


def get_price(message):
    order.get_price(message.chat.id, message.text)
    order.request_confirm_order(message.chat.id)
    bot.register_next_step_handler(message, req_confirm_order)


def req_confirm_order(message):
    order.check(message.chat.id, message.text)
    bot.register_next_step_handler(message, confirm_order)


def confirm_order(message):
    order.confirm_order(message.chat.id, message.text)


def manage_orders(message):
    order.manage(message.chat.id, message.text)
    bot.register_next_step_handler(message, change_order)

def change_order(message):
    order.change_order(message.chat.id, message.text)
    bot.register_next_step_handler(message, change_price)

def change_price(message):
    order.change_price(message.chat.id, message.text)


def admin_manage(message):
    order.admin_manage(message.chat.id, message.text)
    bot.register_next_step_handler(message, verify_order)

def verify_order(message):
    order.verify_order(message.chat.id, message.text)


# @bot.callback_query_handler(func=lambda call: True)
# def market(call):
#     global order
#     user_id = call.from_user.id
#     chat_id = call.message.chat.id
#
#     #Обработка типов товара
#     if call.data == 'allocation':
#         order['type'] = 'allocation'
#         bot.send_message(chat_id, 'allocation')
#     if call.data == 'wl':
#         order['type'] = 'wl'
#     if call.data == 'sn_account':
#         order['type'] = 'sn_account'
#     if call.data == 'unlocked_tokens':
#         order['type'] = 'unlocked_tokens'
#     if call.data == 'other':
#         order['type'] = 'other'
#
#     #Обработка проверки
#     if call.data == 'yes':
#         bot.send_message(chat_id, 'Отлично! Добавим твой ордер в базу')
#     if call.data == 'no':
#         bot.send_message(chat_id, 'Давай разбираться что не так')


bot.polling(none_stop=True)
