from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart

import app.keyboards as kb

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 🙋‍♀️\n"
        "Освободите пространство для жизни: храните всё лишнее доверяя сервису SelfStorage\n\n"
        "Перед началом использования бота, пожалуйста, ознакомьтесь с "
        "документом "
        "о согласии на обработку персональных данных.\n\n"
        "Нажмите кнопку ниже, чтобы подтвердить согласие:",
        reply_markup=kb.consent_keyboard
    )

    consent_file = FSInputFile("files/soglasie.pdf")
    await message.answer_document(document=consent_file)
