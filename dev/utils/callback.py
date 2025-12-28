from telegram import User, Chat

class Callback:
    def __init__(self, async_func=None, bot=None, **kwargs):
        self.func = async_func
        self._bot = bot          # <-- bot non va serializzato

        # Trasforma automaticamente User/Chat in dict serializzabili
        for k, v in kwargs.items():
            if isinstance(v, User):
                kwargs[k] = {key: getattr(v, key, None) for key in ["id", "first_name", "last_name", "username", "is_bot"]}
            elif isinstance(v, Chat):
                kwargs[k] = {key: getattr(v, key, None) for key in ["id", "type", "title", "username"]}
        self.__dict__.update(kwargs)


    async def __call__(self):
        #print("Callback __call__:", self.func, self.__dict__)
        if self.func:
            if self._bot:
                await self.func(bot=self._bot, **self.__dict__)
            else:
                await self.func(**self.__dict__)

    def set_bot(self, bot):
        self._bot = bot
