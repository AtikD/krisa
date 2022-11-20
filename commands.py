from config import dp, db, bot, ofcrs, notes, notes_db, app, tagall

from aiogram import types
from aiogram.utils.exceptions import BadRequest, BotKicked

@dp.message_handler(lambda m: m.from_user.id == m.chat.id and m.from_user.id in notes) # Ждет сообщение для заметки
async def cmd_wait_for_note(message: types.Message):
    user = notes_db.get(str(message.from_user.id))
    if not user:
        notes_db.set(str(message.from_user.id),{'1':message.text})
        await message.reply(f"Готово! \nНомер заметки: <code>1</code>\n")
    else:
        user.update({str(len(user) + 1): message.text}) 
        notes_db.set(str(message.from_user.id), user)
        await message.reply(f"Готово! \nНомер заметки: <code>{len(user)}</code>")    
    notes.remove(message.from_user.id)

@dp.message_handler(commands=["start"]) # Приветствие и еще добавление в группу
async def cmd_start(message: types.Message):
    if message.chat.id == message.from_user.id:
        await message.answer("Привет! Команды:\n <code>/group</code> - Добавить бота в группу\n<code>/groups</code> - Список ваших групп\n<code>/note</code> - Добавить заметки\n<code>/notes</code> - Список ваших заметок\n<code>/removenote</code> - Удалить заметку\n<code>/removegroup</code> - Удалить группу\nДля отправки сообщения пишем: '{номер_группы} {ваше текст}'\nНапример: <code>1 Всем привет! это сообщение будет закреплено!</code>\n\nКак использовать заметки: '{номер_группы} {ваш текст, !номер_заметки}', перед номером заметки ставим восклицательный знак.\nНапример: <code>1 !1 Перед словом 'перед' была заметка под номером 1!</code>")
        return
    if message.from_user.id in ofcrs:
        is_admin = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if is_admin.is_chat_admin() is False and is_admin.is_chat_creator() is False and is_admin.is_chat_owner() is False:
            await bot.send_message(message.from_user.id,"Ты не админ в этой группе!")
            return  
        user = db.get(str(message.from_user.id))      
        if not user:
            db.set(str(message.from_user.id),{"1":{"id": message.chat.id, "title": message.chat.title}})
            await bot.send_message(message.from_user.id, f"Готово! \nНомер группы: <code>1</code>\nНазвание группы: <code>{message.chat.title}</code>")
        else:
            user.update({str(len(user)+1):{"id": message.chat.id, "title": message.chat.title}})
            db.set(str(message.from_user.id), user)
            await bot.send_message(message.from_user.id, f"Готово! \nНомер группы: <code>{len(user)}</code>\nНазвание группы: <code>{message.chat.title}</code>")
        await message.reply("Дайте мне права удалять сообщения и закреплять их, и я буду готов к выполнению поручений!")
        ofcrs.remove(message.from_user.id)

@dp.message_handler(lambda m: m.from_user.id == m.chat.id,commands=["group"])# Старт процесса добавления в группу
async def cmd_addgroup(message: types.Message):
    username = await bot.get_me()
    button = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text = "Добавить в группу!", url = f'tg://resolve?domain={username.username}&startgroup=trues'))
    await message.answer("Добавь меня в группу!",reply_markup = button)
    ofcrs.append(message.from_user.id)

@dp.message_handler(lambda m: m.from_user.id == m.chat.id,commands=["removegroup"])# Удалить группу
async def cmd_removegroup(message: types.Message):
    user = db.get(str(message.from_user.id))
    if not user:
        await message.answer("[Error] У Вас нет добавленных групп!")
        return
    num = message.text.split(' ')[1]
    try:
        user[num] = False
    except KeyError:
        await message.answer("[Error] Такого кода нет в Вашем списке!")
        return
    db.set(str(message.from_user.id), user)
    await message.answer("Успешно удалил!")

