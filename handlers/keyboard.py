from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .models import StorageRate, PickupLocation
import pytz
from datetime import datetime, timedelta

timezone = pytz.timezone('Europe/Moscow')  # Указываем временную зону через pytz
local_time = timezone.localize(datetime.now())  # Корректное добавление временной зоны
current_time = timezone.localize(datetime.now())  # Аналогично


def create_keyboard(buttons):
    """Универсальный генератор клавиатур."""
    return InlineKeyboardMarkup([[InlineKeyboardButton(**btn)] for btn in buttons])


# 1. Главное меню
def get_main_menu_keyboard():
    buttons = [
        {"text": "📦 Заказать бокс", "callback_data": "order_box"},
        {"text": "📜 Правила хранения", "callback_data": "storage_rules"},
        {"text": "☎️ Связаться с администратором", "callback_data": "contact_admin"}
    ]
    return create_keyboard(buttons)


# 2. Клавиатура выбора услуги доставки или самовывоза
def get_delivery_options_keyboard():
    buttons = [
        {"text": "🚚 Курьерская доставка", "callback_data": "delivery_courier"},
        {"text": "Самовывоз", "callback_data": "pickup_point"}
    ]
    return create_keyboard(buttons)


# 3. Клавиатура выбора тарифа (категории бокса)
def get_storage_rate_keyboard():
    rates = StorageRate.objects.all()
    buttons = [{"text": f"{rate.get_volume_category_display()} - {rate.cost_per_day} ₽/день", 
                "callback_data": f"rate_{rate.id}"} for rate in rates]
    return create_keyboard(buttons)


# 4. Клавиатура выбора даты
def get_date_keyboard():
    """Клавиатура с выбором даты (на 5 дней вперёд)."""
    today = timezone.localize(datetime.now())  # Локализуем текущую дату
    dates = [today + timedelta(days=i) for i in range(5)]  # timedelta вместо datetime.timedelta
    buttons = [{"text": date.strftime("%d-%m-%Y"), "callback_data": f"date_{date.strftime('%Y-%m-%d')}"}
               for date in dates]
    return create_keyboard(buttons)


# 5. Подтверждение заказа
def get_confirm_keyboard():
    buttons = [
        {"text": "✅ Подтвердить заказ", "callback_data": "confirm_order"}
    ]
    return create_keyboard(buttons)


# 6. Клавиатура точек самовывоза
def get_pickup_points_keyboard():
    points = PickupLocation.objects.all()
    buttons = [{"text": point.name, "callback_data": f"pickup_{point.id}"} for point in points]
    return create_keyboard(buttons)

