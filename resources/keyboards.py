import telebot
from resources.buttons import Buttons

bt = Buttons()

# Реплай кнопки в начале
main = telebot.types.ReplyKeyboardMarkup(True)
main.row(bt.buy, bt.sell)
main.row(bt.my_orders)
main.row(bt.my_address, bt.edit_address)
main.row(bt.connect_admin)

# go_main = telebot.types.ReplyKeyboardMarkup(True)
# go_main.row(bt.back)

# Реплай кнопки типов
buttons_types = telebot.types.ReplyKeyboardMarkup(True)
buttons_types.row(bt.allocation, bt.wl)
buttons_types.row(bt.sn_account, bt.unlocked_tokens)
buttons_types.row(bt.other)

# Реплай кнопки проверки
buttons_check = telebot.types.ReplyKeyboardMarkup(True)
buttons_check.row(bt.yes, bt.no)

# Реплай кнопки изменения ордеров
buttons_manage = telebot.types.ReplyKeyboardMarkup(True)
buttons_manage.row(bt.change_price, bt.cancel_order)

# Реплай кнопки верификации
buttons_verify = telebot.types.ReplyKeyboardMarkup(True)
buttons_verify.row(bt.verify, bt.decline, bt.wait)
