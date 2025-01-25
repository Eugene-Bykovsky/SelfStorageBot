from aiogram import F, Router
from aiogram.types import CallbackQuery
import requests

import app.keyboards as kb
from config import API_URL

order_box_router = Router()


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
async def order_courier_handler(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id 

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

        response = requests.post(
            f"{API_URL}/calls/",
            json={
                "user": user_id,
                "call_type": "courier",
            }
        )

        if response.status_code == 201:
            await callback_query.message.answer("Запрос успешно обработан. Ожидайте звонка.")
        else:
            await callback_query.message.answer("Произошла ошибка при создании запроса. Попробуйте позже.")
    else:
        print(f"Ошибка при получении данных о пользователях: {user_response.status_code}")
        await callback_query.message.answer("Произошла ошибка при получении данных о пользователях.Попробуйте")