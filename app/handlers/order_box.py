from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests

import app.keyboards as kb
from config import API_URL

order_box_router = Router()


class OrderCourierStates(StatesGroup):
    waiting_for_phone_number = State()
    waiting_for_address = State()
    waiting_for_storage_duration = State()


@order_box_router.callback_query(F.data == "order_box")
async def order_box_handler(callback_query: CallbackQuery):

    await callback_query.message.answer(
        "Выберите действие:", reply_markup=kb.order_box_keyboard
    )
    await callback_query.answer()


@order_box_router.callback_query(F.data == "warehouse_addresses")
async def warehouse_addresses_handler(callback_query: CallbackQuery):
    response = requests.get(f'{API_URL}/pickup-locations')
    if response.status_code == 200 and response.json():
        places = response.json()
        await callback_query.message.answer(
            "Выберите адрес склада:",
            reply_markup=await kb.warehouse_addresses_keyboard(places)
        )
        await callback_query.answer()
    else:
        await callback_query.answer(
            "Произошла ошибка при загрузке адресов складов. Попробуйте позже."
            )
        return


@order_box_router.callback_query(F.data.startswith("location:"))
async def handle_location_callback(callback_query: CallbackQuery):
    _, latitude, longitude = callback_query.data.split(":")

    await callback_query.message.answer(
        f"Вы выбрали склад с координатами:\n"
        f"🌍 Широта: {latitude}, Долгота: {longitude}\n"
        "Спасибо. Ждем Вас по данному адресу."
    )
    await callback_query.message.answer_location(
        latitude=float(latitude),
        longitude=float(longitude)
    )
    await callback_query.answer()


@order_box_router.callback_query(F.data == "order_courier")
async def order_courier_handler(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    # Получаем данные о пользователе из API
    user_response = requests.get(f"{API_URL}/users/?telegram_id={telegram_id}")

    if user_response.status_code == 200:
        user_data = user_response.json()

        # Фильтруем пользователя по telegram_id
        user = next((u for u in user_data if u["telegram_id"] == telegram_id), None)

        if user is None:
            print(f"Пользователь с telegram_id={telegram_id} не найден.")
            await callback_query.message.answer("Пользователь не зарегистрирован. Пожалуйста, зарегистрируйтесь.")
            return

        user_id = user["id"]
        print(f"User ID: {user_id}")

        # Сохраняем user_id в состоянии
        await state.update_data(user_id=user_id)

        # Запрашиваем у пользователя номер телефона
        await callback_query.message.answer(
            "Пожалуйста, введите номер телефона. Наш оператор свяжется с Вами и уточнит детали. "
            "Напоминаем о том, что замеры курьер проводит бесплатно."
        )
        await callback_query.answer()

        # Устанавливаем состояние
        await state.set_state(OrderCourierStates.waiting_for_phone_number)
    else:
        print(f"Ошибка при получении данных о пользователях: {user_response.status_code}")
        await callback_query.message.answer("Произошла ошибка при получении данных о пользователях. Попробуйте позже.")


@order_box_router.message(OrderCourierStates.waiting_for_phone_number)
async def handle_phone_number(message: Message, state: FSMContext):
    phone_number = message.text.strip()

    # Проверяем формат номера телефона
    if not phone_number.isdigit() or len(phone_number) < 10:
        await message.answer("Пожалуйста, введите корректный номер телефона.")
        return

    # Запрашиваем у пользователя адрес
    await message.answer("Пожалуйста, введите адрес, по которому будет осуществляться доставка.")
    await state.set_state(OrderCourierStates.waiting_for_address)

    # Сохраняем номер телефона в состояние
    await state.update_data(phone_number=phone_number)


@order_box_router.message(OrderCourierStates.waiting_for_address)
async def handle_address(message: Message, state: FSMContext):
    address = message.text.strip()

    # Запрашиваем срок хранения
    await message.answer("Пожалуйста, введите срок хранения в днях.")
    await state.update_data(address=address)
    await state.set_state(OrderCourierStates.waiting_for_storage_duration)


@order_box_router.message(OrderCourierStates.waiting_for_storage_duration)
async def handle_storage_duration(message: Message, state: FSMContext):
    try:
        storage_duration = int(message.text.strip())

        # Получаем все данные из состояния
        state_data = await state.get_data()
        phone_number = state_data.get("phone_number")
        address = state_data.get("address")

        # Склеиваем все данные для поля pre_order
        pre_order_data = f"Телефон: {phone_number}, Адрес: {address}, Срок хранения: {storage_duration} дней"

        # Получаем user_id из состояния
        user_id = state_data.get("user_id")

        # Обновляем номер телефона пользователя через API
        response = requests.patch(
            f"{API_URL}/users/{user_id}/",
            json={"phone_number": phone_number}
        )

        if response.status_code == 200:
            # Создаем запрос на вызов курьера с добавленным pre_order
            courier_response = requests.post(
                f"{API_URL}/calls/",
                json={
                    "user": user_id,
                    "call_type": "courier",
                    "pre_order": pre_order_data  # Передаем склеенные данные
                }
            )

            if courier_response.status_code == 201:
                await message.answer("Запрос успешно обработан. Ожидайте звонка.")
            else:
                await message.answer("Произошла ошибка при создании запроса. Попробуйте позже.")
        else:
            await message.answer("Произошла ошибка при обновлении номера телефона. Попробуйте позже.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный срок хранения в днях.")

    # Завершаем состояние
    await state.clear()
