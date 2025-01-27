from aiogram.types import CallbackQuery
from aiogram import F, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import aiohttp  # Для взаимодействия с VK API


VK_API_TOKEN = "d74d7d96d74d7d96d74d7d9662d4654931dd74dd74d7d96b0d9bcdfe76fcba1f352ec7a"
VK_API_BASE_URL = "https://api.vk.com/method"

# Хранилище для рекламных ссылок 
ads_links = [
    "https://vk.cc/cHOh6l",
    "https://vk.cc/example2",  # Пример второй ссылки
]

start_router = Router()


async def get_clicks_count(link):
    """
    Получение количества переходов через VK API.
    """
    async with aiohttp.ClientSession() as session:
        # Получаем короткий идентификатор ссылки (после vk.cc/)
        short_key = link.split("/")[-1]

        # Формируем запрос к API
        params = {
            "access_token": VK_API_TOKEN,
            "v": "5.131",
            "key": short_key,
        }
        async with session.get(f"{VK_API_BASE_URL}/utils.getLinkStats", params=params) as response:
            data = await response.json()
            
            if "response" in data:
                return data["response"]["stats"][-1]["views"]  # Последнее значение статистики
            else:
                return 0  # Если данные не найдены или ошибка


async def get_ads_keyboard():
    """
    Генерация клавиатуры для списка рекламных ссылок.
    """
    keyboard = InlineKeyboardBuilder()

    # Кнопка для каждой ссылки
    for link in ads_links:
        clicks = await get_clicks_count(link)  # Получаем количество переходов
        button_text = f"{link} - {clicks} переходов"
        callback_data = f"ad_click:{link}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    # Настройка клавиатуры (по одной кнопке в строке)
    keyboard.adjust(1)
    return keyboard.as_markup()


@start_router.callback_query_handler(lambda c: c.data == "ads")
async def show_ads(callback_query: CallbackQuery):
    """
    Обработчик нажатия кнопки "Реклама".
    """
    keyboard = await get_ads_keyboard()
    await callback_query.message.answer("Рекламные ссылки:", reply_markup=keyboard)


@start_router.callback_query_handler(lambda c: c.data.startswith("ad_click"))
async def ad_click(callback_query: CallbackQuery):
    """
    Обработка клика по рекламной ссылке.
    """
    link = callback_query.data.split(":", 1)[1]  # Извлекаем ссылку из callback_data

    if link in ads_links:
        # Уведомляем пользователя и отправляем ссылку
        await callback_query.message.answer(f"Ссылка открывается: {link}")
    else:
        # Если ссылка не найдена
        await callback_query.message.answer("Ссылка не найдена. Попробуйте позже.")
