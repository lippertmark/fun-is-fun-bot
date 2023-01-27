from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class DbMiddleware(LifetimeControllerMiddleware):
    """
    Makes sessionmaker reachable for handlers
    """
    skip_patterns = ['error']

    def __init__(self, sm):
        super().__init__()
        self.sessionmaker = sm

    async def pre_process(self, obj, data, *args):
        # `sm` is a name of var passed to handler
        data["sm"] = self.sessionmaker