@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=["reload"])# Перезагрузка списков групп и заметок
async def cmd_reload(message: types.Message):
    old_notes, old_chats = notes_db.get(str(message.from_user.id)), db.get(str(message.from_user.id))
    new_notes, new_chats = {}, {}
    for i in old_notes:
        if old_notes[i] is not False:
            new_notes.update({str(len(new_notes)+1): old_notes[i]})
    for i in old_chats:
        if old_chats[i] is not False:
            new_chats.update({str(len(new_chats)+1): old_chats[i]})
    notes_db.set(str(message.from_user.id), new_notes)
    db.set(str(message.from_user.id), new_chats)
    await message.answer('done')
            

@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=["notes"])# Список заметок
async def cmd_notelits(message: types.Message):
    user = notes_db.get(str(message.from_user.id))
    text = "Ваши заметки: \n\n"
    if user:
        for i in user:
            if user[i]:
                text += F"{i} - {user[i]}\n"
    await message.reply(text)

@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=["note"])# Создать заметку
async def cmd_addnote(message: types.Message):
    await message.answer("Отправьте сообщение для сохранения его в заметках!")
    notes.append(message.from_user.id)

@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=["removenote"])# Удалить заметку
async def cmd_removenote(message: types.Message):
    user = notes_db.get(str(message.from_user.id))
    if not user:
        await message.answer("[Error] У Вас нет заметок!")
        return
    num = message.text.split(' ')[1]
    try:
        user[num] = False
    except KeyError:
        await message.answer("[Error] Такой заметки не существует!")
        return
    notes_db.set(str(message.from_user.id), user)
    await message.answer("Успешно удалил!")

@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=["groups"])# Список груп
async def cmd_grouplist(message: types.Message):
    user = db.get(str(message.from_user.id))
    text = 'Ваши группы: \n\n'
    if user:  
        for i in user:
            if user[i]:
                text += f"{i} - {user[i]['title']}\n"
    await message.answer(text)

@dp.message_handler(lambda m: m.from_user.id == m.chat.id and m.text.split()[0].isdigit())# Процесс передачи сообщения в чаты
async def cmd_rass(message: types.Message):
    msg1 = message.text.split(' ', maxsplit = 1)
    if len(msg1) < 2:
        return
    user = db.get(str(message.from_user.id))
    if msg1[0] not in user or not user[msg1[0]] :
        return
    text = msg1[1]
    note = notes_db.get(str(message.from_user.id))
    if note:
        for i in text.split(' '):
            if i.startswith("!"):
                try:
                    text = text.replace(i,note[i[1:]])
                except KeyError:
                    pass
                except TypeError:
                    pass
                except Exception as ex:
                  await message.reply(str(ex))
                  await message.answer("[Error] Отправьте это @atikdd пожалуйста!")
                  return
    try:
        msg = await app.send_message(user[msg1[0]]['id'], text)
        await msg.pin()
    except BotKicked:
        await message.reply("[Report] Меня нет в чате!")
        return
    except BadRequest:
        await message.reply(f"[Report] У меня нет прав закреплять сообщения, но отправить я смог!\n<a href='{msg.link}'>Клик!</a>")
        return
    except Exception as ex:
        await message.reply(str(ex))
        await message.answer("[Error] Отправьте это @atikdd пожалуйста!")
        return
    users = [
            str(member.user.id)
            async for member in app.get_chat_members(msg.chat.id)
            if not (member.user.is_bot or member.user.is_deleted)
        ]
    tagall.update({str(user[msg1[0]]['id']): users})
    button = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text = "TagAll!", callback_data = f"{user[msg1[0]]['id']}"))
    await message.reply(f"Операция выполнена успешно!\n<a href='{msg.link}'>Клик!</a>",reply_markup = button)

@dp.callback_query_handler() # TAGALL
async def cmd_tagall(call: types.CallbackQuery):
    if call.data not in tagall:
        await call.message.edit_reply_markup()
        return await call.answer("НЕТ ТЕГАЛА!")
    users = [f"<a href=\"tg://user?id={i}\">\u2060</a>" for i in tagall[call.data]]
    for output in [
            users[i: i + 5]
            for i in range(0, len(users), 5)
        ]:
            await bot.send_message(call.data,"[TagAll] Действуем!" + "\u2060".join(output))    
    await call.message.edit_text(call.message.html_text + "\nУспешно всех тегнул!")