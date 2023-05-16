from pyrogram.errors import FloodWait, SlowmodeWait, ChatWriteForbidden, UserBannedInChannel, ReactionInvalid, Forbidden
from pyrogram.raw.functions.messages import CheckChatInvite
from pyrogram import Client, filters, enums
import asyncio
import random
import time
import cfg


chance = list(range(1, cfg.chance+1))
app = Client(
    name="alice",
    api_id=cfg.api_id,
    api_hash=cfg.api_hash
)

def print_message(usr_id, usrname, frst_name, m, chat_id, msg_id):
    print("*"*50)
    s_chat = str(chat_id).replace('-', '').replace('100', '')
    ms_lnk = f"https://t.me/c/{s_chat}/{msg_id}"
    print("Ответ в сообщениях")
    print(f"От кого: [{usr_id}]({usrname}){frst_name}")
    print(f"Сообщение: {m}\n{ms_lnk}")


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
    msg_id = message.id
    user = message.from_user
    try:
        bot = message.from_user.is_bot
    except:
        bot = False
    if user and not bot:
        time_now = int(time.time())
        u_id = user.id
        first_name = user.first_name
        username = user.username
        chat_id = message.chat.id
        msg = message.text
        try:
            ignorechats[chat_id]
        except KeyError:
            ignorechats[chat_id] = 0
        ch = random.choice(chance)
        is_link = False
        if chat_id > 0:
            try:
                open_link = False
                lnk = ""
                if msg[:1] == '@':
                    lnk = msg[1:]
                    open_link = True
                    is_link = True

                elif msg[:13] == 'https://t.me/':
                    if msg[13:14] != '+' and msg[13:21] != 'joinchat':
                        lnk = msg[13:]
                        open_link = True
                        is_link = True

                if msg[13:14] == '+':
                    lnk = msg[14:]
                    is_link = True

                if msg[13:21] == 'joinchat':
                    lnk = msg[22:]
                    is_link = True
                if is_link:
                    link = msg
                    if open_link:
                        s = await app.get_chat(lnk)
                        if enums.ChatType.CHANNEL == s.type:
                            is_channel = True
                        else:
                            is_channel = False
                    else:
                        s = await app.invoke(CheckChatInvite(hash=lnk))
                        is_channel = s.channel

                    if not open_link:
                        lnk = link

                    if is_channel:
                        if not open_link:
                            await app.join_chat(lnk)
                        c = await app.get_chat(lnk)
                        await app.join_chat(c.linked_chat.id)

                    else:
                        await app.join_chat(lnk)
            except:
                pass
            print_message(u_id, username, first_name, msg, chat_id, msg_id)
        isreply = False
        if message.reply_to_message:
            if message.reply_to_message.from_user:
                rep_id = message.reply_to_message.from_user.id
                if rep_id == my_id:
                    isreply = True
                    ch = 1
                    if chat_id < 0:
                        print_message(u_id, username, first_name, msg, chat_id, msg_id)
        if not cfg.send_pm:
            if chat_id > 0:
                ch = 0
        if ch == 1 and not isreply and cfg.answer_only_on_replies:
            ch = 0
        if ch == 1 and u_id not in ignoreusers and chat_id not in chats:
            await app.read_chat_history(chat_id)
            if ignorechats[chat_id] < time_now:
                try:
                    await app.send_chat_action(chat_id, enums.ChatAction.TYPING)
                    await asyncio.sleep(random.randint(3, 5))
                    msg = random.choice(msgs)
                    if cfg.reply_only == 1:
                        await app.send_message(chat_id, msg, reply_to_message_id=msg_id)
                    elif cfg.reply_only == 2:
                        reply = random.choice([True, False])
                        if reply:
                            await app.send_message(chat_id, msg, reply_to_message_id=msg_id)
                        else:
                            await app.send_message(chat_id, msg)
                    elif cfg.reply_only == 0:
                        await app.send_message(chat_id, msg)
                except SlowmodeWait as e:
                    print(e)
                    ignorechats[chat_id] = time_now+e.value+2
                except FloodWait as e:
                    print(e)
                    ignorechats[chat_id] = time_now+e.value+2
                except ChatWriteForbidden:
                    if not cfg.chat_leave:
                        try:
                            await app.send_reaction(chat_id, msg_id, random.choice(cfg.reactions))
                        except FloodWait as e:
                            ignorechats[chat_id] = time_now+e.value+30
                        except:
                            pass
                    else:
                        try:
                            await app.leave_chat(chat_id)
                        except UserNotParticipant:
                            ignorechats[chat_id] = time_now+99999999
                except UserBannedInChannel:
                    try:
                        await app.send_reaction(chat_id, msg_id, random.choice(cfg.reactions))
                    except FloodWait as e:
                        print(e)
                        ignorechats[chat_id] = time_now+e.value+30
                    except Exception as e:
                        print(e)
                except Forbidden:
                    if not cfg.chat_leave:
                        try:
                            await app.send_reaction(chat_id, msg_id, random.choice(cfg.reactions))
                        except FloodWait as e:
                            ignorechats[chat_id] = time_now+e.value+30
                        except:
                            pass
                    else:
                        try:
                            print(1)
                            await app.leave_chat(chat_id)
                        except UserNotParticipant:
                            ignorechats[chat_id] = time_now+99999999

app.run()
