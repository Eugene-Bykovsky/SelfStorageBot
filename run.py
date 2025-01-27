import asyncio
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.handlers.start import start_router
from app.handlers.order_box import order_box_router
from app.handlers.storage_conditions import storage_conditions_router
from app.handlers.usage_rules import usage_rules_router
from app.handlers.contact_admin import contact_admin_router
from app.handlers.my_orders import my_orders_router

from config import API_URL
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def send_reminders(bot: Bot):
    """Отправляет напоминания клиентам, у которых контракт истекает через 14 дней."""
    logging.info("Начало выполнения задачи send_reminders")

    # Получаем список контрактов, истекающих через 14 дней
    response = requests.get(f"{API_URL}/contracts/expiring_in_14_days/")

    if response.status_code == 200:
        contracts = response.json()
        today = datetime.now().date()

        for contract in contracts:
            expiration_date = datetime.strptime(contract["expiration_date"], "%Y-%m-%d").date()

            # Проверяем, действительно ли срок аренды заканчивается через 14 дней
            reminder_date = expiration_date - timedelta(days=14)
            logging.info(f"Контракт ID: {contract['id']} - Дата истечения: {expiration_date}, Напоминание на: {reminder_date}")

            if reminder_date == today:  # Проверяем, совпадает ли дата напоминания с сегодняшним днем
                logging.info(f"Контракт ID: {contract['id']} подходит для напоминания!")
                owner_id = contract["owner_name"]
                user_response = requests.get(f"{API_URL}/users/{owner_id}")

                if user_response.status_code == 200:
                    user_data = user_response.json()
                    if user_data:
                        telegram_id = user_data.get("telegram_id")
                        if telegram_id:
                            logging.info(f"Попытка отправить сообщение пользователю с telegram_id: {telegram_id}")
                            message = (
                                f"⏳ Уведомление!\n"
                                f"📦 Заказ ID: {contract['id']}\n"
                                f"📍 Адрес: {contract['place_address']}\n"
                                f"🧳 Содержимое: {contract['content']}\n\n"
                                f"⚠️ Через 2 недели заканчивается срок аренды ячейки."
                            )
                            await bot.send_message(chat_id=telegram_id, text=message)
                            logging.info(f"Сообщение отправлено пользователю {telegram_id}")
                    else:
                        logging.warning(f"Telegram ID отсутствует для пользователя {owner_id}")
                else:
                    logging.error(f"Ошибка API при запросе пользователя {owner_id}: {user_response.status_code}")
    else:
        logging.error(f"Ошибка API при запросе контрактов: {response.status_code}")


async def main():
    env = Env()
    env.read_env()
    TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start_router, order_box_router,
                       storage_conditions_router, usage_rules_router,
                       contact_admin_router, my_orders_router,
                       advertisement_router)

    # Планировщик задач
    scheduler = AsyncIOScheduler()
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))
    scheduler.add_job(send_reminders, "cron", hour=20, minute=38, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
