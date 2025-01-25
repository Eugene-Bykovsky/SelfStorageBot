from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

consent_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Согласен с обработкой персональнных данных")],
        [KeyboardButton(text="Не согласен с обработкой персональнных данных")]
    ],
    resize_keyboard=True,
)

main_menu_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Заказать бокс", callback_data="order_box")],
            [
                InlineKeyboardButton(
                    text="🗄 Условия хранения", callback_data="storage_conditions"
                )
            ],
            [InlineKeyboardButton(text="📝 Мои заказы", callback_data="my_orders")],
            [
                InlineKeyboardButton(
                    text="📞 Связь с администратором", callback_data="contact_admin"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📃 Правила пользования сервисом", callback_data="usage_rules"
                )
            ],
        ]
    )

order_box_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📍 Адреса складов", callback_data="warehouse_addresses"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚚 Заказать курьера", callback_data="order_courier"
            )
        ],
    ]
)


async def warehouse_addresses_keyboard(places):
    """
    Генератор клавиатуры с адресами и координатами.
    """
    keyboard = InlineKeyboardBuilder()

    for place in places:
        button_text = place["address"]
        callback_data = f"location:{place['latitude']}:{place['longitude']}"

        keyboard.add(InlineKeyboardButton(text=button_text,
                                          callback_data=callback_data))

    return keyboard.as_markup()
