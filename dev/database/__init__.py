from peewee import SqliteDatabase, Model
import os
import importlib

DATABASE_FILE = "data/bot_data.db"
_conn = None

def get_db_connection():
    global _conn
    if _conn is None:
        _conn = SqliteDatabase(DATABASE_FILE)
    return _conn

def initialize_database(models_dir: str = "data/models"):
    """Importa automaticamente tutti i model e crea le tabelle."""
    db = get_db_connection()
    if db.is_closed():
        db.connect()

    # lista dei model da creare
    models = []

    for filename in os.listdir(models_dir):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        module_name = filename[:-3]
        file_path = os.path.join(models_dir, filename)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # prendi tutte le classi che estendono peewee.Model
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            try:
                if issubclass(attr, Model) and attr is not Model:
                    models.append(attr)
            except TypeError:
                continue

    if models:
        db.create_tables(models)

def close_db_connection():
    db = get_db_connection()
    if not db.is_closed():   # opzionale, evita errori se già chiusa
        db.close()