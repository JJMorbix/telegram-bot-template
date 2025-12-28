import importlib
import inspect
from telegram import Update
DEFAULT_LANGUAGE = "it"

_loaded_languages = {}

def load_language(lang_code: str):
    if lang_code in _loaded_languages:
        return _loaded_languages[lang_code]
    try:
        mod = importlib.import_module(f"modules.texts.texts_{lang_code}")
        _loaded_languages[lang_code] = mod
        return mod
    except ImportError:
        return None

def split_parts(key, lang_module):
    parts = key.replace("]", "").replace("[", ".").split(".")
    val = lang_module
    for p in parts:
        if isinstance(val, dict):
            val = val[p]
        else:
            val = getattr(val, p)
    return val

def get_from_user(update):
    if update.message:
        return update.message.from_user
    if update.callback_query:
        return update.callback_query.from_user
    if update.inline_query:
        return update.inline_query.from_user
    raise ValueError("Nessun from_user trovato in questo update")

def get_text(key: str, user: dict = None, update: Update = None, subs: dict = None):
    #print(f"user= {user} and update={update}")
    if(update):
        user = get_from_user(update)

        user_id = user.id
        username = user.username or None
        user_first_name = user.first_name or None
        user_last_name = user.last_name or None
    else:
        user_id = user['id']
        username = user['username'] or None
        user_first_name = user['first_name'] or None
        user_last_name = user['last_name'] or None

    from modules.lang import get_user_language
    lang = get_user_language(user_id) or DEFAULT_LANGUAGE
    text = get_text_of_lang(key, lang)

    if isinstance(text, list):
        import random
        text = random.choice(text)

    default_subs = {
        "username": f"@{username}" if username else user_first_name,
        "user_id": user_id,
    }
    subs = {**(subs or {}), **default_subs}

    for k, v in subs.items():
        text = text.replace(f"{{{{{k}}}}}", str(v))

    return text

def get_text_of_lang(key: str, lang: str = None):
    lang = lang or DEFAULT_LANGUAGE
    lang_module = load_language(lang)

    if lang_module:
        try:
            val = split_parts(key, lang_module)
            return val
        except (AttributeError, KeyError):
            pass

    if lang != DEFAULT_LANGUAGE:
        default_module = load_language(DEFAULT_LANGUAGE)
        
        try:
            val = split_parts(key, default_module)
            return val
        except (AttributeError, KeyError):
            pass

    return f"[MISSING REQUESTED STRING \"{key}\"]"

_EXTRA_MODULES = {}  # cache
def EXTRA_MODULE(folder, key_name, lang_module=None):
    """
    Ritorna il valore di un extra module generico.
    
    - folder: nome della cartella sotto /extra/ (es. "adventures", "items")
    - key_name: nome della chiave dentro il modulo extra
    - lang_module: il modulo della lingua principale (opzionale, letto automaticamente se None)
    """
    if lang_module is None:
        lang_module = inspect.getmodule(inspect.stack()[1][0])

    lang_code = getattr(lang_module, "LANG_CODE", None)
    if not lang_code:
        return None

    # chiave cache univoca: (folder, lang_code)
    cache_key = (folder, lang_code)
    if cache_key not in _EXTRA_MODULES:
        try:
            mod = importlib.import_module(f".extra.{folder}.{lang_code}", __package__)
            _EXTRA_MODULES[cache_key] = mod
        except ImportError:
            _EXTRA_MODULES[cache_key] = None

    mod = _EXTRA_MODULES[cache_key]
    if mod:
        return getattr(mod, key_name, get_text_of_lang(f"{folder}.{key_name}", lang_code))
    else:
        return get_text_of_lang(f"{folder}.{key_name}", lang_code)