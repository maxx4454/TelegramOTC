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


@bot.message_handler(content_types=['document'])
def get_new_credentials(message):
    order.get_new_credentials(message.chat.id, message)

def get_credentials(message):
    order.get_credentials(message.chat.id, message)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! <b>Это бот для OTC.</b>\n'
                     'Здесь ты можешь безопасно покупать и продавать товары со вторички\n\n',
                     parse_mode='html'
                     )
    bot.send_message(message.chat.id,
                     'Для того чтобы купить/продать что-то, <b>тебе понадобится:</b>\n'
                     '1) Выбрать тип товара из предложенных\n'
                     '2) Ввести название\n'
                     '3) Ввести желаемое количество\n'
                     '4) А также цену по которой ты хочешь купить/продать товар\n'
                     '5) Удостовериться что все введено верно', parse_mode='html'
                     )
    bot.send_message(message.chat.id,
                     'Далее, в зависимости от того какого действие ты хочешь выполнить, тебя попросят следующее:\n\n'
                     'Если ты хочешь <b>купить</b>, то тебе будет необходимо:\n'
                     '1) Отправить указанную сумму (цена * количество) на наш адрес (таже будет указан)\n'
                     '2) Написать id транзакции, что мы могли ее найти\n'
                     'После такого как админ найдет твою транзакцию, твой ордер будет выставлен, и виден другим пользователям\n\n'
                     'Если ты хочешь <b>продить</b>, то тебе будет необходимо:\n'
                     '1) Отправить файл .txt с данными от аккаунтов которые ты продаешь (в указанном количестве, один акк - одна строка в файле)\n'
                     'После такого как админ верифицирует данные от аккаунта, твой ордер будет выставлен, и виден другим пользователям', parse_mode='html'
                     )
    bot.send_message(message.chat.id,
                     'Еще пара слов о <b>структуре бота:</b>\n'
                     'После того админ верифицирует ордера, пользователи смогут их видеть\n'
                     'А как только найдутся два ордера купить - продать с одним товаром и ценой, они автоматически исполнятся, т.е.\n'
                     '<i>Покупателю</i> - пришлем товар\n'
                     '<i>Продавцу</i> - деньги на указанный адрес\n\n'
                     'До этого момента, деньги будут хранится на нашем счете, а верифицированные данные на нашем защищенном сервере\n'
                     'Таким образом, мы гарантируем надежность', parse_mode='html'
                     )
    bot.send_message(message.chat.id,
                     'На этом инструктаж закончен, пользуйся :)\n\n'
                     '<u>P.S. вводи данные корректо, где просят числа, вводи числа, где слова - там слова\n'
                     'Это в твоих же интересах, чтобы обрабатывать и выставлять твои ордера как можно быстрее)</u>', parse_mode='html'
                     )
    bot.send_message(message.chat.id, 'Выбери действие из предложенных:', reply_markup=main)
    bot.register_next_step_handler(message, basic)


@bot.message_handler(content_types=['text'])
def basic(message):
    # если нажал купить
    if message.text == bt.buy:
        if db.return_address(message.chat.id):
            order.buy(message.chat.id)
            bot.register_next_step_handler(message, get_type)
        else:
            bot.send_message(message.chat.id,
                             'Ты еще не ввел свой адрес. Пожалуйста нажми на кнопку редактировать адрес',
                             reply_markup=main)
            bot.register_next_step_handler(message, basic)
    # если нажал продать
    elif message.text == bt.sell:
        if db.return_address(message.chat.id):
            order.sell(message.chat.id)
            bot.register_next_step_handler(message, get_type)
        else:
            bot.send_message(message.chat.id,
                             'Ты еще не ввел свой адрес. Пожалуйста нажми на кнопку редактировать адрес',
                             reply_markup=main)
            bot.register_next_step_handler(message, basic)
    # если нажал мои ордера
    elif message.text == bt.my_orders:
        order.get_my_orders(message.chat.id)
        bot.register_next_step_handler(message, manage_orders)
    # если нажал мой адресс
    elif message.text == bt.my_address:
        order.get_my_address(message.chat.id)
    # если нажал редактировать адресс
    elif message.text == bt.edit_address:
        order.edit_address(message.chat.id)
        bot.register_next_step_handler(message, get_new_address)
    # если нажал помощь
    elif message.text == bt.connect_admin:
        bot.send_message(message.chat.id, 'Пиши админам @btcup555 или @bellik_niko', reply_markup=main)
        bot.register_next_step_handler(message, basic)
    # некорректный ввод
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста используй кнопки', reply_markup=main)
        bot.register_next_step_handler(message, basic)


def get_new_address(message):
    order.get_new_address(message.chat.id, message.text)


def get_type(message):
    if message.text in bt.types:
        order.get_type(message.chat.id, message.text)
        bot.register_next_step_handler(message, get_item)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста используй кнопки', reply_markup=buttons_types)
        bot.register_next_step_handler(message, get_type)

def get_item(message):
    if order.get_item(message.chat.id, message.text):
        bot.register_next_step_handler(message, get_amount)
    else:
        bot.register_next_step_handler(message, check_if_ok)


def check_if_ok(message):
    if message.text == bt.yes:
        bot.send_message(message.chat.id, 'Сколько штук?')
        order.create_item()
        bot.register_next_step_handler(message, get_amount)
    elif message.text == bt.no:
        bot.send_message(message.chat.id, 'Напиши корректное название товара', reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_item)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста используй кнопки', reply_markup=buttons_check)
        bot.register_next_step_handler(message, check_if_ok)


def get_amount(message):
    if message.text.isdigit():
        order.get_amount(message.chat.id, message.text)
        bot.register_next_step_handler(message, get_price)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста введи число')
        bot.register_next_step_handler(message, get_amount)


def get_price(message):
    if message.text.isdigit():
        order.get_price(message.chat.id, message.text)
        order.request_confirm_order(message.chat.id)
        bot.register_next_step_handler(message, req_confirm_order)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста введи число')
        bot.register_next_step_handler(message, get_price)


def req_confirm_order(message):
    if message.text == bt.yes:
        if order.check(message.chat.id, message.text) == 'buy':
            bot.register_next_step_handler(message, get_tx_id)
        else:
            bot.register_next_step_handler(message, get_credentials)
    elif message.text == bt.no:
        bot.send_message(message.chat.id, 'Хорошо, давай заново', reply_markup=main)
        bot.register_next_step_handler(message, start)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Пожалуйста используй кнопки', reply_markup=buttons_check)
        bot.register_next_step_handler(message, req_confirm_order)



def get_tx_id(message):
    order.confirm_payment(message.chat.id, message.text)


# админ хендлеры
def admin_manage(message):
    order.admin_manage(message.chat.id, message.text)
    bot.register_next_step_handler(message, verify_order)

def verify_order(message):
    order.verify_order(message.chat.id, message.text)
    bot.register_next_step_handler(message, get_new_credentials)


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
