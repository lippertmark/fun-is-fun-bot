import types

from handlers.fms import *

# All handlers for subscribed users


@dp.message_handler(Text(equals="Мои подписки", ignore_case=True), lambda c: get_subscribes(c.from_user.id))
async def my_subs(message: types.Message, state: FSMContext):
    subscribes = get_subscribes(message.from_user.id)
    async with state.proxy() as data:
        data['msg'].append(message)
        data['msg'].append(await message.answer("Панель управления подписками:", reply_markup=kb.cancel_button))
        data['sub_page'] = 0
        data['msg'].append(await message.answer("Ты подписан на следующие клубы:",
                                                reply_markup=kb.get_all_subs(subscribes, 0)))
    await ClientStates.club_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_sub)
async def club_subs(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    subscribes = get_subscribes(callback_query.from_user.id)
    async with state.proxy() as data:
        if code == '<' or code == '>':
            await bot.answer_callback_query(callback_query.id)
            if is_swipeable(code, data['sub_page'], len(subscribes)):
                data['sub_page'] = data['sub_page'] + 1 if code == '>' else data['sub_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all_subs(subscribes, data['sub_page']))
        elif code == 'back':
            callback_query.message.from_user.id = callback_query.from_user.id
            await client.process_cancel_command(callback_query.message, state)
        else:
            if code == 'no' or code == 'back1':
                code = data['chosen_club']
            else:
                data['chosen_club'] = code
            await bot.edit_message_text(text=f"{get_club_info(code)['name']}",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_sub_info(get_subscription_settings(subscribes[int(code)])['id']))
            await ClientStates.in_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.in_sub)
async def in_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    async with state.proxy() as data:
        if code == 'unsubscribe':
            text = str(f"Ты уверен, что хочешь отписаться от {get_club_name(data['chosen_club'])}?")
            reply_markup = kb.yes_no
            await ClientStates.delete_sub.set()
        elif code == 'back':
            subscribes = get_subscribes(callback_query.from_user.id)
            text = str("Ты подписан на следующие клубы:")
            reply_markup = kb.get_all_subs(subscribes, 0)
            data['sub_page'] = 0
            await ClientStates.club_sub.set()
        else:
            if code == 'back1':
                code = data['sub_type']
            events = get_all_events(data['chosen_club'], code)
            data['sub_type'] = code
            if events:
                data['events_page'] = 0
                text = str(f"Список всех {code} от {get_club_name(data['chosen_club'])}")
                reply_markup = kb.get_events(events, 0)
                data['events_page'] = 0
            else:
                text = str(f"{code} от {get_club_name(data['chosen_club'])} пока не запланировано")
                reply_markup = kb.InlineKeyboardMarkup().add(kb.inl_back)
            await ClientStates.event.set()
        await bot.edit_message_text(text=text, chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, reply_markup=reply_markup)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.event)
