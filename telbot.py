from functools import partial
from io import BytesIO
from time import sleep

import requests
from environs import Env
from redis.commands.json.path import Path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from stateclient import saves_last_state_client


HANDLE_MENU, HANDLE_DESCRIPTION, HANDLE_CART, WAITING_EMAIL, TELEFON_NUMBER = range(
    1, 6
)
NUMBER_DIGITS = 10


def receives_product_descriptions(product_id=""):
    params = {"populate": "*"}
    try:
        response = requests.get(
            f"http://localhost:1337/api/products/{product_id}", params=params
        )
        response.raise_for_status()
        products = response.json()["data"]
        return products
    except requests.exceptions.HTTPError:
        print("Нет каталога с продуктами")
        raise SystemExit()


def combines_weight_with_ID():
    id_weight = ""
    for product in receives_product_descriptions():
        id_weight += str(product["id"]) + " 5|"
        id_weight += str(product["id"]) + " 10|"
        id_weight += str(product["id"]) + " 15|"
    return id_weight


PRODUCTS_ID = ("|").join(
    [str(product["id"]) for product in receives_product_descriptions()]
)

ID_WEIGHT = combines_weight_with_ID()


def generates_menu_buttons():
    products = receives_product_descriptions()
    keyboard = []
    for product in products:
        keyboard.append(
            [
                InlineKeyboardButton(
                    product["attributes"]["title"], callback_data=str(product["id"])
                ),
            ]
        )
    reply_markup = InlineKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
    )
    return reply_markup


def start(update: Update, context: CallbackContext):
    reply_markup = generates_menu_buttons()
    if not reply_markup["inline_keyboard"]:
        update.message.reply_text("В продаже товара нет")
        return ConversationHandler.END
    update.message.reply_text("Пожалуйста, выберите товар!", reply_markup=reply_markup)
    return HANDLE_MENU


