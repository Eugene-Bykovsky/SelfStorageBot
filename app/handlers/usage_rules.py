from aiogram import F, Router
from aiogram.types import CallbackQuery


usage_rules_router = Router()


@usage_rules_router.callback_query(F.data == "usage_rules")
async def usage_rules_handler(callback_query: CallbackQuery):
    usage_rules_text = (
        "Правила пользования сервисом:\n\n"
        "Можно хранить:\n"
        " - Личные вещи\n"
        " - Бытовая техника\n"
        " - Мебель\n"
        " - Сезонные вещи\n"
        "\nНельзя хранить:\n"
        " - Легковоспламеняющиеся вещества\n"
        " - Токсичные или опасные материалы\n"
        " - Живые существа\n"
        " - Нелегальные товары\n"
    )

    await callback_query.message.answer(usage_rules_text)
    await callback_query.answer()
