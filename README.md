# 🚀 Getting started with Strapi

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

## ⚙️ Deployment

Strapi gives you many possible deployment options for your project including [Strapi Cloud](https://cloud.strapi.io). Browse the [deployment section of the documentation](https://docs.strapi.io/dev-docs/deployment) to find the best solution for your use case.

## 📚 Learn more

- [Resource center](https://strapi.io/resource-center) - Strapi resource center.
- [Strapi documentation](https://docs.strapi.io) - Official Strapi documentation.
- [Strapi tutorials](https://strapi.io/tutorials) - List of tutorials made by the core team and the community.
- [Strapi blog](https://strapi.io/blog) - Official Strapi blog containing articles made by the Strapi team and the community.
- [Changelog](https://strapi.io/changelog) - Find out about the Strapi product updates, new features and general improvements.

Feel free to check out the [Strapi GitHub repository](https://github.com/strapi/strapi). Your feedback and contributions are welcome!

## ✨ Community

- [Discord](https://discord.strapi.io) - Come chat with the Strapi community including the core team.
- [Forum](https://forum.strapi.io/) - Place to discuss, ask questions and find answers, show your Strapi project and get feedback or just talk with other Community members.
- [Awesome Strapi](https://github.com/strapi/awesome-strapi) - A curated list of awesome things related to Strapi.

---

<sub>🤫 Psst! [Strapi is hiring](https://strapi.io/careers).</sub># Продаём рыбу в телеграме
Данный проект позволяет с помощью `бота` покупать покупать рыбу в `телеграме`.
Ознакомиться с работой `бота` можете по [ссылке](https://t.me/norgius_speech_bot).

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

![Иллюстрация к проекту](https://github.com/serega19851/sell_fish_in_telegram/raw/main/illustrations_redmi/Снимок%20экрана%20от%202023-11-30%2010-27-02.png)

<!--  -->
<!-- ![Image alt](https://github.com/{username}/{repository}/raw/{branch}/{path}/image.png) -->
<!--  -->
<!-- {username} — ваш ник на ГитХабе; -->
<!-- {repository} — репозиторий где хранятся картинки; -->
<!-- {branch} — ветка репозитория; -->
<!-- {path} — путь к месту нахождения картинки. -->

## Создайте аккаунт на [Strapi](https://docs.strapi.io/dev-docs/installation/cli)

Далее создайте две модели:

```
ELASTICPATH_CLIENT_SECRET=
ELASTICPATH_CLIENT_ID=
```

Вам также необходимо задать время жизни токена доступа к магазину, который автоматически будет получать бот в процессе своей работы, на текущий момент в [документации](https://documentation.elasticpath.com/commerce-cloud/docs/api/basics/authentication/index.html#:~:text=Authentication%20tokens%20are%20generated%20via%20the%20authentication%20endpoint%20and%20expire%20within%201%20hour.%20They%20need%20to%20be%20then%20regenerated.) указано, что время жизни `токена` равно `1 часу`. Поэтому укажите время `в секундах равное 1 часу` или менее:

```
TOKEN_LIFETIME=
```

Вы можете ограничить или же увеличить количество отображаемых товаров в меню (товар который не отобразился в сообщении можно будет увидеть листая меню специальными кнопками `<` и `>` ), для этого необходимо указать в файле `.env` данное значение, по умолчанию, установлено `6`:

```
PRODUCTS_PER_PAGE=
```

## Создаём бота

Напишите [отцу ботов](https://telegram.me/BotFather) для создания телеграм бота.

Запишите его токен в `.env`:

```
FISH_SHOP_BOT_TG_TOKEN=
```

## Подключаем Redis

Регистрируемся на [Redis](https://redis.com/) и заводим себе удаленную `базу данных`. Для подключения к ней вам понадобятся `host`, `port` и `password`. Запишите их в файле `.env`:

```
REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
```

## Запуск бота

Бот запускается командой

```
python bot.py
```
