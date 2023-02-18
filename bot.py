import logging
from aiogram import executor
from bot_init import dp
from handlers import client, admin
from database.db import connect_db

logging.basicConfig(level=logging.INFO)
client.register_client_handlers(dp)
admin.register_admin_handlers(dp)


async def on_startup(_):
    connect_db()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
