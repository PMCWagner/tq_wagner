from pyrogram.errors import FloodWait, SlowmodeWait
from pyrogram import Client, filters, enums
import random
import asyncio
import time


phone = "alice"
api_id = 25983686
api_hash = "d49ffa3e2b617c66250b7f4c169d1cb9"
chance = 2 #шанс ответа
chance = list(range(chance))
app = Client(phone, api_id, api_hash)
ignorechats = {}
f = open("words.txt", encoding="utf-8", errors="ignore")
data = f.read()
f.close()
msgs = [ms for ms in data.split("\n") if ms]
ignoreusers = [] #игнор пользователей (айдишники через запятую вставлять внутри квадратных скобок)
chats = [] #игнор чатов (айдишники через запятую вставлять внутри квадратных скобок)


@app.on_message(filters.all)
async def hello(client, message):
    try:
        bot = message.from_user.is_bot
    except:
        bot = False
    time_now = int(time.time())
    chat_id = message.chat.id
    try:
        print("Айди пользователя:", message.from_user.id)
    except:
        print("Айди пользователя:", message.sender_chat.id)
    print("Айди чата:", chat_id)
    try:
        ignorechats[chat_id]
    except KeyError:
        ignorechats[chat_id] = 0
    ch = random.choice(chance)
    my_id = await app.get_me()
    ignoreusers.append(my_id.id)
    if ch == 1 and not bot and message.from_user.id not in ignoreusers and message.from_user.id > 0 and chat_id not in chats:
        if ignorechats[chat_id] < time_now:
            try:
                await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
                await asyncio.sleep(random.randint(1, 3))
                msg = random.choice(msgs)
                msg_id = message.id
                await app.send_message(chat_id, msg, reply_to_message_id=msg_id)
                await app.read_chat_history(chat_id)
            except SlowmodeWait as e:
                print(e)
                ignorechats[chat_id] = time_now+e.value
            except FloodWait as e:
                print(e)
                ignorechats[chat_id] = time_now+e.value


app.run()
