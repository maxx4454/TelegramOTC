import multiprocessing
from logging import getLogger
from market_making import *
import requests
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request
from db import *

STAGE = 1
BUY = 'buy'
SELL = 'sell'
VERIFY = 'verify'
WAIT = 'wait'
SIDE = True  # 1 buy; 0 sell
DECLINE = 'decline'
params = list()


def start_command_handler(update: Update, context: CallbackContext):
    global STAGE
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'anonymous'

    STAGE = 1

    # text = update.effective_message.text
    text = 'Введи следующим сообщением интересующий тебя товар!'
    reply_text = f'Привет, {name}!\n\n{text}'

    update.message.reply_text(
        text=reply_text,
        # reply_markup=get_keyboard()
    )

    STAGE += 1


def manage_orders_command_handler(update: Update, context: CallbackContext):
    user = update.effective_user

    active_orders = find_active_orders(user.id)
    if len(active_orders) > 0:
        for order in active_orders:
            print(order)
            reply_text = 'unverified: '

            reply_text += str(order[0])

            reply_text += '\n'
            reply_text += 'verified: '

            reply_text += str(order[1])

            update.message.reply_text(
                text=reply_text,
                reply_markup=get_keyboard_manage_orders()
            )
    else:
        update.message.reply_text(text='no active orders')


def admin_command_handler(update: Update, context: CallbackContext):
    user = update.effective_user

    if user.id == 585587478:
        unverified_list = find_unverified()
        if len(unverified_list) > 0:
            for unverified_order in unverified_list:
                print(unverified_order)
                reply_text = ''
                address_t = return_address(unverified_order[1])
                credentials = return_credentials(unverified_order[0])
                print(address_t[0])

                reply_text += str(address_t[0])
                reply_text += "\n"
                reply_text += str(unverified_order)
                reply_text += "\n"
                reply_text += str(credentials)
                update.message.reply_text(
                    text=reply_text,
                    reply_markup=get_keyboard_verification()
                )

        else:
            update.message.reply_text(text='everything verified')
    else:
        update.message.reply_text(
            text='ACCESS DENIED',
            # reply_markup=get_keyboard()
        )


def message_user(text: str, bot, user_id):
    global STAGE
    bot.send_message(chat_id=user_id, text=text)
    STAGE = 1


def send_notification(text, user_id="@bot_test_kaka"):
    bot_token = "2139562951:AAHKCDhPe0wI_AR0BGzBvg8OvDdoIdNxGVI"

    # bot_chat_id = "@bot_test_kaka"
    bot_chat_id = str(user_id)
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chat_id + \
                '&parse_mode=Markdown&text=' + text
    response = requests.get(send_text)
    return response.json()


def message_handler(update: Update, context: CallbackContext):
    global STAGE
    user = update.effective_user

    if STAGE == 2:
        text = update.effective_message.text

        if text:
            fitting_items = find_item(
                item=text
            )
            temp = None
            items = read_items()
            for i in items:
                if text in i:
                    temp = i

            if fitting_items and temp:
                response = '\n\n'.join([f'#{side} - {amount}' for side, amount in fitting_items])
                params.append(temp)

            elif temp:
                response = 'be the first to put up an order!'
                params.append(temp)
            else:
                response = 'orders are unavailabe for this item. contact @makckc5 or start over.'
                STAGE = 2

            update.effective_message.reply_text(
                text=response,
                reply_markup=get_keyboard()
            )

    elif STAGE == 3:
        text = update.effective_message.text

        if text:
            params.append(text)
            STAGE = 4
            print(find_user_address(user.id))
            if not find_user_address(user.id):
                if SIDE:
                    update.effective_message.reply_text(
                        text='С какого адреса BUSD покупаете?',
                    )
                else:
                    update.effective_message.reply_text(
                        text='На какой адрес BUSD желаете получить деньги?',
                    )
            else:
                update.effective_message.reply_text(
                    text='Ваш адрес уже сохранен в базе!',
                    # желаете ли поменять?
                )
                STAGE = 5
                if SIDE:
                    add_params(user.id, params)
                    params.clear()
                    update.effective_message.reply_text(
                        text='Положите деньги на __address__ и ожидайте подтверждения заявки!',
                    )
                    send_notification('check for verifications!')
                else:
                    update.effective_message.reply_text(
                        text='Скиньте данные аккаунта через :',
                    )

                    STAGE = 5

    elif STAGE == 4:
        if not find_user_address(user.id):
            if SIDE:
                text = update.effective_message.text
                if text:
                    add_address(user.id, text)
                    add_params(user.id, params)
                    params.clear()
                    STAGE = 5
                    update.effective_message.reply_text(
                        text='Положите деньги на __address__ и ожидайте подтверждения заявки!',
                    )
                    send_notification('check for verifications!')
            else:
                text = update.effective_message.text
                if text:
                    add_address(user.id, text)

                    update.effective_message.reply_text(
                        text='Скиньте данные аккаунта через :',
                    )

                    STAGE = 5

    elif STAGE == 5:
        text = update.effective_message.text
        if text:
            if SIDE:
                update.effective_message.reply_text(
                    text='Положите деньги на XXX и ожидайте подтверждения заявки!',
                )
            else:
                mem = update.effective_message.text
                print(mem)

                params.append(mem)
                add_params(user.id, params)
                params.clear()
                update.effective_message.reply_text(
                    text='Ожидайте подтверждения заявки!',
                )
                send_notification('check for verifications!')


