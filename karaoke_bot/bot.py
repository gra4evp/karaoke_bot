from aiogram.utils import executor
from create_bot import dispatcher
from karaoke_bot.handlers.scripts.common import other
from karaoke_bot.handlers.scripts.visitor import visitor
from karaoke_bot.handlers.scripts.admin import admin
from karaoke_bot.handlers.scripts.owner import owner

other.register_other_handlers(dispatcher)
owner.register_owner_handlers(dispatcher)
visitor.register_visitor_handlers(dispatcher)
admin.register_admin_handlers(dispatcher)

executor.start_polling(dispatcher, skip_updates=True)
