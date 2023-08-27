from aiogram.utils import executor
from create_bot import dispatcher
from handlers import admin, other, visitor, owner, moderator


other.register_other_handlers(dispatcher)
owner.register_owner_handlers(dispatcher)
visitor.register_visitor_handlers(dispatcher)

admin.register_admin_handlers(dispatcher)

executor.start_polling(dispatcher, skip_updates=True)
