from load import bot
import keybords as kb


async def swipe(code, callback_query, page, list_, is_back):
    """
    :param code: info about swipe forward or backward
    :param callback_query: to update InlineKeyboard
    :param page: page number
    :param list_: list
    :param is_back: add 'back' keyboard
    :return: new page number (+1 or -1)
    """
    if (len(list_) - page * 10) > 10 and code == '>' or page > 0 and code == '<':
        page = page + 1 if code == '>' else page - 1
        await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=kb.swipe(list_, page, is_back=is_back))
    return page


def is_swipeable(code, page, length):
    return code == '<' and page > 0 or code == '>' and (length - page * 10) > 10


def get_subs_info(sub_list):
    result = ""
    for sub in sub_list:
        result = result + str(sub['subscription_type']) + f' включает в себя:\n'
        for k in sub["includes"]:
            result = result + f'- {k}\n'
        result = result + f'\n Стоимость: {sub["price"]}\n\n'
    return result


async def delete_last_message(state):
    async with state.proxy() as data:
        await data['msg'][len(data['msg']) - 1].delete()
