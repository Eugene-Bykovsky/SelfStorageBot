from aiogram import F, Router
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart

import requests

import app.keyboards as kb
from config import API_URL

start_router = Router()

# Общий текст приветствия
WELCOME_MESSAGE = (
    "Привет, {user_name}! 🙋‍♀️\n"
    "Освободите пространство для жизни: храните всё лишнее, доверяя "
    "сервису SelfStorage."
    "\nХранение вещей в ячейках для хранения — это удобное, безопасное и "
    "практичное решение для тех, кто ищет дополнительное пространство для "
    "своих вещей. Этот способ позволяет освободить дом или офис от лишних "
    "предметов, при этом сохраняя их в надежном и защищенном месте. Ячейки "
    "для хранения могут быть полезны в различных ситуациях: при переезде, "
    "во время ремонта, для хранения сезонных вещей, архивов или "
    "ценностей."
)


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    user_name = message.from_user.first_name
    usef_last_name = message.from_user.last_name

    # Проверяем, есть ли пользователь в базе данных через API
    response = requests.get(f'{API_URL}/users/?search={telegram_id}')

    if response.status_code == 200 and response.json():
        # Пользователь найден
        user_data = response.json()[0]
    else:
        # Если пользователя нет, создаём его
        create_response = requests.post(f'{API_URL}/users/', json={
            'telegram_id': telegram_id,
            'username': user_name + ' ' + usef_last_name,
            'name': user_name,
            'is_active': False  # Новый пользователь по умолчанию неактивен
        })

        if create_response.status_code == 201:  # 201 Created
            user_data = create_response.json()
        else:
            # Если создание пользователя не удалось
            await message.answer(
                "Произошла ошибка при создании пользователя. Попробуйте позже."
            )
            return

    # Проверяем статус пользователя
    if user_data['is_active']:
        # Если пользователь активен, отправляем только приветственное сообщение
        await message.answer(WELCOME_MESSAGE.format(user_name=user_name))
        await message.answer("Главное меню:",
                             reply_markup=kb.main_menu_keyboard)
    else:
        # Если пользователь неактивен, отправляем текст с документом и кнопкой
        await send_consent_message(message, user_name)


async def send_consent_message(message: Message, user_name: str):
    """Функция отправки сообщения с согласием"""
    await message.answer(
        WELCOME_MESSAGE.format(user_name=user_name) + "\n\n"
        "Перед началом использования бота, пожалуйста, ознакомьтесь с "
        "документом о согласии на обработку персональных данных.\n\n"
        "Если вы согласны, нажмите 'Согласен с обработкой персональнных данных'."
        "Иначе, нажмите 'Не согласен с обработкой персональнных данных'.",
        reply_markup=kb.consent_keyboard
    )
    consent_file = FSInputFile("files/soglasie.pdf")
    await message.answer_document(document=consent_file)


@start_router.message(F.text == "Согласен с обработкой персональнных данных")
async def handle_consent(message: Message):
    telegram_id = message.from_user.id

    # Получаем пользователя через API
    response = requests.get(f'{API_URL}/users/?search={telegram_id}')

    if response.status_code == 200 and response.json():
        user_data = response.json()[0]
        user_id = user_data['id']

        # Обновляем статус пользователя на активный
        update_response = requests.patch(f'{API_URL}/users/{user_id}/',
                                         json={'is_active': True})

        if update_response.status_code == 200:
            # Убираем клавиатуру после подтверждения
            await message.answer(
                "Спасибо! 🎉 Ваше согласие зарегистрировано. Теперь вы "
                "можете пользоваться ботом.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await message.answer("Произошла ошибка при обновлении статуса. "
                                 "Попробуйте позже.")
    else:
        await message.answer("Пользователь не найден. Попробуйте начать "
                             "сначала, отправив /start.")

    await message.answer("Главное меню:", reply_markup=kb.main_menu_keyboard)


@start_router.message(F.text == "Не согласен с обработкой "
                                "персональнных данных")
async def disagree_command(message: Message):
    await message.answer(
        "Извините, к сожалению, Вы не можете продолжить без подтверждения "
        "согласия",
        reply_markup=ReplyKeyboardRemove()
    )
