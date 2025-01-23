from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .models import StorageRate
import datetime

def create_keyboard(buttons):
    """Универсальный генератор клавиатур."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(**btn)] for btn in buttons])


def get_main_menu_keyboard():
    buttons = [
        {"text": "📦 Заказать бокс", "callback_data": "order_box"},
        {"text": "📜 Правила хранения", "callback_data": "storage_rules"},
        {"text": "☎️ Связаться с администратором", "callback_data": "contact_admin"}
    ]
    return create_keyboard(buttons)


def get_storage_rate_keyboard():
    rates = StorageRate.objects.all()
    buttons = [{"text": f"{rate.get_volume_category_display()} - {rate.cost_per_day} ₽/день", 
                "callback_data": f"rate_{rate.id}"} for rate in rates]
    return create_keyboard(buttons)


def get_date_keyboard():
    """Клавиатура с выбором даты (на 5 дней вперёд)."""
    today = datetime.datetime.now()
    dates = [today + datetime.timedelta(days=i) for i in range(5)]
    buttons = [{"text": date.strftime("%d-%m-%Y"), "callback_data": f"date_{date.strftime('%Y-%m-%d')}"}
               for date in dates]
    return create_keyboard(buttons)


def get_confirm_keyboard():
    buttons = [
        {"text": "✅ Подтвердить заказ", "callback_data": "confirm_order"}
    ]
    return create_keyboard(buttons)
