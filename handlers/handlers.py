from apscheduler.schedulers.background import BackgroundScheduler
from .models import StorageRate, StorageBox
from handlers.keyboard import ( 
    get_main_menu_keyboard,
    get_pickup_points_keyboard,
    get_delivery_options_keyboard, 
    get_storage_rate_keyboard,
    get_date_keyboard,
    get_confirm_keyboard
)

from collections import defaultdict
import datetime
import pytz
from datetime import datetime

timezone = pytz.timezone('Europe/Moscow')
current_time = timezone.localize(datetime.now())

USER_DATA = defaultdict(dict)

# 1. Основной обработчик кнопок
def button_handler(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == "agree":
        USER_DATA[chat_id] = {}
        message = "Спасибо за согласие! Выберите категорию бокса для хранения вещей:"
        reply_markup = get_storage_rate_keyboard()
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

    elif query.data == "disagree":
        message = "К сожалению, вы не можете продолжить без согласия на обработку данных."
        context.bot.send_message(chat_id=chat_id, text=message)

    elif query.data == "order_box":
        message = "Выберите категорию бокса:"
        reply_markup = get_storage_rate_keyboard()
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

    elif query.data.startswith("rate_"):
        rate_id = query.data.split("_")[1]
        USER_DATA[chat_id]["rate_id"] = rate_id
        rate = StorageRate.objects.get(id=rate_id)
        message = f"Вы выбрали бокс категории '{rate.get_volume_category_display()}'. Теперь выберите дату:"
        reply_markup = get_date_keyboard()
        context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

    elif query.data.startswith("date_"):
        raw_date = query.data.split("_")[1]
        USER_DATA[chat_id]["start_date"] = raw_date
        message = f"Вы выбрали дату {raw_date}. Укажите ваш адрес доставки:"
        context.bot.send_message(chat_id=chat_id, text=message)

    elif query.data == "confirm_order":
        rate_id = USER_DATA[chat_id].get("rate_id")
        start_date = USER_DATA[chat_id].get("start_date")
        address = USER_DATA[chat_id].get("address")
        phone = USER_DATA[chat_id].get("phone")

        if not all([rate_id, start_date, address, phone]):
            context.bot.send_message(chat_id=chat_id, text="Ошибка! Укажите все данные для завершения заказа.")
            return

        # Создание записи о заказе
        StorageBox.objects.create(
            user_id=chat_id,
            size=rate_id,
            start_date=start_date,
            address=address,
            is_active=True
        )

        context.bot.send_message(chat_id=chat_id, text="✅ Ваш заказ успешно оформлен. Спасибо!")

    elif query.data == "storage_rules":
        rules = (
            "✅ Разрешено хранить:\n"
            "- Мебель\n"
            "- Одежду\n"
            "- Бытовую технику\n"
            "- Жидкости (в герметичной упаковке)\n\n"
            "❌ Запрещено хранить:\n"
            "- Легковоспламеняющиеся вещества\n"
            "- Оружие\n"
            "- Животных"
        )
        context.bot.send_message(chat_id=chat_id, text=rules)

    elif query.data == "contact_admin":
        message = "Свяжитесь с администратором по номеру: +7 (123) 456-78-90"
        context.bot.send_message(chat_id=chat_id, text=message)

# 2. Обработка ввода адреса пользователем
def address_handler(update, context):
    chat_id = update.message.chat_id
    USER_DATA[chat_id]["address"] = update.message.text
    message = "Адрес сохранён. Укажите ваш номер телефона:"
    context.bot.send_message(chat_id=chat_id, text=message)

# 3. Обработка ввода номера телефона пользователем
def phone_handler(update, context):
    chat_id = update.message.chat_id
    phone = update.message.text
    USER_DATA[chat_id]["phone"] = phone

    message = "Телефон сохранён. Подтвердите ваш заказ:"
    reply_markup = get_confirm_keyboard()
    context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

# 4. Напоминание пользователю о бесплатных замерах
def send_reminder_for_measurement(update, context):
    chat_id = update.message.chat_id
    message = "Не забывайте, что курьер бесплатно произведет замеры перед отправкой."
    context.bot.send_message(chat_id=chat_id, text=message)

# 5. Напоминание о конце срока аренды
def send_rent_expiration_reminder(context):
    orders = StorageBox.objects.all()
    now = timezone.localize(datetime.now())  # Локализуем текущее время

    for order in orders:
        if (order.end_date - now).days == 14:
            context.bot.send_message(order.user_id, "Через 2 недели заканчивается срок аренды ячейки.")

# 6. Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(send_rent_expiration_reminder, 'interval', days=1)
scheduler.start()
