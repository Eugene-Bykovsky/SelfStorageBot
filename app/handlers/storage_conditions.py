from aiogram import F, Router
from aiogram.types import CallbackQuery


storage_conditions_router = Router()


@storage_conditions_router.callback_query(F.data == "storage_conditions")
async def storage_conditions_handler(callback_query: CallbackQuery):
    tariff_message = (
        "Список тарифов на аренду ячеек:\n\n"
        "1. Минимальный: Объем до 1 м³: 100 р./день\n"
        "2. Стандарт: Объем 1-5 м³: 300 р./день\n"
        "3. Премиум: Объем больше 5 м³: 500 р./день\n"
    )
    await callback_query.message.answer(tariff_message)
    await callback_query.answer()
