from aiogram.utils import executor
from create_bot import dispatcher
from handlers import admin, client, other
from data_base import sqlite_db


sqlite_db.sql_start()

other.register_other_handlers(dispatcher)
client.register_client_handlers(dispatcher)
admin.register_admin_handlers(dispatcher)

executor.start_polling(dispatcher, skip_updates=True)
