import logging
import os
from functools import partial
from io import BytesIO
from time import sleep

import redis
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

env = Env()
env.read_env()
_database = None


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_password = env.str("REDIS_PASS")
        database_host = env.str("REDIS_HOST")
        database_port = env.str("REDIS_PORT")
        _database = redis.Redis(
            host=database_host,
            port=database_port,
            password=database_password,
            charset="utf-8",
            decode_responses=True,
        )
    return _database


def receives_product_descriptions(product_id=""):
    params = {"populate": "*"}
    try:
        response = requests.get(
            env.str("PRODUCTS_URL") + product_id,
            params=params,
        )
        response.raise_for_status()
        products = response.json()["data"]
        return products
    except requests.exceptions.HTTPError:
        print("Нет каталога с продуктами")
        raise SystemExit()
