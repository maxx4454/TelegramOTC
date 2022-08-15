from src.functions import *
from src.db import Database
from resources.config import *
import multiprocessing

order = Order()
db = Database()


@bot.message_handler(commands=['admin'])
def admin(message):
    if str(message.from_user.id) in ADMIN:
        bot.send_message(message.chat.id, 'Админ панель')
        order.admin(message.chat.id)
        bot.register_next_step_handler(message, admin_manage)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа')
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=main)


def admin_manage(message):
    order.admin_manage(message.chat.id, message.text)
    bot.register_next_step_handler(message, verify_order)


def verify_order(message):
    order.verify_order(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_new_credentials)

@bot.message_handler(content_types=['document'])
def get_new_credentials(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src = '../resources/new_credentials/' + message.document.file_name
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    with open(src, 'r') as f:
        new_credentials = f.read()
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=main)
    # new_credentials - строка с содержимым файла


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! <b>Это бот для OTC.</b>\n\n'
                     'Здесь ты можешь безопасно покупать и продавать товары со вторички\n'
                     'Выбери действие, которое тебя интересует',
                     parse_mode='html', reply_markup=main
                     )


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


@bot.message_handler(content_types=['text'])
def get_new_address(message):
    order.get_new_address(message.chat.id, message.text)


# если нажал редактировать адресс
@bot.message_handler(func=lambda message: message.text == bt.edit_address)
def edit_address(message):
    order.edit_address(message.chat.id)
    bot.register_next_step_handler(message, get_new_address)


@bot.message_handler(content_types=['text'])
def get_type(message):
    order.get_type(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_item)


def get_item(message):
    if order.get_item(message.chat.id, message.text):
        bot.register_next_step_handler(message, get_amount)
    else:
        bot.register_next_step_handler(message, check_if_ok)


def check_if_ok(message):
    if message.text == "YES":
        bot.send_message(message.chat.id, 'Сколько штук?')
        order.create_item()
        bot.register_next_step_handler(message, get_amount)
    else:
        bot.send_message(message.chat.id, 'start over')


def get_amount(message):
    order.get_amount(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_price)


def get_price(message):
    order.get_price(message.chat.id, message.text)
    order.request_confirm_order(message.chat.id)
    bot.register_next_step_handler(message, req_confirm_order)


def req_confirm_order(message):
    if order.check(message.chat.id, message.text):
        bot.register_next_step_handler(message, confirm_order)

        # if db.return_address(message.chat.id):
        #     bot.register_next_step_handler(message, confirm_order)
        # else:
        #     bot.send_message(message.chat.id, 'your bep20 address?')
        #     bot.register_next_step_handler(message, add_address)


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


def main_func():
    bot.polling(none_stop=True)


MM = MarketMaking()
if __name__ == "__main__":
    p1 = multiprocessing.Process(target=main_func)
    p2 = multiprocessing.Process(target=MM.market_making)
    p1.start()
    p2.start()
