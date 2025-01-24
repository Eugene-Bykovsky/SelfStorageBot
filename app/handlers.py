from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from .keyboards import start_keyboard, order_box_keyboard, warehouse_addresses_keyboard

router = Router()


class QuestionStates(StatesGroup):
    choosing_talk = State()
    writing_question = State()
    waiting_for_phone_number = State()


class OrderCourierStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_duration = State()


@router.message(F.text == "/start")
async def start_command(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Привет, {user_name}! 🙋‍♂️\n"
        "Хранение вещей в ячейках для хранения — это удобное, безопасное и практичное решение для тех, кто ищет дополнительное пространство для своих вещей. Этот способ позволяет освободить дом или офис от лишних предметов, при этом сохраняя их в надежном и защищенном месте.Ячейки для хранения могут быть полезны в различных ситуациях: при переезде, во время ремонта, для хранения сезонных вещей, архивов или ценностей..\n\n"
        "Перед началом аренды ознакомьтесь с политикой обработки персональных данных: "
        "[PDF](https://clck.ru/3FKLhp).\n\n"
        'Если вы согласны, нажмите "✅ Согласен". Иначе, нажмите "❌ Не согласен".',
        reply_markup=start_keyboard,
    )


@router.message(F.text == "❌ Не согласен")
async def disagree_command(message: Message):
    await message.answer(
        "Извините, к сожалению, Вы не можете продолжить без подтверждения согласия"
    )


@router.message(F.text == "✅ Согласен")
async def agree_command(message: Message):
    main_menu_markup = InlineKeyboardMarkup(
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
    await message.answer("Главное меню:", reply_markup=main_menu_markup)


@router.callback_query(F.data == "usage_rules")
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


@router.callback_query(F.data == "contact_admin")
async def contact_admin_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Оставьте номер телефона, наш оператор свяжется с Вами"
    )
    await state.set_state(QuestionStates.waiting_for_phone_number)
    await callback_query.answer()


@router.message(QuestionStates.waiting_for_phone_number)
async def phone_number_handler(message: Message, state: FSMContext):
    user_phone = message.text
    await message.answer("Спасибо, ожидайте звонка")
    await state.clear()


@router.callback_query(F.data == "storage_conditions")
async def storage_conditions_handler(callback_query: CallbackQuery):
    tariff_message = (
        "Список тарифов на аренду ячеек:\n\n"
        "1. Минимальный: Объем до 1 м³: 100 р./день\n"
        "2. Стандарт: Объем 1-5 м³: 300 р./день\n"
        "3. Премиум: Объем больше 5 м³: 500 р./день\n"
    )
    await callback_query.message.answer(tariff_message)
    await callback_query.answer()


@router.callback_query(F.data == "order_box")
async def order_box_handler(callback_query: CallbackQuery):
    order_box_markup = InlineKeyboardMarkup(
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
    await callback_query.message.answer(
        "Выберите действие:", reply_markup=order_box_markup
    )
    await callback_query.answer()


@router.callback_query(F.data == "warehouse_addresses")
async def warehouse_addresses_handler(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Выберите адрес склада:", reply_markup=warehouse_addresses_keyboard
    )
    await callback_query.answer()


@router.callback_query(
    F.data.in_(["address_1", "address_2", "address_3", "address_4", "address_5"])
)
async def address_handler(callback_query: CallbackQuery):
    await callback_query.message.answer("Спасибо, ожидаем Вас по выбранному адресу")
    await callback_query.answer()


@router.callback_query(F.data == "order_courier")
async def order_courier_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Пожалуйста, введите Ваш номер телефона.")
    await callback_query.answer()
    await state.set_state(OrderCourierStates.waiting_for_phone)


@router.message(OrderCourierStates.waiting_for_phone)
async def phone_input(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)

    await message.answer("Пожалуйста, введите ваш адрес")
    await state.set_state(OrderCourierStates.waiting_for_address)


@router.message(OrderCourierStates.waiting_for_address)
async def address_input(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    await message.answer("Пожалуйста, укажите продолжительность аренды (в днях)")
    await state.set_state(OrderCourierStates.waiting_for_duration)


@router.message(OrderCourierStates.waiting_for_duration)
async def duration_input(message: Message, state: FSMContext):
    await state.update_data(duration=message.text)

    user_data = await state.get_data()
    await message.answer(
        f"Спасибо! Ваши данные:\n"
        f"Телефон: {user_data['phone']}\n"
        f"Адрес: {user_data['address']}\n"
        f"Продолжительность аренды: {user_data['duration']} дней\n"
        "Ваши данные были успешно отправлены. Наш оператор свяжется с Вами для уточнения деталей"
    )
    await state.clear()


@router.callback_query(F.data == "my_orders")
async def my_orders_handler(callback_query: CallbackQuery):
    orders = [
        {"id": 1, "address": "ул. Примерная, д. 1", "end_date": "2023-12-31"},
        {"id": 2, "address": "ул. Образцовая, д. 2", "end_date": "2024-01-15"},
    ]

    for order in orders:
        order_text = (
            f"Заказ ID: {order['id']}\n"
            f"Адрес: {order['address']}\n"
            f"Дата окончания: {order['end_date']}\n"
        )

        order_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔍 Запросить QR-код к товару",
                        callback_data=f'request_qr_{order["id"]}',
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ℹ️ Подробная информация",
                        callback_data=f'order_details_{order["id"]}',
                    )
                ],
            ]
        )

        await callback_query.message.answer(order_text, reply_markup=order_markup)

    await callback_query.answer()


@router.callback_query(F.data.startswith("order_details_"))
async def order_details_handler(callback_query: CallbackQuery):
    order_id = int(callback_query.data.split("_")[2])

    orders = {
        1: {
            "tariff": "Стандарт",
            "end_date": "2023-12-31",
            "address": "ул. Примерная, д. 1",
        },
        2: {
            "tariff": "Премиум",
            "end_date": "2024-01-15",
            "address": "ул. Образцовая, д. 2",
        },
        3: {
            "tariff": "Минимальный",
            "end_date": "2024-01-15",
            "address": "ул. Колесникова, д. 8",
        },
    }

    if order_id in orders:
        order = orders[order_id]
        current_date = datetime.now().date()
        end_date = datetime.strptime(order["end_date"], "%Y-%m-%d").date()
        remaining_days = (end_date - current_date).days

        details_text = (
            f"Детали заказа ID: {order_id}\n"
            f"Выбранный тариф: {order['tariff']}\n"
            f"Оставшийся срок хранения: {remaining_days} дней\n"
            f"Адрес хранения: {order['address']}\n"
        )

        await callback_query.message.answer(details_text)

    await callback_query.answer()


@router.callback_query(F.data.startswith("request_qr_"))
async def courier_order_handler(callback_query: CallbackQuery):
    image_url = "https://avatars.mds.yandex.net/i?id=55981026a1aba60200c3c8fd7c3ca02f977919dd-13217315-images-thumbs&n=13"
    await callback_query.message.answer_photo(photo=image_url, caption="Ваш QR-код")
    await callback_query.answer()
