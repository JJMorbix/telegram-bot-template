from peewee import Model, SqliteDatabase, IntegerField, CharField, TextField
from database import get_db_connection

from modules.example import Example

class PeeweeExampleModel(Model):
    example_id = IntegerField(primary_key=True)
    value = CharField(max_length=30, default="")
    class Meta:
        database = get_db_connection()

    def to_example(self) -> Example:
        """Trasforma il record DB in un oggetto Example."""
        return Example(
            example_id=int(self.example_id), # type: ignore
            value=self.value # type: ignore
        )