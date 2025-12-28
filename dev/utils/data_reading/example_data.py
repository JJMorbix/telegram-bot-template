from utils.data_reading import BaseReader
from data.models import ExampleModel

class ExampleDataReader(BaseReader):
    def _register_handlers(self):
        self.handlers = {
            "example": {"get": self.get_example, "set": self.create_example}
        }

    async def _load_from_file(self, key: str) -> ExampleModel | None:
        async with self._lock:
            return ExampleModel.get_or_none(example_id=key)

    async def _save_to_file(self, key: str, value: ExampleModel):
        async with self._lock:
            data = dict(value.__data__)  # tutti i campi inclusa la PK
            pk_name = value._meta.primary_key.name

            ExampleModel.insert(**data).on_conflict(
                conflict_target=[pk_name],
                update={k: v for k, v in data.items() if k != pk_name}  # aggiorna tutto tranne la PK
            ).execute()

    async def _has_changed(self, key: str, value: ExampleModel) -> bool:
        return bool(value.dirty_fields)

    async def _get_example_model(self, example_id: int) -> ExampleModel | None:
        return await self.get(str(example_id))

    async def get_example(self, example_id: int) -> ExampleModel | None:
        """Recupera i dati di una Esempio"""
        model = await self._get_example_model(example_id)
        if model:
            return model.to_example()
        return None

    async def create_example(self, example_id: int = -1, value : str = "") -> int:
        """Crea una nuova Esempio"""
        if example_id is -1:
            example_id = await self._biggest_example_id() + 1
        model = ExampleModel(example_id=example_id, value=value)

        await self.set(str(example_id), model)
        return example_id

    async def _biggest_example_id(self) -> int:
        from peewee import fn
        async with self._lock:
            if self._cache:
                max_cache_id = max(int(uid) for uid in self._cache.keys())
            else:
                max_cache_id = -1

        # 🔹 massimo id nel DB
        max_db_id = ExampleModel.select(fn.MAX(ExampleModel.example_id)).scalar() or 0

        # 🔹 ritorna il massimo tra i due
        return max(max_cache_id, max_db_id)