def callback_handler(update: Update, context: CallbackContext):
    global STAGE, SIDE
    user = update.effective_user
    callback_data = update.callback_query.data

    if callback_data == BUY:
        params.append('BUY')
        SIDE = True
        STAGE = 3
        text = 'На какую сумму Вы покупаете? (BUSD)'

    elif callback_data == SELL:
        params.append('SELL')
        SIDE = False
        STAGE = 3
        text = 'На какую сумму Вы продаете? (BUSD)'

    elif callback_data == VERIFY:
        order = find_unverified()
        send_notification(f'order {str(order[0][0])} is verified', order[0][1])

        verify_first_unverified()
        text = 'verified'

        # verify the first one
    elif callback_data == DECLINE:
        order = find_unverified()
        send_notification(f'order {str(order[0][0])} is declined', order[0][1])

        delete_first_unverified()
        text = 'declined'
        # decline the first one
    elif callback_data == WAIT:
        # ignore the first one
        text = 'ignored'
    else:
        text = 'Error'

    update.effective_message.reply_text(
        text=text,
    )


def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Купить', callback_data=BUY)
            ],
            [
                InlineKeyboardButton(text='Продать', callback_data=SELL)
            ],
        ],
    )


def get_keyboard_verification():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Verify', callback_data=VERIFY)
            ],
            [
                InlineKeyboardButton(text='Wait', callback_data=WAIT)
            ],
            [
                InlineKeyboardButton(text='Decline', callback_data=DECLINE)
            ],
        ],
    )


def get_keyboard_manage_orders():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Verify', callback_data=VERIFY)
            ],
            [
                InlineKeyboardButton(text='Wait', callback_data=WAIT)
            ],
            [
                InlineKeyboardButton(text='Decline', callback_data=DECLINE)
            ],
        ],
    )


def main():
    print('Start ArchiveBot')

    req = Request(
        connect_timeout=0.5,
        read_timeout=1.0
    )
    bot = Bot(
        token='2139562951:AAHKCDhPe0wI_AR0BGzBvg8OvDdoIdNxGVI',
        request=req,
        base_url='https://api.telegram.org/bot'
        # хз насчет ссылки
    )
    updater = Updater(
        bot=bot,
        use_context=True
    )

    dp = updater.dispatcher

    info = bot.get_me()
    print(f'Bot info: {info}')

    # init_db(force=True)
    init_db()

    dp.add_handler(CommandHandler("admin", admin_command_handler))
    dp.add_handler(CommandHandler("manage", manage_orders_command_handler))
    dp.add_handler(CommandHandler("start", start_command_handler))
    dp.add_handler(MessageHandler(Filters.all, message_handler))
    dp.add_handler(CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()

    print('Stop ArchiveBot')


if __name__ == '__main__':
    # main()

    p1 = multiprocessing.Process(target=main)
    p1.run()
    p2 = multiprocessing.Process(target=market_making)
    p2.run()
