from flask import Flask, render_template, send_from_directory, request, jsonify, redirect
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ChatMember
from aiogram.filters import Command
from aiogram import F
from threading import Thread
from db_utils import add_user, get_user, update_user_coins, update_invited_friends, award_referral_bonus

# === Настройки Telegram-бота ===
TOKEN = '7930529716:AAF5TYEKKTsG_jUD3k0gtzIa3YvAfikUIdk'

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Настройки Flask-сервера ===
app = Flask(__name__, static_folder='../src', template_folder='../src')


# === Роуты Flask ===
@app.route('/')
def index():
    user_id = request.args.get('user_id', 0)
    username = request.args.get('username', 'Guest')
    user = get_user(user_id)

    if user:
        # Определяем монеты до следующего уровня
        level_thresholds = [
            0,  # Уровень 1
            5000,  # Уровень 2
            25000,  # Уровень 3
            100000,  # Уровень 4
            1000000,  # Уровень 5
            2000000,  # Уровень 6
            10000000,  # Уровень 7
            50000000,  # Уровень 8
            1000000000,  # Уровень 9
            10000000000  # Уровень 10
        ]

        # Уровень пользователя
        current_level = user.level
        if current_level < len(level_thresholds):
            next_level_coins = level_thresholds[current_level] - level_thresholds[current_level - 1]
        else:
            next_level_coins = "Maximum level"  # If max level, display this text

        return render_template(
            'index.html',
            user_id=user.user_id,
            username=user.username,
            coins=user.coins,
            profit_per_tap=user.profit_per_tap,
            profit_per_hour=user.profit_per_hour,
            level=user.level,
            next_level_coins=next_level_coins  # Количество монет для следующего уровня
        )
    else:
        return render_template(
            'index.html',
            user_id=user_id,
            username=username,
            coins=0,
            profit_per_tap=1,
            profit_per_hour=0,
            level=1,
            next_level_coins=5000  # Начальное значение для уровня 2
        )

@app.route('/mine')
def mine():
    user_id = request.args.get('user_id', 0)
    username = request.args.get('username', 'Guest')
    return render_template('mine.html', user_id=user_id, username=username)

@app.route('/friends')
def friends():
    user_id = request.args.get('user_id', 0)
    username = request.args.get('username', 'Guest')
    return render_template('friend.html', user_id=user_id, username=username)

@app.route('/earn')
def earn():
    user_id = request.args.get('user_id', 0)
    username = request.args.get('username', 'Guest')
    return render_template('earn.html', user_id=user_id, username=username)

@app.route('/airdrop')
def airdrop():
    user_id = request.args.get('user_id', 0)
    username = request.args.get('username', 'Guest')
    return render_template('airdrop.html', user_id=user_id, username=username)


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../src', filename)


@app.route('/assets/<path:filename>')
def assets_files(filename):
    return send_from_directory('../src/assets', filename)


# Новый роут для рендеринга шаблона с именем пользователя
@app.route('/user/<username>')
def user(username):
    user_id = request.args.get('user_id', 0)  # Получение user_id
    user = get_user(user_id)  # Получаем пользователя из БД

    if user:
        # Определяем монеты до следующего уровня
        level_thresholds = [
            0,          # Уровень 1
            5000,       # Уровень 2
            25000,      # Уровень 3
            100000,     # Уровень 4
            1000000,    # Уровень 5
            2000000,    # Уровень 6
            10000000,   # Уровень 7
            50000000,   # Уровень 8
            1000000000, # Уровень 9
            10000000000# Уровень 10
        ]

        # Уровень пользователя
        current_level = user.level
        if current_level < len(level_thresholds):
            next_level_coins = level_thresholds[current_level] - level_thresholds[current_level - 1]
        else:
            next_level_coins = "Maximum level"  # If max level, display this text

        return render_template(
            'index.html',
            username=user.username,
            user_id=user.user_id,
            coins=user.coins,
            profit_per_tap=user.profit_per_tap,
            profit_per_hour=user.profit_per_hour,
            level=user.level,
            next_level_coins=next_level_coins  # Количество монет для следующего уровня
        )
    else:
        return render_template(
            'index.html',
            username=username,
            user_id=0,
            coins=0,
            profit_per_tap=1,
            profit_per_hour=0,
            level=1,
            next_level_coins=5000  # Начальное значение для уровня 2
        )




