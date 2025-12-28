from modules.texts import get_text
from utils.callback import Callback
from utils.permissions import require_registered, require_admin

#@require_registered()
# Note: the registered constraint to work need a way to store registered users' ids
# To check the registered status, an handler must be able to answer GET requests for the "registered" field
async def start_command(update, context):
    await update.message.reply_text(get_text(key="START", update=update))

@require_admin()
async def reload_command(update, context):
    await update.message.reply_text(get_text(key="RELOAD", update=update))

    from utils.cooldown import add_cooldown
    cb = Callback(
        async_func=reload_complete,
        chat=update.message.chat,
        message_id=update.message.message_id,
        user=update.message.from_user,
        action_id="RELOAD"
    )
    add_cooldown(update.message.from_user.id, "RELOAD", 5, cb)

    import bot_status
    bot_status.exit_code = 3 # RELOAD
    bot_status.stop_event.set()

async def reload_complete(**kwargs):
    bot = kwargs['bot']
    await bot.send_message(chat_id=kwargs['chat']['id'], text=get_text(key="RELOAD_COMPLETATO", user=kwargs['user']), reply_to_message_id=kwargs['message_id'])