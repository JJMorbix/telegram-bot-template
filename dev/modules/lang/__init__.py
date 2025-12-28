import json

PREFERENCE_LANG_FILE = "data/preferences/lang.json"

preferences = {}

def set_preferred_language(lang_code, user_id):
    # Set the preferred language for the user
    preferences[str(user_id)] = lang_code

def get_user_language(user_id):
    # Get the user's preferred language, if not present None
    lang = preferences.get(str(user_id))

    return lang

def read_preferences():
    global preferences
    # read preferences from PREFERENCE_LANG_FILE
    with open(PREFERENCE_LANG_FILE, "r") as f:
        data = json.load(f)
        preferences.update(data)

def save_preferences():
    # save preferences to PREFERENCE_LANG_FILE
    with open(PREFERENCE_LANG_FILE, "w") as f:
        json.dump(preferences, f)
