from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests

from config import API_URL

contact_admin_router = Router()


class ContactAdminStates(StatesGroup):
    waiting_for_phone_number = State()


@contact_admin_router.callback_query(F.data == "contact_admin")
async def contact_admin_handler(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    # Получаем данные о пользователе из API
    user_response = requests.get(f"{API_URL}/users/?telegram_id={telegram_id}")

    if user_response.status_code == 200:
        user_data = user_response.json()

        # Фильтруем пользователя по telegram_id
        user = next((u for u in user_data if u["telegram_id"] == telegram_id), None)

        if user is None:
            await callback_query.message.answer("Пользователь не зарегистрирован. Пожалуйста, зарегистрируйтесь.")
            return

        user_id = user["id"]

        # Сохраняем user_id в состоянии
        await state.update_data(user_id=user_id)

        # Запрашиваем у пользователя номер телефона
        await callback_query.message.answer(
            "Оставьте номер телефона, наш оператор свяжется с Вами."
        )
        await callback_query.answer()

        # Устанавливаем состояние
        await state.set_state(ContactAdminStates.waiting_for_phone_number)
    else:
        await callback_query.message.answer("Произошла ошибка при получении данных о пользователях. Попробуйте позже.")


@contact_admin_router.message(ContactAdminStates.waiting_for_phone_number)
async def handle_admin_phone_number(message: Message, state: FSMContext):
    phone_number = message.text.strip()

    # Проверяем формат номера телефона
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return

    # Получаем user_id из состояния
    state_data = await state.get_data()
    user_id = state_data.get("user_id")

    if not user_id:
        await message.answer("Произошла ошибка: пользователь не найден. Пожалуйста, попробуйте снова.")
        await state.clear()
        return

    # Данные для отправки
    payload = {
        "phone_number": phone_number,
        "call_type": "admin",
        "user": user_id,
    }

    # Логируем данные перед отправкой
    print(f"Отправляем данные в API: {payload}")

    # Отправляем запрос
    response = requests.post(f"{API_URL}/calls/", json=payload)

    if response.status_code == 201:
        await message.answer("Спасибо, ожидайте звонка.")
    else:
        # Логируем ответ от API
        print(f"Ошибка API: {response.status_code}, Ответ: {response.text}")
        await message.answer("Произошла ошибка при создании запроса. Попробуйте позже.")

    # Завершаем состояние
    await state.clear()
