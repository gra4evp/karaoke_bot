from aiogram.utils import executor
from create_bot import dispatcher
from handlers import admin, client, other
from data_base import sqlite_db


sqlite_db.sql_start()

other.register_handlers_other(dispatcher)
client.register_handlers_client(dispatcher)
admin.register_handlers_admin(dispatcher)

executor.start_polling(dispatcher, skip_updates=True)
