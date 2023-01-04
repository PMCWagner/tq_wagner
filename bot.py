from pyrogram.errors import FloodWait, SlowmodeWait, ChatWriteForbidden
from pyrogram import Client, filters, enums
import random
import asyncio
import time
import cfg


chance = list(range(cfg.chance))
app = Client("alice", cfg.api_id, cfg.api_hash)
ignorechats = {}
f = open("words.txt", encoding="utf-8", errors="ignore")
data = f.read()
f.close()
my_id = cfg.my_id
msgs = [ms for ms in data.split("\n") if ms]
ignoreusers = cfg.ignoreusers
chats = cfg.chats

@app.on_message(filters.all)
async def hello(client, message):
    try:
        bot = message.from_user.is_bot
    except:
        bot = False
    time_now = int(time.time())
    chat_id = message.chat.id
    try:
        ignorechats[chat_id]
    except KeyError:
        ignorechats[chat_id] = 0
    ch = random.choice(chance)
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            rep_id = message.reply_to_message.from_user.id
            if rep_id == my_id:
                ch = 1
    if ch == 1 and not bot and message.from_user.id not in ignoreusers and message.from_user.id > 0 and chat_id not in chats:
        if ignorechats[chat_id] < time_now:
            try:
                await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
                await asyncio.sleep(random.randint(3, 5))
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
            except ChatWriteForbidden as e:
                print(e)
                ignorechats[chat_id] = time_now+3600


app.run()
