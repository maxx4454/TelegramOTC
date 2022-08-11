import telebot
from telebot import types

bot = telebot.TeleBot('5404369551:AAGXDshe2IWUBo0ikE0867Ei6Ugg6qo58qQ')

product = ''
amount = 0
usd_amount = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! <b>Это бот для OTC.</b>\nЗдесь ты можешь безопасно покупать и продавать товары со вторички', parse_mode='html')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_buy = types.KeyboardButton('Я хочу купить')
    key_sell = types.KeyboardButton('Я хочу продать')

    markup.add(key_buy, key_sell)

    bot.send_message(message.chat.id, 'Выбери действие, которое тебя интересует', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def action(message):
    if message.text == 'Я хочу купить':
        bot.send_message(message.chat.id, 'Отлично. Давай определимся что ты хочешь купить\nВведи название (например NFT)')
        bot.register_next_step_handler(message, get_product)
    elif message.text == 'Я хочу продать':
        bot.send_message(message.chat.id, 'Отлично. Давай определимся что ты хочешь продать\nВведи название (например NFT)')
        bot.register_next_step_handler(message, get_product)

def get_product(message):
    global product
    product = message.text
    bot.send_message(message.chat.id, 'Введи количество для покупки:')
    bot.register_next_step_handler(message, get_amount)

def get_amount(message):
    global amount
    amount = int(message.text)
    bot.send_message(message.chat.id, 'Это стоит 500usd')
    bot.send_message(message.chat.id, 'Введи количество usd для пополнения:')
    bot.register_next_step_handler(message, get_usd_amount)

def get_usd_amount(message):
    global usd_amount
    usd_amount = int(message.text)
    bot.send_message(message.chat.id, 'Теперь отправь их на кошелек нашего гаранта:\n<u>адресс кошелька</u>', parse_mode='html')

bot.polling(none_stop=True)