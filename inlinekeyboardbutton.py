from environs import Env
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

env = Env()
env.read_env()


def generates_menu_buttons(products):
    products = products
    keyboard = []
    for product in products:
        keyboard.append(
            [
                InlineKeyboardButton(
                    product["attributes"]["title"],
                    callback_data=str(str(product["id"])),
                ),
            ]
        )
    reply_markup = InlineKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
    )
    return reply_markup


def creates_buttons_product_description(product_id):
    keyboard = [
        [
            InlineKeyboardButton("5кг", callback_data=product_id + " 5"),
            InlineKeyboardButton("10кг", callback_data=product_id + " 10"),
            InlineKeyboardButton("15кг", callback_data=product_id + " 15"),
        ],
        [InlineKeyboardButton("Моя корзина", callback_data="cart")],
        [InlineKeyboardButton("Назад в меню", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def basket_buttons(basket_products):
    keyboard = []
    for product in basket_products:
        title = product["attributes"]["title"]
        product_id = product["id"]
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
    return reply_markup


def buttons_data_verification():
    keyboard = [
        [InlineKeyboardButton("Верно", callback_data="Yes")],
        [InlineKeyboardButton("Неверно", callback_data="pay")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
