from functools import wraps
from telegram import InlineKeyboardButton
from modules.texts import get_text

def add_author_to_callback(func):
    """Aggiunge automaticamente l'user_id alla fine di callback_data."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.pop("user_id")
        keyboard = func(*args, **kwargs)
        
        new_keyboard = []
        for row in keyboard:
            new_row = []
            for btn in row:
                new_row.append(
                    InlineKeyboardButton(btn.text, callback_data=f"{btn.callback_data}:{user_id}")
                )
            new_keyboard.append(new_row)
        return new_keyboard
    return wrapper

from functools import wraps
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def require_confirmation(builder):
    """
    Decorator che chiede conferma prima di eseguire l'azione.

    - builder(update, user, data, canceled: bool) -> (testo, tastiera)
      * canceled=False: messaggio di conferma
      * canceled=True: messaggio di annullamento
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context, query_data: str):
            # query.data può finire per :user_id
            # query_data è uguale ma sicuramente senza id
            query = update.callback_query
            #print(f"query_: {query_data}")
            #print(f"query.: {query.data}")
            await query.answer()
            user = query.from_user
            parts = query.data.split(":")
            action, data = parts[0], ":".join(parts[1:])

            actual_parts = query_data.split(":")
            actual_action, actual_data = actual_parts[0], ":".join(actual_parts[1:])

            #print(f"GUARDO {action} SU {data}")

            # Conferma → esegue la funzione decorata
            if action == "confirm":
                return await func(update, context, actual_data)

            # Annullato → builder con canceled=True
            if action == "cancel":
                text, keyboard = await builder(update, user, actual_data, canceled=True)
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
                    parse_mode="HTML"
                )
                return

            # Step iniziale → builder con canceled=False
            text, _ = await builder(update, user, actual_data, canceled=False)
            text += "\n\n" + get_text(key="CONFERMA[DOMANDA]", update=update)
            keyboard = [
                [
                    InlineKeyboardButton(get_text(key="CONFERMA[SI]", update=update), callback_data=f"confirm:{action}:{data}"),
                    InlineKeyboardButton(get_text(key="CONFERMA[NO]", update=update), callback_data=f"cancel:{action}:{data}")
                ]
            ]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        return wrapper
    return decorator