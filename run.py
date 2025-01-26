import asyncio
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers.start import start_router
from app.handlers.order_box import order_box_router
from app.handlers.storage_conditions import storage_conditions_router
from app.handlers.usage_rules import usage_rules_router
from app.handlers.contact_admin import contact_admin_router
from app.handlers.my_orders import my_orders_router


async def main():
    env = Env()
    env.read_env()
    TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start_router, order_box_router,
                       storage_conditions_router, usage_rules_router,
                       contact_admin_router, my_orders_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