def handle_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    product_id = query.data
    user_id = query.message.chat_id
    product = receives_product_descriptions(product_id)["attributes"]
    description = product["description"]
    title = product["title"]
    price = product["price"]
    index_last_uploaded_photo = -1
    keyboard = [
        [
            InlineKeyboardButton("5кг", callback_data=product_id + " 5"),
            InlineKeyboardButton("10кг", callback_data=product_id + " 10"),
            InlineKeyboardButton("15кг", callback_data=product_id + " 15"),
        ],
        [InlineKeyboardButton("Моя корзина", callback_data=product_id)],
        [InlineKeyboardButton("Назад в меню", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    picture_url = receives_product_descriptions(product_id)["attributes"]["picture"][
        "data"
    ][index_last_uploaded_photo]["attributes"]["url"]
    image_response = requests.get(f"http://127.0.0.0:1337{picture_url}")
    image_data = BytesIO(image_response.content)
    query.bot.send_photo(
        chat_id=user_id,
        photo=image_data,
        caption=f"{title} {price} руб/кг\n\n{description}",
        reply_markup=reply_markup,
    )
    query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
    saves_last_state_client(user_id, "HANDLE_DESCRIPTION")
    return HANDLE_DESCRIPTION


def handle_description(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    reply_markup = generates_menu_buttons()
    user_id = query.message.chat_id
    query.bot.send_message(
        chat_id=user_id, text="Пожалуйста, выберите товар!", reply_markup=reply_markup
    )
    query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
    saves_last_state_client(user_id, "HANDLE_MENU")
    return HANDLE_MENU


def adds_item_cart(update: Update, context: CallbackContext, url):
    query = update.callback_query
    query.answer()
    product_id, quantity_kg = query.data.split(" ")
    user_id = query.message.chat_id
    response = requests.get(url)  #
    carts = response.json()["data"]
    url_products = "http://localhost:1337/api/products/"
    fish_weight = {
        "data": {
            "quantity_kg": float(quantity_kg),
        },
        "meta": {},
    }
    new_user_cart = {
        "data": {
            "id": user_id,
            "user_id": str(user_id),
            "products": [product_id],
        }
    }
    existing_cart = {"data": {"products": {"connect": [int(product_id)]}}}
    if carts:
        for cart in carts:
            if user_id is not cart["id"]:
                requests.post(url, json=new_user_cart)

        requests.put(url + str(user_id), json=existing_cart)

    requests.post(url, json=new_user_cart)
    requests.put(url_products + str(product_id), json=fish_weight)


def sends_cart_details(update: Update, context: CallbackContext, url):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    params = {"populate": "*"}
    response = requests.get(url)
    carts = response.json()["data"]
    if not carts:
        return None
    response = requests.get(url + str(user_id), params=params)
    response.raise_for_status()
    basket_products = response.json()["data"]["attributes"]["products"]["data"]
    if not basket_products:
        return handle_description(update, context)
    cart_information = ""
    keyboard = []
    for product in basket_products:
        title = product["attributes"]["title"]
        quantity_kg = product["attributes"]["quantity_kg"]
        product_id = product["id"]
        price = product["attributes"]["price"]
        total = str(quantity_kg * price)

        cart_information += f"""{title.upper()} цена - {
            str(price)
            } руб/кг\nВЕС - {quantity_kg} кг \nОБЩАЯ СУММА - {total} руб\n\n"""

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Убрать из корзины {title} ", callback_data=str(product_id)
                )
            ],
        )

    keyboard.extend(
        [
            [InlineKeyboardButton("Оплатить", callback_data="pay")],
            [InlineKeyboardButton("Назад в меню", callback_data="back")],
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.bot.send_message(
        chat_id=user_id, text=cart_information, reply_markup=reply_markup
    )
    query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
    saves_last_state_client(user_id, "HANDLE_CART")
    return HANDLE_CART


def handle_cart(update: Update, context: CallbackContext, url):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    user_id = query.message.chat_id

    if user_reply in "back":
        return handle_description(update, context)

    if user_reply in "pay":
        query.bot.send_message(chat_id=user_id, text="Оставте почту")
        return WAITING_EMAIL

    if user_reply:
        products_id = {"data": {"products": {"disconnect": [user_reply]}}}
        requests.put(url + str(user_id), json=products_id)
        return sends_cart_details(update, context, url)


def waiting_email(update: Update, context: CallbackContext, url):
    replay_text = update.message.text
    user_id = update.message.chat.id
    email_cart = {"data": {"email": replay_text}}
    requests.put(url + str(user_id), json=email_cart)
    response = requests.get(url + str(user_id))

    if not response.json()["data"]["attributes"]["email"]:
        context.bot.send_message(
            chat_id=user_id, text="Не правильный адрес почты попробоуте еще раз"
        )
        return WAITING_EMAIL

    context.bot.send_message(chat_id=user_id, text="Введите свой номер")
    return TELEFON_NUMBER


def telefon_number(update, context, url):
    user_id = update.message.chat.id
    user_id = update.message.chat.id
    replay_text = update.message.text

    if replay_text.isdigit() and len(replay_text) == NUMBER_DIGITS:
        telefon_nuber = {"data": {"telephone": replay_text}}
        requests.put(url + str(user_id), json=telefon_nuber)
        return sends_user_data_verification(update, context, url)

    context.bot.send_message(chat_id=user_id, text="Неправельный номер")
    return TELEFON_NUMBER


def sends_user_data_verification(update, context, url):
    user_id = update.message.chat.id
    response = requests.get(url + str(user_id))
    cart_information = response.json()["data"]["attributes"]
    email = cart_information["email"]
    telephon_number = cart_information["telephone"]

    keyboard = [
        [InlineKeyboardButton("Верно", callback_data="Yes")],
        [InlineKeyboardButton("Неверно", callback_data="pay")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=user_id,
        text=f"Ваш емаил: {email}\nВаш номер телефона: {telephon_number}",
        reply_markup=reply_markup,
    )
    return HANDLE_CART


def ends_dialogue(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    query.bot.send_message(chat_id=user_id, text="Спасибо, мы с вами свяжемся")
    return ConversationHandler.END


def main() -> None:
    env = Env()
    env.read_env()
    telegram_bot_token = env.str("BOT_TOKEN")
    updater = Updater(telegram_bot_token)
    carts_url = "http://localhost:1337/api/carts/"
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            HANDLE_MENU: [
                CallbackQueryHandler(handle_menu, pattern="^" + PRODUCTS_ID + "$"),
            ],
            HANDLE_DESCRIPTION: [
                CallbackQueryHandler(handle_description, pattern="^" + "back" + "$"),
                CallbackQueryHandler(
                    partial(adds_item_cart, url=carts_url),
                    pattern="^" + ID_WEIGHT + "$",
                ),
                CallbackQueryHandler(
                    partial(sends_cart_details, url=carts_url),
                    pattern="^" + PRODUCTS_ID + "$",
                ),
            ],
            HANDLE_CART: [
                CallbackQueryHandler(
                    partial(handle_cart, url=carts_url),
                    pattern="^" + f"{PRODUCTS_ID}|back|pay" + "$",
                ),
                CallbackQueryHandler(ends_dialogue, pattern="^" + "Yes" + "$"),
            ],
            WAITING_EMAIL: [
                MessageHandler(Filters.text, partial(waiting_email, url=carts_url)),
            ],
            TELEFON_NUMBER: [
                MessageHandler(Filters.text, partial(telefon_number, url=carts_url))
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
