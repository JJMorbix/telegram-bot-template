from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.data_reading import get_data

from modules.texts import get_text

from config import Config

config = Config()

def global_restrict(func):
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        # bannati
        if user_id in[]:
            try:
                await update.effective_message.reply_text(
                    get_text(key="BANNATO", update=update)
                )
            except:
                pass  # callback inline senza message
            return

        # DEV: utenti non autorizzati
        if config.mode == "dev" and user_id not in config.allowed_users and user_id not in config.admins:
            try:
                await update.effective_message.reply_text(
                    get_text(key="NON_AUTORIZZATO", update=update)
                )
            except:
                pass
            return

        # autorizzato → esegue normalmente
        return await func(update, context, *args, **kwargs)

    return wrapper

def require_registered(if_not=None):
    """Decorator parametrizzabile con messaggio personalizzato."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if not await get_data("registered", user_id):
                # default message se non è fornita una funzione
                if if_not is None:
                    msg = get_text(key="NON_REGISTRATO", update=update)
                else:
                    msg = await if_not(update)
                await update.message.reply_text(msg)
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def require_admin(if_not=None):
    """Decorator parametrizzabile con messaggio personalizzato."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            if not user_id in config.admins:
                if if_not is None:
                    msg = get_text(key="ADMIN[NON_AUTORIZZATO]", update=update)
                else:
                    msg = await if_not(update)
                await update.message.reply_text(msg)
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def require_private(if_not=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            # if chat is a group
            if update.message.chat.type != "private":
                if if_not is None:
                    msg = get_text(key="SOLO_PRIVATE", update=update)
                else:
                    msg = await if_not(update)
                await update.message.reply_text(msg)
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def restrict_to_command_author(func):
    @wraps(func)
    async def wrapper(update, context):
        query = update.callback_query
        if not query:
            return

        parts = query.data.split(":")
        try:
            original_user_id = int(parts[-1])
        except ValueError:
            await query.answer(get_text(key="INLINE[ERRORE]", update=update), show_alert=True)
            return

        if query.from_user.id != original_user_id:
            await query.answer(get_text(key="INLINE[SOLO_AUTORE]", update=update), show_alert=True)
            return

        # salvo dati puliti direttamente come attributo temporaneo
        clean_data = ":".join(parts[:-1])

        # chiama la callback normalmente
        await func(update, context, clean_data)

    return wrapper