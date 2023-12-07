from io import BytesIO

import requests
from environs import Env
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from handler_helper_functions import adds_item_cart
from handler_helper_functions import ends_dialogue
from handler_helper_functions import ID_WEIGHT
from handler_helper_functions import menu
from handler_helper_functions import NUMBER_DIGITS
from handler_helper_functions import PRODUCTS_ID
from handler_helper_functions import sends_cart_details
from handler_helper_functions import sends_information_user
from inlinekeyboardbutton import buttons_data_verification
from inlinekeyboardbutton import creates_buttons_product_description
from inlinekeyboardbutton import generates_menu_buttons
from redis_requests import receives_product_descriptions

env = Env()
env.read_env()


def start(update: Update, context: CallbackContext, products):
    reply_markup = generates_menu_buttons(products)

    if not reply_markup["inline_keyboard"]:
        update.message.reply_text("В продаже товара нет")
        return ConversationHandler.END

    return menu(update, context, products)


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
    text = f"{title} {price} руб/кг\n\n{description}"
    reply_markup = creates_buttons_product_description(product_id)

    picture_url = receives_product_descriptions(product_id)["attributes"]["picture"][
        "data"
    ][index_last_uploaded_photo]["attributes"]["url"]
    image_response = requests.get(env.str("URL") + picture_url)
    image_response.raise_for_status()
    image_data = BytesIO(image_response.content)

    sends_information_user(
        query, user_id, reply_markup, image_data=image_data, text=text
    )
    return "HANDLE_DESCRIPTION"


def handle_description(update: Update, context: CallbackContext, products):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    user_id = query.message.chat_id

    params = {"populate": "*"}
    response = requests.get(env.str("CARTS_URL") + str(user_id), params)
    response.raise_for_status()
    cart_products = response.json()["data"]["attributes"]["products"]["data"]

    if user_reply in "back":
        menu(update, context, products)
        query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return "HANDLE_MENU"

    if user_reply in "cart":
        if not cart_products:
            menu(update, context, products)
            query.bot.delete_message(
                chat_id=user_id, message_id=query.message.message_id
            )
            return "HANDLE_MENU"

        sends_cart_details(update, context)
        query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return "HANDLE_CART"

    if user_reply in ID_WEIGHT.split("|"):
        adds_item_cart(update, context)
        return "HANDLE_DESCRIPTION"


def handle_cart(update: Update, context: CallbackContext, products):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    user_id = query.message.chat_id

    if user_reply in "back":
        menu(update, context, products)
        query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return "HANDLE_MENU"

    if user_reply in "pay":
        query.bot.send_message(chat_id=user_id, text="Оставте почту")
        return "WAITING_EMAIL"

    if user_reply in "Yes":
        return ends_dialogue(update, context)

    if user_reply in PRODUCTS_ID.split("|"):
        products_id = {"data": {"products": {"disconnect": [user_reply]}}}
        requests.put(env.str("CARTS_URL") + str(user_id), json=products_id)
        query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
        return sends_cart_details(update, context, products)

    menu(update, context, products)
    return "HANDLE_MENU"


def sends_information_user(query, user_id, reply_markup, image_data=None, text=None):
    if image_data:
        query.bot.send_photo(
            chat_id=user_id,
            photo=image_data,
            caption=text,
            reply_markup=reply_markup,
        )
        query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    if not image_data:
        query.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
        )


def waiting_email(update: Update, context: CallbackContext):
    replay_text = update.message.text
    user_id = update.message.chat.id

    email_cart = {"data": {"email": replay_text}}
    requests.put(env.str("CARTS_URL") + str(user_id), json=email_cart)

    response = requests.get(env.str("CARTS_URL") + str(user_id))
    response.raise_for_status()

    if not response.json()["data"]["attributes"]["email"]:
        context.bot.send_message(
            chat_id=user_id, text="Не правильный адрес почты попробоуте еще раз"
        )
        return "WAITING_EMAIL"

    context.bot.send_message(chat_id=user_id, text="Введите свой номер")
    return "TELEFON_NUMBER"


def sends_user_data_verification(update, context, url):
    user_id = update.message.chat.id

    response = requests.get(url + str(user_id))
    response.raise_for_status()

    cart_information = response.json()["data"]["attributes"]
    email = cart_information["email"]
    telephon_number = cart_information["telephone"]
    text = f"Ваш емаил: {email}\nВаш номер телефона: {telephon_number}"

    reply_markup = buttons_data_verification()
    sends_information_user(context, user_id, reply_markup, image_data=None, text=text)
    return "HANDLE_CART"


def telefon_number(update, context):
    user_id = update.message.chat.id
    replay_text = update.message.text

    if replay_text.isdigit() and len(replay_text) == NUMBER_DIGITS:
        telefon_nuber = {"data": {"telephone": replay_text}}
        requests.put(env.str("CARTS_URL") + str(user_id), json=telefon_nuber)
        return sends_user_data_verification(update, context, env.str("CARTS_URL"))

    context.bot.send_message(chat_id=user_id, text="Неправельный номер")
    return "TELEFON_NUMBER"