@app.route('/user_data', methods=['GET'])
def user_data():
    user_id = request.args.get('user_id', 0)
    user = get_user(user_id)
    if user:
        # Определяем пороги уровней
        level_thresholds = [
            0, 5000, 25000, 100000, 1000000,
            2000000, 10000000, 50000000, 1000000000, 10000000000
        ]

        # Рассчитываем монеты до следующего уровня
        if user.level < len(level_thresholds):
            next_level_coins = level_thresholds[user.level] - user.coins
        else:
            next_level_coins = "Maximum level"  # Максимальный уровень

        return jsonify(
            success=True,
            coins=user.coins,
            profit_per_tap=user.profit_per_tap,
            profit_per_hour=user.profit_per_hour,
            level=user.level,
            next_level_coins=next_level_coins
        )
    else:
        return jsonify(success=False, error="User not found"), 404



@app.route('/update_coins', methods=['POST'])
def update_coins():
    try:
        data = request.get_json()
        user_id = request.headers.get('User-ID')
        coins = data.get('coins')

        if not user_id or coins is None:
            return jsonify(success=False, error="Invalid data"), 400

        user_id = int(user_id)
        coins = int(coins)

        user = get_user(user_id)
        if user:
            level_thresholds = [
                0, 5000, 25000, 100000, 1000000,
                2000000, 10000000, 50000000, 1000000000, 10000000000
            ]

            # Определяем новый уровень
            new_level = next((i + 1 for i, threshold in enumerate(level_thresholds) if coins < threshold),
                             len(level_thresholds))

            # Уровень только растёт
            if new_level > user.level:
                user.level = new_level

            # Обновляем монеты
            update_user_coins(user_id, coins)

            return jsonify(success=True)
        else:
            return jsonify(success=False, error="User not found"), 404

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500



@app.route('/update_profit_per_hour', methods=['POST'])
def update_profit_per_hour():
    try:
        data = request.get_json()
        user_id = request.headers.get('User-ID')
        profit_per_hour = data.get('profit_per_hour')

        if not user_id or profit_per_hour is None:
            return jsonify(success=False, error="Invalid data"), 400

        update_profit_per_hour(int(user_id), float(profit_per_hour))
        return jsonify(success=True)
    except Exception as e:
        print(f"Error in /update_profit_per_hour: {e}")
        return jsonify(success=False, error=str(e)), 500




# === Telegram-бот: Обработчики ===

# Добавляем новый роут для обработки ссылки приглашения
@app.route('/invite')
def invite():
    referrer_id = request.args.get('referrer_id')
    if not referrer_id:
        return jsonify(success=False, error="Referrer ID is missing"), 400

    # Здесь можно добавить логику для получения информации о пригласившем
    referrer = get_user(referrer_id)
    if not referrer:
        return jsonify(success=False, error="Referrer not found"), 404

    # Генерируем уникальную ссылку для запуска Telegram мини-аппа
    telegram_app_url = f"https://t.me/MMM_Coin_bot?start=referrer_{referrer_id}"

    # Перенаправляем пользователя на Telegram мини-апп
    return redirect(telegram_app_url)


@app.route('/invited_friends', methods=['GET'])
def invited_friends():
    user_id = request.args.get('user_id', 0)
    user = get_user(user_id)
    if user:
        referrals = user.friends_usernames.split(',') if user.friends_usernames else []
        return jsonify(success=True, referrals=[{"name": name} for name in referrals])
    else:
        return jsonify(success=False, error="User not found"), 404

# server.py

