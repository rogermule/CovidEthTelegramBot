from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler
import requests
from Database import Database

'''

'''
updater = Updater(token="1105786287:AAEse9mWu9fNeKAoSernjVZK98v01pRjiT0")
dispatcher = updater.dispatcher

URL = "https://3def29a7.ngrok.io/api/"
database = Database()


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_request(route):
    req = requests.get(url=URL + route, auth=BearerAuth(
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'
        '.eyJhdWQiOiIxIiwianRpIjoiMzE2NTk4ODcxNjYxNmM4OTJmMzE3NGM3ZjdkZWYxZjhkMDcwMWIzMzU5ZTg5YWZiMjM5YWFkMDQ3MDc1MTYwNGU5ZWJjNjczOWU5NmVhYzMiLCJpYXQiOjE1ODQ2MTIxMzMsIm5iZiI6MTU4NDYxMjEzMywiZXhwIjoxNjE2MTQ4MTMzLCJzdWIiOiI5Iiwic2NvcGVzIjpbXX0.A5AQUuNjyD1TigCsWavFFMAth01XCcp00Nu8rUxkJg-wtnr1GPVtY1NCTDZRwKKQ0jKG6xnSH4z0MbOf1YiORX_a61pg2rtzf9f72uLpXcF2TK37qIvUE-Q0XRE_nUhnqRs6HiIque9ulBFSfX-nBscfB-w212GNCJuGxozq5G2E-UEhwRm_rTTyidxTZ9qrAP-_gIwivaJwfEJH6hzh8EvLzKU7RriDk-TM-6crnXzS9FazGFotWbPprI_53JZUI9ggpDvlijPFNkQo-wsrmNyQeGBk7aq-QESlF85b6ZopbNlv_LhItDm1QNTYXyNxtfclhUeDu7JMhnvAXD-tA9ofyztjIjyC79jzl_IBpk4GXTkp3_3hwN88xCbJQCs27rIKEIzkfIOaIwEylXjQYsa3LOevfoyQweKNrxQUFqZb8JQ6BIpHnTXV9FOhdJbWO_q78MR_0GIWtr-nkz4Jlk-3NwTPSw4eCim9l3Y9wVoBsUjw5YUIBFUpTJ1QNTzl4f3izY2XEg0N0o8HYR9K6B34XtYSeEZdH12H2Mr6KRM57O6Lb99cjuSnyXB8WNmKIq6df7i9CFJrl8PNIIHhG0xJBeK3UCHQwWigW_53TxZ1eURhzN87k9X8enq7S_bWcTesRbBJtrSV_Zi5DkEMi6cn9SQlDJGt3uZjLVmuXaI'))
    return req.json()


def start(bot, update):
    user_id = update.message.chat_id
    if database.check_user(user_id):
        parent_id = 0;
        database.update_parent_id(user_id, parent_id)
    menus = []
    req = get_request('nav_menus_list/1')
    for i in req['result']:
        menus.append(i['name'])
        if not database.check_menu(i['id']):
            database.insert_menu(i['id'], i['name'], i['parent'])
    keyboard = [menus[x:x + 2] for x in range(0, len(menus), 2)]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("Select from the following",
                              reply_markup=reply_markup)


def handle_menu(bot, update):
    user_id = update.message.chat_id
    if database.check_user(user_id):
        parent_id = database.get_parent_id(user_id)
    else:
        parent_id = 0
        database.add_status(user_id, parent_id)
    req = get_request('get_parents/' + str(parent_id) + '/' + update.message.text)
    results = req['result']
    database.update_parent_id(user_id, results['id'])
    childs = []
    action = results['action']
    for i in results['childrens']:
        childs.append(i['name'])
    keyboard = [childs[x:x + 2] for x in range(0, len(childs), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text("test", reply_markup=reply_markup)
    if action is not None:
        act_req = get_request('menus/' + str(action))
        menu_result = act_req['result']
        for i in menu_result:
            update.message.reply_text(i['text'])
            bot.send_photo(chat_id=user_id, photo=i['image_url'])


user_info_handler = MessageHandler(Filters.text, handle_menu)
dispatcher.add_handler(user_info_handler)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.start_polling()
