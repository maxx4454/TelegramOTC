import telebot
from resources.buttons import Buttons

bt = Buttons()

# Реплай кнопки в начале
main = telebot.types.ReplyKeyboardMarkup(True)
main.row(bt.buy, bt.sell)
main.row(bt.my_orders, bt.my_address)
main.row(bt.edit_address)

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
buttons_verify.row(bt.verify, bt.decline)

# inline_buttons_types = telebot.types.InlineKeyboardMarkup()
#
# allocation = telebot.types.InlineKeyboardButton(text = bt.allocation, callback_data = 'allocation')
# wl = telebot.types.InlineKeyboardButton(text = bt.wl, callback_data = 'wl')
# sn_account = telebot.types.InlineKeyboardButton(text = bt.sn_account, callback_data = 'sn_account')
# unlocked_tokes = telebot.types.InlineKeyboardButton(text = bt.unlocked_tokens, callback_data = 'unlocked_tokens')
# other = telebot.types.InlineKeyboardButton(text = bt.other, callback_data = 'other')
#
# inline_buttons_types.add(allocation)
# inline_buttons_types.add(wl)
# inline_buttons_types.add(sn_account)
# inline_buttons_types.add(unlocked_tokes)
# inline_buttons_types.add(other)



# Инлайн кнопки проверки
# inline_buttons_check = telebot.types.InlineKeyboardMarkup()
#
# yes = telebot.types.InlineKeyboardButton(text = bt.yes, callback_data = 'yes')
# no = telebot.types.InlineKeyboardButton(text = bt.no, callback_data = 'no')
#
# inline_buttons_check.add(yes)
# inline_buttons_check.add(no)

# Инлайн работы с ордерами
manage_orders = telebot.types.InlineKeyboardMarkup()

verify = telebot.types.InlineKeyboardButton(text = bt.verify, callback_data = 'verify')
wait = telebot.types.InlineKeyboardButton(text = bt.wait, callback_data = 'wait')
decline = telebot.types.InlineKeyboardButton(text = bt.decline, callback_data = 'decline')

manage_orders.add(verify, wait, decline)