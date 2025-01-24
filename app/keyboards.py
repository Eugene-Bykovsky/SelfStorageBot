from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Для стартового сообщения
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Согласен")],
        [KeyboardButton(text="❌ Не согласен")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
)

# Клавиатура для меню выбора после "Заказать бокс"
order_box_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📍Адреса складов", callback_data="warehouse_addresses"
            )
        ],
        [InlineKeyboardButton(text="🚚Заказать курьера", callback_data="order_courier")],
    ]
)

# Клавиатура для выбора адресов складов
warehouse_addresses_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📍 Адрес 1", callback_data="address_1")],
        [InlineKeyboardButton(text="📍 Адрес 2", callback_data="address_2")],
        [InlineKeyboardButton(text="📍 Адрес 3", callback_data="address_3")],
        [InlineKeyboardButton(text="📍 Адрес 4", callback_data="address_4")],
        [InlineKeyboardButton(text="📍 Адрес 5", callback_data="address_5")],
    ]
)
