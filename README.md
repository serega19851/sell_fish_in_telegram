# Продаём рыбу в телеграм

Данный проект позволяет с помощью `бота` покупать рыбу в `телеграме`.

## Что необходимо для запуска

Для данного проекта необходим `Python3.6` (или выше).
Создадим виртуальное окружение в корневой директории проекта:

```
python3 -m venv env
```

После активации виртуального окружения установим необходимые зависимости:

```
pip install -r requirements.txt
```

Также заранее создадим файл `.env` в директории проекта.

## Создайте аккаунт

🚀 Getting started with Strapi

Strapi comes with a full featured [Command Line Interface](https://docs.strapi.io/dev-docs/cli) (CLI) which lets you scaffold and manage your project in seconds.

### `develop`

Start your Strapi application with autoReload enabled. [Learn more](https://docs.strapi.io/dev-docs/cli#strapi-develop)

```
npm run develop
# or
yarn develop
```

### `start`

Start your Strapi application with autoReload disabled. [Learn more](https://docs.strapi.io/dev-docs/cli#strapi-start)

```
npm run start
# or
yarn start
```

### `build`

Build your admin panel. [Learn more](https://docs.strapi.io/dev-docs/cli#strapi-build)

```
npm run build
# or
yarn build
```

## Создайте 2 модели

![Иллюстрация к проекту](https://github.com/serega19851/sell_fish_in_telegram/raw/main/illustrations_redmi/Снимок%20экрана%20от%202023-11-30%2010-17-09.png)
![Иллюстрация к проекту](https://github.com/serega19851/sell_fish_in_telegram/raw/main/illustrations_redmi/Снимок%20экрана%20от%202023-11-30%2010-27-02.png)

Свяжите эти таблицы как показано ниже

![Иллюстрация к проекту](https://github.com/serega19851/sell_fish_in_telegram/raw/main/illustrations_redmi/Снимок%20экрана%20от%202023-11-30%2010-27-43.png)

Заполните все обязательные поля в модели Product как на скриншоте

![Иллюстрация к проекту](https://github.com/serega19851/sell_fish_in_telegram/raw/main/illustrations_redmi/Снимок%20экрана%20от%202023-11-30%2012-55-25.png)

Запишите в `.env` адреса url для доступа к созданным моделям и localhost:1337

```
CARTS_URL="http://localhost:1337/api/carts/"
PRODUCTS_URL="http://localhost:1337/api/products/"
URL='http://127.0.0.0:1337'

```

## Создаём бота

Напишите [отцу ботов](https://telegram.me/BotFather) для создания телеграм бота.

Запишите его токен в `.env`:

```
BOT_TOKEN=

```

## Подключаем Redis

Регистрируемся на [Redis](https://redis.com/) и заводим себе удаленную `базу данных`. Для подключения к ней вам понадобятся `host`, `port` и `password`. Запишите их в файле `.env`:

```
REDIS_PORT=
REDIS_PASS=
REDIS_HOST=
```

## Запуск бота

Бот запускается командой

```
python telegram_bot.py
```