@app.route('/award_referral_bonus', methods=['POST'])
def handle_referral_bonus():
    try:
        data = request.get_json()
        invitee_user_id = data.get('invitee_user_id')
        referrer_id = data.get('referrer_id')
        premium = data.get('premium', False)  # Получаем значение премиум

        if not invitee_user_id or not referrer_id:
            return jsonify(success=False, error="Invalid data"), 400

        award_referral_bonus(invitee_user_id, referrer_id, premium)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500



#тестить завтра


async def check_premium_status(user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=user_id, user_id=user_id)
        premium_status = chat_member.user.is_premium if hasattr(chat_member.user, 'is_premium') else False
        print(f"User {user_id} premium status: {premium_status}")
        return premium_status
    except Exception as e:
        print(f"Error checking premium status for user {user_id}: {e}")
        return False

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "User"

    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    web_app_url = f"https://d6b5-2a0d-5600-44-5000-00-1c14.ngrok-free.app/user/{username}?user_id={user_id}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Играть в 1 клик 🎮', web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text='Подписаться на канал 📢', url='https://t.me/your_channel')],
        [InlineKeyboardButton(text='Как заработать на игре 💰', callback_data='how_to_earn')]
    ])

    referrer_id = None
    if args and args[0].startswith('referrer_'):
        referrer_id = args[0].split('_')[1]

    existing_user = get_user(user_id)
    if existing_user:
        await message.answer(
            "Привет! Добро пожаловать в MMM Coin 🎮!\n"
            "Отныне ты — директор. Тапай по экрану, собирай монеты, качай пассивный доход,"
            " разрабатывай собственную стратегию дохода."
            "\nПро друзей не забывай — зови их в игру и получайте вместе ещё больше монет!",
            reply_markup=keyboard
        )
        return

    new_user = add_user(user_id, username, referrer_id=referrer_id)

    if referrer_id:
        premium_status = await check_premium_status(user_id)
        award_referral_bonus(user_id, referrer_id, premium_status)

    await message.answer(
        "Привет! Добро пожаловать в MMM Coin 🎮!\n"
        "Отныне ты — директор. Тапай по экрану, собирай монеты, качай пассивный доход,"
        " разрабатывай собственную стратегию дохода."
        "\nПро друзей не забывай — зови их в игру и получайте вместе ещё больше монет!",
        reply_markup=keyboard
    )



@dp.callback_query(F.data.in_({'how_to_earn'}))
async def button_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or callback_query.from_user.first_name or "User"

    web_app_url = f"https://a3da-2a0d-5600-44-9000-00-24c4.ngrok-free.app/user/{username}?user_id={user_id}"
    keyboards = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Играть в 1 клик 🎮', web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton(text='Подписаться на канал 📢', url='https://t.me/your_channel')]
    ])

    await callback_query.message.answer(
        "Как играть в MMMCoin?\n"
        "💰Tap to earn\nТапай по экрану и собирай монеты.\n"
        "\n⛏Mine\nПрокачивай карточки, которые дадут возможность пассивного дохода.\n"
        "\n⏰ Прибыль в час\nБиржа будет работать для тебя самостоятельно, даже когда ты не в игре в течение"
        " 3х часов. Далее нужно будет перезайти в игру снова.\n"
        "\n📈 LVL\nЧем больше монет у тебя на балансе — тем выше уровень биржи."
        " Чем выше уровень — тем быстрее сможешь зарабатывать ещё больше монет.\n"
        "\n👥 Friends\nПриглашай своих друзей, и вы получите бонусы. Помоги другу перейти в следующие лиги,"
        " и вы получите ещё больше бонусов.",
        reply_markup=keyboards
    )

    await callback_query.answer()


# === Запуск Telegram-бота ===
async def telegram_main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# === Запуск Flask и Telegram параллельно ===
def run_flask():
    app.run(host='0.0.0.0', port=5000, use_reloader=False)


if __name__ == '__main__':
    # Flask запускается в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Telegram запускается в основном asyncio-событии
    asyncio.run(telegram_main())
