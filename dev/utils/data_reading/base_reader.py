from abc import ABC, abstractmethod
from typing import Callable, Any
import asyncio
from collections import OrderedDict
import hashlib
import json

MAX_CACHE_SIZE = 20

class BaseReader(ABC):
    def __init__(self):
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = asyncio.Lock()
        self.handlers: dict[str, dict[str, Any]] = {}
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self):
        """Popola self.handlers con key → funzione"""
        pass

    @abstractmethod
    async def _load_from_file(self, key: str) -> Any:
        """Come leggere un item dal file"""
        pass

    @abstractmethod
    async def _save_to_file(self, key: str, value: Any):
        """Come salvare un item nel file (quando viene espulso dalla cache)"""
        pass
    
    @abstractmethod
    async def _has_changed(self, key: str, value: Any) -> bool:
        """Come riconoscere se un item in cache è diverso da quello su file"""
        pass

    async def save_to_file(self, key: str, value: Any):
        if await self._has_changed(key,value):
            print(f"Salvo su file {key} (READER: {self.__class__.__name__})")
            await self._save_to_file(key,value)

    async def set(self, key: str, value: Any):
        """Aggiorna/inserisce in cache, scrive su file solo se espulso"""
        print(f"Setting cache for key: {key} - Val {value}")
        async with self._lock:
            self._cache[key] = value
            self._cache.move_to_end(key)

            if len(self._cache) > MAX_CACHE_SIZE:
                old_key, old_value = self._cache.popitem(last=False)
                await self.save_to_file(old_key, old_value)

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            if key in self._cache:
                print(f"Cache hit for key: {key}")
                self._cache.move_to_end(key)
                return self._cache[key]

        # non in cache → leggi dal file
        print(f"Read from file {key}")
        value = await self._load_from_file(key)
        if value is not None:
            await self.set(key, value)

        return value

    async def clear_cache(self, persist=True):
        """Svuota la cache, salvando prima gli elementi se richiesto"""
        if persist:
            for k, v in self._cache.items():
                await self.save_to_file(k, v)
        self._cache.clear()