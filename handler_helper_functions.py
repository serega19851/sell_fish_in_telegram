import requests
from environs import Env
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler

from inlinekeyboardbutton import basket_buttons
from inlinekeyboardbutton import generates_menu_buttons
from redis_requests import receives_product_descriptions

env = Env()
env.read_env()


def combines_weight_with_id():
    id_weight = ""
    for product in receives_product_descriptions():
        id_weight += str(product["id"]) + " 5|"
        id_weight += str(product["id"]) + " 10|"
        id_weight += str(product["id"]) + " 15|"
    id_weight.split("|")
    return id_weight


NUMBER_DIGITS = 10
PRODUCTS_ID = ("|").join(
    [str(product["id"]) for product in receives_product_descriptions()]
)
ID_WEIGHT = combines_weight_with_id()


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


def menu(update, context, products):
    reply_markup = generates_menu_buttons(products)
    text = "Пожалуйста, выберите товар!"

    if update.message:
        user_id = update.message.chat_id
        update.message.reply_text(text, reply_markup=reply_markup)
        return "HANDLE_MENU"
    elif update.callback_query:
        user_id = update.callback_query.message.chat_id
        sends_information_user(
            update.callback_query,
            user_id,
            reply_markup,
            image_data=None,
            text=text,
        )
        return "HANDLE_MENU"
    else:
        return None


def adds_item_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    product_id, quantity_kg = query.data.split(" ")
    user_id = query.message.chat_id

    response = requests.get(env.str("CARTS_URL"))
    response.raise_for_status()

    carts = response.json()["data"]
    url_products = env.str("PRODUCTS_URL")
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
                requests.post(env.str("CARTS_URL"), json=new_user_cart)

        requests.put(env.str("CARTS_URL") + str(user_id), json=existing_cart)

    requests.post(env.str("CARTS_URL"), json=new_user_cart)
    requests.put(url_products + str(product_id), json=fish_weight)


def sends_cart_details(update: Update, context: CallbackContext, products=None):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id

    response = requests.get(env.str("CARTS_URL"))
    response.raise_for_status()
    carts = response.json()["data"]

    if not carts:
        return None

    params = {"populate": "*"}
    response = requests.get(env.str("CARTS_URL") + str(user_id), params=params)
    response.raise_for_status()
    basket_products = response.json()["data"]["attributes"]["products"]["data"]
    reply_markup = basket_buttons(basket_products)

    if not basket_products:
        menu(update, context, products)
        return "HANDLE_MENU"

    if basket_products:
        cart_information = ""
        for product in basket_products:
            title = product["attributes"]["title"]
            quantity_kg = product["attributes"]["quantity_kg"]
            price = product["attributes"]["price"]
            total = str(quantity_kg * price)

            cart_information += f"""{title.upper()} цена - {
              str(price)
              } руб/кг\nВЕС - {quantity_kg} кг \nОБЩАЯ СУММА - {total} руб\n\n"""

        sends_information_user(
            query, user_id, reply_markup, image_data=None, text=cart_information
        )
        return "HANDLE_CART"
    query.bot.delete_message(chat_id=user_id, message_id=query.message.message_id)
    return "HANDLE_CART"


def ends_dialogue(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.message.chat_id
    query.bot.send_message(chat_id=user_id, text="Спасибо, мы с вами свяжемся")
    return ConversationHandler.END
