from aiogram.dispatcher.storage import BaseStorage
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker
from ast import literal_eval
from db.models import *
import typing


class Storage(BaseStorage):
    """
    Implementation of base storage for FSM.
    Used to keep info in local db.
    """
    def __init__(self, users_type: str, session_maker: sessionmaker):
        """
        Creates Storage.

        :param users_type:
        :param session_maker:
        """
        # determines which schemas will be used for storage
        if users_type == "client":
            self._user_class = UserClient
            self._states = AiogramStateClients
            self._data = AiogramDataClients
        elif users_type == "admin":
            self._user_class = UserAdmin
            self._states = AiogramStateAdmins
            self._data = AiogramDataAdmins
        else:
            raise ValueError("wrong user type")

        self._session_maker = session_maker

    async def get_state(self, *,
                        chat: typing.Union[str, int, None] = None,
                        user: typing.Union[str, int, None] = None,
                        default: typing.Optional[str] = None) -> typing.Optional[str]:
        """
        Get current state of user in chat. Return `default` if no record is found.

        :param chat:
        :param user:
        :param default:
        :return:
        """
        chat, user = self.check_address(chat=chat, user=user)

        async with self._session_maker() as session:
            async with session.begin():
                user_state = await session.execute(select(self._states.state).where(self._states.user_id == user))
                user_state = user_state.one_or_none()

        if not user_state or not user_state.state:
            return default
        else:
            return user_state.state

    async def get_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       default: typing.Optional[typing.Dict] = None) -> typing.Dict:
        """
        Get state-data for user in chat. Return `default` if no data is provided in storage.

        :param chat:
        :param user:
        :param default:
        :return:
        """
        chat, user = self.check_address(chat=chat, user=user)

        async with self._session_maker() as session:
            async with session.begin():
                user_data = await session.execute(select(self._data.data).where(self._data.user_id == user))
                user_data = user_data.one_or_none()

        if not user_data or not user_data.data:
            return default
        else:
            return literal_eval(user_data.data)

    async def set_state(self, *,
                        chat: typing.Union[str, int, None] = None,
                        user: typing.Union[str, int, None] = None,
                        state: typing.Optional[typing.AnyStr] = None):
        """
        Set new state for user in chat.

        :param chat:
        :param user:
        :param state:
        """
        chat, user = self.check_address(chat=chat, user=user)

        user_state = await self.get_state(chat=chat, user=user, default=None)
        if state is None:
            query = delete(self._states).where(self._states.user_id == user)
        elif user_state is None:
            query = insert(self._states).values(user_id=user, state=state)
        else:
            query = update(self._states).where(self._states.user_id == user).values(state=state)

        async with self._session_maker() as session:
            async with session.begin():
                await session.execute(query)

    async def set_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       data: typing.Dict = None):
        """
        Set data for user in chat.

        :param chat:
        :param user:
        :param data:
        """
        chat, user = self.check_address(chat=chat, user=user)

        user_data = await self.get_data(chat=chat, user=user, default=None)
        if data is None:
            query = delete(self._data).where(self._data.user_id == user)
        elif user_data is None:
            query = insert(self._data).values(user_id=user, data=str(data))
        else:
            query = update(self._data).where(self._data.user_id == user).values(data=str(data))

        async with self._session_maker() as session:
            async with session.begin():
                await session.execute(query)

    async def update_data(self, *,
                          chat: typing.Union[str, int, None] = None,
                          user: typing.Union[str, int, None] = None,
                          data: typing.Dict = None,
                          **kwargs):
        """
        Update data for user in chat
        You can use data parameter or|and kwargs.

        :param data:
        :param chat:
        :param user:
        :param kwargs:
        :return:
        """
        chat, user = self.check_address(chat=chat, user=user)

        if data is None:
            data = {}

        current_data = await self.get_data(chat=chat, user=user, default={})

        current_data.update(data, **kwargs)
        await self.set_data(chat=chat, user=user, data=current_data)

    async def close(self):
        """
        Called when application shutdowns to save data. IS NOT USED

        :return: None
        """
        # TODO: probably should close connections here!
        pass

    async def wait_closed(self):
        """
        For asynchronous storages. IS NOT USED

        :return:
        """
        return True

    # next ones are not used anywhere (and are not implemented)
    async def get_bucket(self, *, chat: typing.Union[str, int, None] = None, user: typing.Union[str, int, None] = None,
                         default: typing.Optional[dict] = None) -> typing.Dict:
        pass

    async def set_bucket(self, *, chat: typing.Union[str, int, None] = None, user: typing.Union[str, int, None] = None,
                         bucket: typing.Dict = None):
        pass

    async def update_bucket(self, *, chat: typing.Union[str, int, None] = None,
                            user: typing.Union[str, int, None] = None, bucket: typing.Dict = None, **kwargs):
        pass
