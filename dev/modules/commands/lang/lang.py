from modules.texts import get_text
from utils.callback import Callback

async def setlang_command(update, context):
    lang = context.args[0] if context.args else None

    if lang:
        from modules import texts
        lang_mod = texts.load_language(lang)
        if lang_mod:
            from modules.lang import set_preferred_language
            set_preferred_language(lang_mod.LANG_CODE, update.message.from_user.id)
            subs = { "lang": lang_mod.LANG_FULLNAME }
            await update.message.reply_text(get_text(key="LINGUA_IMPOSTATA", update=update, subs=subs))
        else:
            await update.message.reply_text(get_text(key="LINGUA_NON_IMPOSTATA", update=update))
    else:
        await update.message.reply_text(get_text(key="LINGUA_NON_IMPOSTATA", update=update))