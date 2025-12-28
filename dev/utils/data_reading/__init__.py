from abc import ABC, abstractmethod
from typing import Callable, Any
import importlib
import inspect
import pkgutil
from pathlib import Path
from .base_reader import BaseReader

# 🔹 Manager centrale
class DataReaderManager:
    def __init__(self):
        self.dispatch: dict[str, dict[str, Callable[..., Any]]] = {}
        self._readers: list[BaseReader] = []

    def register_reader(self, reader: "BaseReader"):
        for k, methods in reader.handlers.items():
            if k in self.dispatch:
                raise ValueError(f"Chiave '{k}' già gestita")
            self.dispatch[k] = methods
        self._readers.append(reader)

    async def get_data(self, key: str, *args):
        """Chiama l'handler GET associato alla chiave"""
        handler = self.dispatch.get(key, {}).get("get")
        if not handler:
            raise ValueError(f"Nessun handler GET per '{key}'")
        return await handler(*args)

    async def set_data(self, key: str, item_key: str, *args):
        """Chiama l'handler SET associato alla chiave"""
        handler = self.dispatch.get(key, {}).get("set")
        if not handler:
            raise ValueError(f"Nessun handler SET per '{key}'")
        return await handler(item_key, *args)

    async def clear_all_caches(self):
        for reader in self._readers:
            #print(f"Pulisco {reader}: CACHE = {reader._cache}")
            await reader.clear_cache()  # chiama la funzione specifica del reader

manager = None
def init_readers():
    global manager
    manager = DataReaderManager()
    
    package_dir = Path(__file__).parent
    package_name = __name__
    # scansiona tutti i moduli dentro data_reader/
    for _, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if is_pkg or module_name in {"__init__"}:
            continue  # ignora sottopacchetti e file non rilevanti

        module = importlib.import_module(f"{package_name}.{module_name}")

        # cerca le classi che estendono BaseReader
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseReader) and obj is not BaseReader:
                manager.register_reader(obj())
                print(f"🔹 Registrato reader: {obj.__name__}")

async def get_data(key: str, *args):
    global manager
    if not manager:
        init_readers()
    return await manager.get_data(key, *args)

async def set_data(key: str, item_key: str, *args):
    global manager
    if not manager:
        init_readers()
    return await manager.set_data(key, item_key, *args)

async def save_caches():
    global manager
    if not manager:
        init_readers()
    await manager.clear_all_caches()