import telebot
from config import *
from buttons import Buttons
from keyboards import *
# from functions import Functions

bot = telebot.TeleBot(TOKEN)

bt = Buttons()
# func = Functions()

order = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,

            'Привет! <b>Это бот для OTC.</b>\n\n'
            'Здесь ты можешь безопасно покупать и продавать товары со вторички\n'
            'Выбери действие, которое тебя интересует',
            parse_mode='html', reply_markup=main

        )

# если нажал купить
@bot.message_handler(func = lambda message: message.text == bt.buy)
def buy(message):
    global order
    order['side'] = 'buy'
    bot.send_message(message.chat.id, 'Какой тип продукта тебя интересует', reply_markup=buttons_types)
    bot.register_next_step_handler(message, get_type)

# если нажал продать
@bot.message_handler(func = lambda message: message.text == bt.sell)
def sell(message):
    global order
    order['side'] = 'sell'
    bot.register_next_step_handler(message, get_type)

# если нажал мои ордера
# @bot.message_handler(func = lambda message: message.text == bt.orders)
# def orders(message):
#     func.information_about_orders(message.chat.id, message.from_user.id)


@bot.message_handler(content_types=['text'])
def get_type(message):
    markup = telebot.types.ReplyKeyboardRemove()
    global order
    order['type'] = message.text
    bot.send_message(message.chat.id, 'Теперь напиши название самого товара', reply_markup=markup)
    bot.register_next_step_handler(message, get_item)

def get_item(message):
    global order
    order['item'] = message.text
    bot.send_message(message.chat.id, 'Сколько?')
    bot.register_next_step_handler(message, create_order)

# def get_amount(message):
#     global order
#     order['amount'] = message.text
#     bot.send_message(message.chat.id, 'Сколько?')
#     bot.register_next_step_handler(message, create_order)

def create_order(message):
    global order
    order['amount'] = int(message.text)

    side = order['side']
    type = order['type']
    item = order['item']
    amount = order['amount']
    bot.send_message(message.chat.id,
                     'Твой ордер:\n\n'
                     f'Действие: {side}\n'
                     f'Тип: {type}\n'
                     f'Товар: {item}\n'
                     f'Количество: {amount}\n\n'
                     'Все верно?', reply_markup=buttons_check)
    bot.register_next_step_handler(message, check)

def check(message):
    markup = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Отлично! Добавим твой ордер в базу', reply_markup=markup)
    #     добавление ордера в дата базу
    if message.text == 'Нет':
        bot.send_message(message.chat.id, 'Давай разбираться что не так', reply_markup=markup)


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
