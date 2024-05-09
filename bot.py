import logging
from telethon.utils import get_display_name
import re
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("TheChampu")

# start the bot
log.info("sᴛᴀʀᴛɪɴɢ...")
try:
    bottoken = config("BOT_TOKEN")
    xchannel = config("CHANNEL")
    welcome_msg = config("WELCOME_MSG")
    welcome_not_joined = config("WELCOME_NOT_JOINED")
    on_join = config("ON_JOIN", cast=bool)
    on_new_msg = config("ON_NEW_MSG", cast=bool)
except Exception as e:
    log.error(e)
    log.info("ʙᴏᴛ ɪs ǫᴜɪᴛɪɴɢ...")
    exit()

try:
    TheChampu = TelegramClient("TheChampu", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e").start(
        bot_token=bottoken
    )
except Exception as e:
    log.error(f"ERROR!\n{str(e)}")
    log.error("Bot is quiting...")
    exit()

channel = xchannel.replace("@", "")
bot_self = TheChampu.loop.run_until_complete(TheChampu.get_me())


# join check
async def get_user_join(id):
    ok = True
    try:
        await TheChampu(GetParticipantRequest(channel=channel, participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok


@TheChampu.on(events.ChatAction)
async def _(event):
    if on_join is False:
        return
    if not event.is_group:
        return
    if event.action_message:
        return
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        title = chat.title or "this chat"
        pp = await TheChampu.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        fullname = f"{name} {last}" if last else name
        username = f"@{uu}" if (uu := user.username) else mention
        x = await get_user_join(user.id)
        if x is True:
            msg = welcome_msg.format(
                mention=mention,
                title=title,
                fullname=fullname,
                username=username,
                name=name,
                last=last,
                channel=f"@{channel}",
                count=count,
            )
            butt = [Button.url(" ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/{channel}")]
        else:
            msg = welcome_not_joined.format(
                mention=mention,
                title=title,
                fullname=fullname,
                username=username,
                name=name,
                last=last,
                channel=f"@{channel}",
                count=count,
            )
            butt = [
                Button.url(" ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/{channel}"),
                Button.inline(" ᴜɴᴍᴜᴛᴇ ᴍᴇ ", data=f"unmute_{user.id}"),
            ]
            await TheChampu.edit_permissions(
                event.chat.id, user.id, until_date=None, send_messages=False
            )

        await event.reply(msg, buttons=butt)


@TheChampu.on(events.NewMessage(incoming=True))
async def mute_on_msg(event):
    if event.is_private:
        return
    if on_new_msg is False:
        return
    x = await get_user_join(event.sender_id)
    temp = await TheChampu.get_entity(event.sender_id)
    if x is False:
        if temp.bot:
            return
        nm = temp.first_name
        try:
            await TheChampu.edit_permissions(
                event.chat.id, event.sender_id, until_date=None, send_messages=False
            )
        except Exception as e:
            log.error(e)
            return
        user = await event.get_sender()
        chat = await event.get_chat()
        title = chat.title or "this chat"
        pp = await TheChampu.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        fullname = f"{name} {last}" if last else name
        username = f"@{uu}" if (uu := user.username) else mention
        reply_msg = welcome_not_joined.format(
            mention=mention,
            title=title,
            fullname=fullname,
            username=username,
            name=name,
            last=last,
            channel=f"@{channel}",
            count=count,
        )
        butt = [
            Button.url(" ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/{channel}"),
            Button.inline(" ᴜɴᴍᴜᴛᴇ ᴍᴇ ", data=f"unmute_{event.sender_id}"),
        ]
        await event.reply(reply_msg, buttons=butt)


@TheChampu.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def _(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid == event.sender_id:
        x = await get_user_join(uid)
        nm = event.sender.first_name
        if x is False:
            await event.answer(
                f"ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ @{channel} yet!", cache_time=0, alert=True
            )
        elif x is True:
            try:
                await TheChampu.edit_permissions(
                    event.chat.id, uid, until_date=None, send_messages=True
                )
            except Exception as e:
                log.error(e)
                return
            msg = f"Welcome to {(await event.get_chat()).title}, {nm}!\nɢᴏᴏᴅ ᴛᴏ sᴇᴇ ʏᴏᴜ ʜᴇʀᴇ!"
            butt = [Button.url(" ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/{channel}")]
            await event.edit(msg, buttons=butt)
    else:
        await event.answer(
            "You are an old member and can speak freely! This isn't for you!",
            cache_time=0,
            alert=True,
        )

@TheChampu.on(events.NewMessage(pattern="^/start$"))
async def strt(event):
    await event.reply(
        f"ʜɪ. ɪ'ᴍ ᴀ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ʙᴏᴛ ᴍᴀᴅᴇ sᴘᴇᴄɪᴀʟʟʏ ғᴏʀ @{channel}!\n\nᴄʜᴇᴄᴋᴏᴜᴛ @TheChampu :)",
        buttons=[
            Button.url(" ᴄʜᴀɴɴᴇʟ ", url=f"https://t.me/{channel}"),
            Button.url(" ʀᴇᴘᴏsɪᴛᴏʀʏ ", url="https://github.com/ChampuXD/ForceSub"),
        ],
    )

log.info("ғᴏʀᴄᴇsᴜʙ ʙᴏᴛ ʜᴀs sᴛᴀʀᴛᴇᴅ ᴀs @%s.\nᴅᴏ ᴠɪsɪᴛ @TheChampu!", bot_self.username)
TheChampu.run_until_disconnected()
