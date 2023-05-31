from pyrogram.errors import FloodWait, SlowmodeWait, ChatWriteForbidden
from pyrogram.raw.functions.messages import CheckChatInvite
from pyrogram import Client, filters, enums
from importlib import reload
import asyncio
import random
import time
import cfg


chance = list(range(1, cfg.chance+1))
app = Client(name="alice", api_id=cfg.api_id, api_hash=cfg.api_hash)

def print_message(usr_id, usrname, frst_name, m, chat_id, msg_id):
    print("*"*50)
    s_chat = str(chat_id).replace('-', '').replace('100', '')
    ms_lnk = f"https://t.me/c/{s_chat}/{msg_id}"
    print("Ответ в сообщениях")
    print(f"От кого: [{usr_id}]({usrname}){frst_name}")
    print(f"Сообщение: {m}\n{ms_lnk}")


ignorechats = {}
msgs = [ms for ms in open("words.txt", encoding="utf-8", errors="ignore").read().split("\n") if ms]


async def chat_join(client, msg):
    open_link = False
    is_channel = False
    is_link = False
    if msg[:13] == 'https://t.me/':
        if msg.find('+') == -1:
            msg = msg[13:]
            open_link = True
        is_link = True
    if is_link:
        if open_link:
            s = await client.get_chat(msg)
            if enums.ChatType.CHANNEL == s.type:
                is_channel = True
        else:
            s = await client.invoke(CheckChatInvite(hash=msg[14:]))
            is_channel = s.channel

        if is_channel:
            if not open_link:
                f = await client.join_chat(msg)
                g_chat_data = f.id
            else:
                g_chat_data = msg
            c = await client.get_chat(g_chat_data)
            await client.join_chat(c.linked_chat.id)
        else:
            await client.join_chat(msg)


@app.on_message(filters.all)
async def hello(client, message):
    reload(cfg)
    msg_id = message.id
    user = message.from_user
    chat_id = message.chat.id
    try:
        ignorechats[chat_id]
    except KeyError:
        ignorechats[chat_id] = 0
    try:
        bot = message.from_user.is_bot
    except:
        bot = False
    if user and not bot and not message.outgoing:
        ch = random.choice(chance)
        time_now = int(time.time())
        u_id = user.id
        first_name = user.first_name
        username = user.username
        is_link = False
        if chat_id > 0:
            if not cfg.send_pm:
                ch = 0
            if message.text:
                await chat_join(client, message.text)
            print_message(u_id, username, first_name, message.text, chat_id, msg_id)
        if message.mentioned:
            ch = 1
            print_message(u_id, username, first_name, message.text, chat_id, msg_id)
        if ch == 1 and u_id not in cfg.ignoreusers and chat_id not in cfg.ignorechats and ignorechats[chat_id] < time_now:
            ignorechats[chat_id] = time_now
            try:
                await client.read_chat_history(chat_id)
                await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
                await asyncio.sleep(random.randint(3, 5))
                msg = random.choice(msgs)
                await client.send_message(chat_id, msg, reply_to_message_id=msg_id)
            except ChatWriteForbidden:
                if not cfg.chat_leave:
                    await client.send_reaction(chat_id, msg_id, random.choice(cfg.reactions))
                else:
                    await client.leave_chat(chat_id)
            except SlowmodeWait as e:
                print(e)
                ignorechats[chat_id] += e.value+2
            except FloodWait as e:
                print(e)
                ignorechats[chat_id] += e.value+2
            except:
                ignorechats[chat_id] += 300

app.run()
