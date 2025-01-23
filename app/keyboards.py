from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

consent_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Согласен с обработкой персональнных данных")],
    ],
    resize_keyboard=True,
)
