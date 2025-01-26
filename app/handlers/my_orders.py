from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
import requests
import segno
import os

import app.keyboards as kb
from config import API_URL

my_orders_router = Router()


@my_orders_router.callback_query(F.data == "my_orders")
async def my_orders_handler(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id

    # Получение данных пользователя
    user_response = requests.get(f"{API_URL}/users/", params={"telegram_id": telegram_id})

    if user_response.status_code == 200:
        users = user_response.json()

        user = next((u for u in users if u["telegram_id"] == telegram_id), None)

        if user:
            user_id = user["id"]

            # Получение списка заказов
            orders_response = requests.get(f"{API_URL}/contracts/", params={"owner_name": user_id})

            if orders_response.status_code == 200 and orders_response.json():
                orders = orders_response.json()

                # Формирование текста и клавиатуры
                orders_text = "Ваши заказы:\n\n"
                for order in orders:
                    orders_text += (
                        f"📦 Заказ ID: {order['id']}\n"
                        f"📍 Адрес: {order['place_address']}\n"
                        f"📅 Дата окончания хранения: {order['expiration_date']}\n"
                        f"🧳 Содержимое: {order['content']}\n\n"
                    )

                await callback_query.message.answer(
                    orders_text,
                    reply_markup=kb.generate_orders_keyboard(orders)
                )
                await callback_query.answer()
            else:
                await callback_query.message.answer(
                    "Произошла ошибка при загрузке заказов. Попробуйте позже."
                )
                await callback_query.answer()
        else:
            await callback_query.message.answer(
                "Пользователь не найден. Пожалуйста, зарегистрируйтесь."
            )
            await callback_query.answer()
    else:
        await callback_query.message.answer(
            "Произошла ошибка при проверке пользователя. Попробуйте позже."
        )
        await callback_query.answer()


@my_orders_router.callback_query(F.data.startswith("order_"))
async def order_qr_handler(callback_query: CallbackQuery):
    order_id = callback_query.data.split("_")[1]

    # Создание QR-кода
    qr_code = segno.make_qr(order_id)
    file_path = f"qrcodes/qr_{order_id}.png"
    os.makedirs("qrcodes", exist_ok=True)
    qr_code.save(file_path)

    qr_code_file = FSInputFile(file_path)
    await callback_query.message.answer_document(
        document=qr_code_file,
        caption=f"Ваш QR-код для заказа #{order_id}"
    )
    await callback_query.answer()

    os.remove(file_path)
