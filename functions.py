import telebot
from config import *
# from database import Database


bot = telebot.TeleBot(TOKEN)

# db = Database()

# class Functions:

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

    # order = {}
    # # Обрабатывает нажатие на кнопку покупки
    # def buy(self, chat_id, user_id, message):
    #     order_ = Functions.create_order(chat_id, user_id)
    #     # bot.send_message(chat_id,
    #     #                  'Отлично. Давай определимся что ты хочешь купить\n'
    #     #                  'Введи название (например NFT)'
    #     #                  )
    #     bot.send_message(chat_id, f"{order['id']} + {order['item']} + {order['amount']}")
    # # Обрабатываает нажатие на кнопку продажи
    # def sell(self, chat_id, user_id):
    #     bot.send_message(chat_id,
    #                      'Отлично. Давай определимся что ты хочешь продать\n'
    #                      'Введи название (например NFT)'
    #                      )
    # # Собираем item
    # def create_order(self, chat_id, user_id):
    #     new_order = {}
    #
    #     item = get_item()
    #     amount = get_amount()
    #
    #     new_order['id'] = user_id
    #     new_order['item'] = item
    #     new_order['amount'] = amount
    #
    #     return new_order
    #
    # # Название item
    # def get_item(self, chat_id, user_id, message):
    #     bot.register_next_step_handler(message, get_item)
    #     item = message
    #     bot.send_message(chat_id,
    #                      'Введите количество для покупки:'
    #                      )
    # # Количество item
    # # def get_amount(self, chat_id, user_id, message):
    # #     amount = int(message)
