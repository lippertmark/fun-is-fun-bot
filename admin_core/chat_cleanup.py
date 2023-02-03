from aiogram.dispatcher import FSMContext
from aiogram.bot import bot


async def clear_block(chat_id: int, state: FSMContext, bot: bot):
    """
    Deletes messages from one block of i/o.
    Trace of messages is stored in user data as a sequence of lists-blocks, each block represent line of i/o.

    :param chat_id: from which chat message should be deleted
    :param state:
    :param bot: to access delete message method
    :return:
    """
    user_data = await state.get_data()
    messages = user_data.get('io_trace')

    if not messages:
        return

    last_block = messages.pop(-1)
    for message_id in last_block:
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception:
            pass

    await state.update_data(io_trace=messages)


async def clear_io(chat_id: int, state: FSMContext, bot: bot):
    """
    Deletes all messages of i/o.
    Trace of messages is stored in user data as a sequence of lists-blocks, each block represent line of i/o.

    :param chat_id: from which chat message should be deleted
    :param state:
    :param bot: to access delete message method
    :return:
    """
    user_data = await state.get_data()
    messages = user_data.get('io_trace')

    if not messages:
        return

    for block in messages:
        for message_id in block:
            try:
                await bot.delete_message(chat_id, message_id)
            except Exception:
                pass

    await state.update_data(io_trace=[])


async def add_trace(message_id: int, state: FSMContext):
    """
    Puts message_id into last block. If io_trace is empty, creates new one.
    Trace of messages is stored in user data as a sequence of lists-blocks, each block represent line of i/o.

    :param message_id:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    if user_data is None:
        user_data = {}
    messages = user_data.get('io_trace')

    if not messages:
        messages = [[message_id]]
    else:
        messages[-1].append(message_id)

    await state.update_data(io_trace=messages)


async def add_block_and_trace(message_id: int, state: FSMContext):
    """
    Creates new block and adds message_id there.
    Trace of messages is stored in user data as a sequence of lists-blocks, each block represent line of i/o.

    :param message_id:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    messages = user_data.get('io_trace')

    if not messages:
        messages = [[message_id]]
    else:
        messages.append([message_id])

    await state.update_data(io_trace=messages)
