class Example:
    def __init__(self, example_id : int, value : str = "Esempio"):
        self._example_id = example_id
        self._value = value

    # proprietà read-only
    @property
    def example_id(self):
        return self._example_id

    @property
    def value(self):
        return self._value