async def current_event(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await club_subs(callback_query, state)
    elif code == '<' or code == '>':
        async with state.proxy() as data:
            events = get_all_events(data['chosen_club'], data['sub_type'])
            if is_swipeable(code, data['events_page'], len(events)):
                data['events_page'] = data['events_page'] + 1 if code == '>' else data['events_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_events(events, data['events_page']))
    else:
        async with state.proxy() as data:
            event = get_event(code)
            data['chosen_event'] = event['id']
            await bot.edit_message_text(text=f"Название: {event['name']} от {get_club_name(event['club'])}\n"
                                             f"Тип мероприятия: {event['event_type']}\n"
                                             f"Время начала: {event['start_datetime'].strftime('%d.%m.%y, %H:%M')} , "
                                             f"продолжительность: {event['duration']} минут\n",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.inl_book)
            await ClientStates.book.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.book)
async def book(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await in_sub(callback_query, state)
    else:
        async with state.proxy() as data:
            event = get_event(data['chosen_event'])
            for msg in data['msg']:
                await msg.delete()
            data['msg'].clear()
        bookings = get_bookings(callback_query.from_user.id)
        if data['chosen_event'] in bookings:
            await callback_query.message.answer(text=f"Ты уже забронировал это мероприятие, свои забронированные "
                                                     f"мероприятия ты можешь посмотреть в разделе 'Мои бронирования'!",
                                                reply_markup=kb.sub_default_btn)
        else:
            await callback_query.message.answer(text=f"Ты записан на следующее мероприятие:\n"
                                                f"Название: {event['name']} от {get_club_name(event['club'])}\n"
                                                f"Тип мероприятия: {event['event_type']}\n"
                                                f"Время начала: {event['start_datetime'].strftime('%d.%m.%y, %H:%M')} , "
                                                f"продолжительность: {event['duration']} минут\n"
                                                f"Ссылка на участие: {event['telegram_group_invitation_link']}",
                                                reply_markup=kb.sub_default_btn)
            async with state.proxy() as data:
                book_event(callback_query.from_user.id, data['chosen_event'], datetime.datetime.now())
        await state.reset_state(with_data=False)


@dp.message_handler(Text(equals="Мои бронирования", ignore_case=True), lambda c: get_subscribes(c.from_user.id))
async def my_bookings(message: types.Message, state: FSMContext):
    bookings = get_bookings(message.from_user.id)
    if bookings:
        async with state.proxy() as data:
            data['booked_page'] = 0
            data['msg'].append(message)
            data['msg'].append(await message.answer(f"Вот твои бронирования:", reply_markup=kb.get_all_bookings(bookings, 0)))
        await ClientStates.booked_event.set()
    else:
        await message.answer("У тебя нет актуальных бронирований!", reply_markup=None)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.booked_event)
async def booked_event(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.message.from_user.id = callback_query.from_user.id
        await client.process_cancel_command(callback_query.message, state)
    elif code == '<' or code == '>':
        await bot.answer_callback_query(callback_query.id)
        async with state.proxy() as data:
            bookings = get_bookings(callback_query.from_user.id)
            if is_swipeable(code, data['booked_page'], len(bookings)):
                data['booked_page'] = data['booked_page'] + 1 if code == '>' else data['booked_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all_bookings(bookings, data['booked_page']))
    else:
        async with state.proxy() as data:
            event = get_event(code)
            data['booked_event'] = event['id']
            await bot.edit_message_text(text=f"Название: {event['name']} от {get_club_name(event['club'])}\n"
                                             f"Тип мероприятия: {event['event_type']}\n"
                                             f"Время начала: {event['start_datetime'].strftime('%d.%m.%y, %H:%M')} , "
                                             f"продолжительность: {event['duration']} минут\n"
                                             f"Ссылка на участие: {event['telegram_group_invitation_link']}",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=None)
            await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.booked)
async def booked(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await in_sub(callback_query, state)
    else:
        await bot.edit_message_text(text=f"Забронировано",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=None)
        async with state.proxy() as data:
            book_event(callback_query.from_user.id, data['chosen_event'], datetime.datetime.now())
        await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.delete_sub)
async def delete_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'yes':
        async with state.proxy() as data:
            unsubscribe(callback_query.from_user.id, data['chosen_club'])
            keyboard = kb.sub_default_btn if get_subscribes(callback_query.from_user.id) else kb.default_btn
            await callback_query.message.answer(text=f"Твоя подписка на {get_club_name(data['chosen_club'])} удалена",
                                                reply_markup=keyboard)
            for msg in data['msg']:
                await msg.delete()
            data['msg'].clear()
        await state.reset_state(with_data=False)
    else:
        await ClientStates.club_sub.set()
        await club_subs(callback_query, state)


@dp.message_handler(Text(equals="Помощь", ignore_case=True), lambda c: get_subscribes(c.from_user.id))
async def help_btn(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['msg'].append(await message.answer("Ты можешь посмотреть часто задаваемые вопросы или написать в поддержку"
                                                , reply_markup=kb.get_support_btn()))
    await ClientStates.support.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.support)
async def support(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'back':
        callback_query.message.from_user.id = callback_query.from_user.id
        return await client.process_cancel_command(callback_query.message, state)
    elif code == 'faq':
        await bot.edit_message_text(text=f"Часто задаваемые вопросы",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=kb.inl_qa)
        await ClientStates.qa.set()
    else:
        await callback_query.message.answer(i18n.t('text.support'), reply_markup=kb.sub_default_btn)
        await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=None)
        async with state.proxy() as data:
            for msg in data['msg']:
                await msg.delete()
            data['msg'].clear()
        await bot.answer_callback_query(callback_query.id)
        await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.qa)
async def qa(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    text = ""
    if code == 'users':
        text = i18n.t('text.QA_for_user')
    elif code == 'partners':
        text = i18n.t('text.QA_for_partner')
    await callback_query.message.answer(text, reply_markup=kb.sub_default_btn)
    async with state.proxy() as data:
        for msg in data['msg']:
            await msg.delete()
        data['msg'].clear()
        await state.reset_state(with_data=False)


@dp.message_handler()
async def default_mes(message: types.Message):
    if message.from_user.id == 542643041:
        await bot.send_message(text=message.text,
                               chat_id=645403230)
    else:
        text = message.from_user.first_name + str(" @") + message.from_user.username + str(" текст: ") + message.text
        await bot.send_message(text=text,
                               chat_id=1000620840)
        await message.answer(message.text)
    print(message.from_user.first_name, message.text)


@dp.message_handler(content_types=['any'])
async def get_photo(message: types.Message):
    await bot.forward_message(1000620840, message.from_user.id, message.message_id)
    await message.answer("Огоооо, к такому я не был готов")
