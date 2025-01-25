from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.keyboards as kb

order_box_router = Router()


@order_box_router.callback_query(F.data == "order_box")
async def order_box_handler(callback_query: CallbackQuery):

    await callback_query.message.answer(
        "Выберите действие:", reply_markup=kb.order_box_keyboard
    )
    await callback_query.answer()