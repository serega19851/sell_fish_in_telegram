from functools import partial

from environs import Env
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from bot_hadlers import handle_cart
from bot_hadlers import handle_description
from bot_hadlers import handle_menu
from bot_hadlers import start
from bot_hadlers import telefon_number
from bot_hadlers import waiting_email
from redis_requests import get_database_connection
from redis_requests import receives_product_descriptions


env = Env()
env.read_env()


def handle_users_reply(update, context, db, products):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == "/start":
        user_state = "START"
    else:
        user_state = str(db.get(chat_id))

    states_functions = {
        "START": partial(start, products=products),
        "HANDLE_MENU": handle_menu,
        "HANDLE_DESCRIPTION": partial(handle_description, products=products),
        "HANDLE_CART": partial(handle_cart, products=products),
        "TELEFON_NUMBER": telefon_number,
        "WAITING_EMAIL": waiting_email,
    }
    try:
        state_handler = states_functions[user_state]
        next_state = state_handler(update, context)
        db.set(chat_id, str(next_state))

    except Exception as err:
        print(err)


def telegram_bot():
    token = env.str("BOT_TOKEN")
    updater = Updater(token)

    db = get_database_connection()
    products = receives_product_descriptions()

    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(partial(handle_users_reply, products=products, db=db))
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text, partial(handle_users_reply, products=products, db=db)
        )
    )
    dispatcher.add_handler(
        CommandHandler("start", partial(handle_users_reply, products=products, db=db))
    )
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    telegram_bot()
