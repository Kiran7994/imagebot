# (c) CW4RR10R | @AbirHasan2005

import os
import uuid
import shutil
import logging
import asyncio
import traceback
from pyrogram import Client, filters
from core.creds import Credentials
from core.sessionname import SESSION_NAME
from core.database import Database
from telegraph import upload_file
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

## --- Logger --- ##
logging.basicConfig(level=logging.INFO)


## --- Bot --- ##
Mo_tech_yt = Client(
    SESSION_NAME,
    bot_token=Credentials.BOT_TOKEN,
    api_id=Credentials.API_ID,
    api_hash=Credentials.API_HASH,
)


## --- Sub Configs --- ##
db = Database(Credentials.MONGODB_URI, SESSION_NAME)
broadcast_ids = {}
home_text = None
if Credentials.HOME_MSG:
    home_text = Credentials.HOME_MSG
else:
    home_text = """
👋**Hello [{}](tg://user?id={})**

**I'm a simple Telegraph Uploader bot💯**

**Ican convert gif, image or video(Mp4only) into telegra.ph links**

**Click help for more details...**

**You must subscribe our channel in order to use me😇****
"""
about_text = None
if Credentials.ABOUT_MSG:
    about_text = Credentials.ABOUT_MSG
else:
    about_text = """
**🤖 Name :** **TelegrPh**

**👨‍💼 Creator : @Mo_Tech_YT**

**📣 Language :** `Python3`

**📚 Library :** [📃Pyrogram](https://docs.pyrogram.org/)

**📢 Updates :** **@Mo_Tech_YT**

**🗣️ Group :** **@Mo_Tech_Group**

**🔻 YouTube : [Subscriber Now YouTube](https://youtube.com/channel/UCmGBpXoM-OEm-FacOccVKgQ)**

**✳️ Source : [🤪Click Here](https://github.com/PR0FESS0R-99/Image-Upload)**
"""
if Credentials.HOME_MSG:
    help_text = Credentials.HELP_MSG
else:
    help_text = """
**🖐️Hey.. It's not that complicated**

**👇Follow These steps..!👇**

**🔻Send any Image, Gif or Video(Mp4 oNly) below 5MB**

**🔻Wait for the link to get generated**

**🤔Any Doubt :- @Mo_Tech_Group**
"""
async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


## --- Start Handler --- ##
@Mo_tech_yt.on_message(filters.command("start"))
async def start(client, message):
    ## --- Users Adder --- ##
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
    ## --- Force Sub --- ##
    update_channel = Credentials.UPDATES_CHANNEL
    if update_channel:
        try:
            user = await client.get_chat_member(update_channel, message.from_user.id)
            if user.status == "kicked":
               await client.send_message(
                   chat_id=message.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/Mo_Tech_Group).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🔔Join My Update Channel🔔", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/Mo_Tech_YT).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return
    await message.reply_text(
        f"<b>👋Hello {message.from_user.mention}</b>\n\n<b>I'm a simple Telegraph Uploader bot💯\n\nI can convert gif, image or video(Mp4only) into telegra.ph links\n\nYou must subscribe our YouTube Channel😇</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🗣️Group", url="https://telegram.dog/Mo_Tech_Group"),
                    InlineKeyboardButton("📃Bot List", url="https://telegram.dog/Mo_Tech_YT"),
                    InlineKeyboardButton("✳️Source", url="https://github.com/PR0FESS0R-99/Image-Upload")
                ],
                [
                    InlineKeyboardButton("🙏Help", callback_data="help"),
                    InlineKeyboardButton("👨‍💼About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )

## --- help Handler --- ##
@Mo_tech_yt.on_message(filters.command("help"))
async def help(client, message):
   await message.reply_text(
       "<b>🖐️Hey.. It's not that complicated\n\n👇Follow These steps..!👇\n\n🔻Send any Image, Gif or Video(Mp4 oNly) below 5MB\n\n🔻Wait for the link to get generated\n\n🤔Any Doubt :- @Mo_Tech_Group</b>",
       reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🗣️Group", url="https://telegram.dog/Mo_Tech_Group"),
                    InlineKeyboardButton("📃Bot List", url="https://telegram.dog/Mo_Tech_YT"),
                    InlineKeyboardButton("✳️Source", url="https://github.com/PR0FESS0R-99/Image-Upload")
                ],
                [
                    InlineKeyboardButton("🏠Home", callback_data="home"),
                    InlineKeyboardButton("👨‍💼About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )

@Mo_tech_yt.on_message(filters.private & filters.command("status") & filters.user(Credentials.ADMIN))
async def sts(bot, cmd):
    total_users = await db.total_users_count()
    await cmd.reply_text(text=f"**Total Users in DB:** `{total_users}`", parse_mode="Markdown")


@Mo_tech_yt.on_message(filters.private & filters.command("broadcast") & filters.user(Credentials.ADMIN) & filters.reply)
async def broadcast_(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text = f"Broadcast initiated! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total = total_users,
        current = done,
        failed = failed,
        success = success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id = int(user['id']),
                message = broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current = done,
                        failed = failed,
                        success = success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    await aiofiles.os.remove('broadcast.txt')


@Mo_tech_yt.on_message(filters.private & (filters.photo | filters.document))
async def getimage(client, message):
    ## --- Users Adder --- ##
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
    ## --- Force Sub --- ##
    update_channel = Credentials.UPDATES_CHANNEL
    if update_channel:
        try:
            user = await client.get_chat_member(update_channel, message.chat.id)
            if user.status == "kicked":
               await client.send_message(
                   chat_id=message.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/Mo_Tech_Group).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("🔔Join My Update Channel🔔", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/Mo_Tech_Group).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return
    if message.document:
        if not message.document.file_name.endswith(".jpg"):
            return
    tmp = os.path.join("downloads", str(message.chat.id))
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    img_path = os.path.join(tmp, str(uuid.uuid4()) + ".jpg")
    dwn = await message.reply_text("🅳︎🅾︎🆆︎🅽︎🅻︎🅾︎🅰︎🅳︎🅸︎🅽︎🅶︎....", True)
    img_path = await client.download_media(message=message, file_name=img_path)
    await dwn.edit_text("🆄︎🅿︎🅻︎🅾︎🅰︎🅳︎🅸︎🅽︎🅶︎....")
    try:
        response = upload_file(img_path)
    except Exception as error:
        await dwn.edit_text(f"Oops, Something went wrong!\n\n**Error:** {error}")
        return
    await dwn.edit_text(f"https://telegra.ph{response[0]}")
    shutil.rmtree(tmp, ignore_errors=True)

## --- Custom Callback Filter --- ##
def dynamic_data_filter(data):
    async def func(flt, _, query):
        return flt.data == query.data
    return filters.create(func, data=data)

@Mo_tech_yt.on_callback_query(dynamic_data_filter("about"))
async def about_meh(_, query):
    buttons = [
        [
           InlineKeyboardButton("🗣️Group", url="https://telegram.dog/Mo_Tech_Group"),
           InlineKeyboardButton("📃Bot List", url="https://telegram.dog/Mo_Tech_YT"),
           InlineKeyboardButton("✳️Source", url="https://github.com/PR0FESS0R-99/Image-Upload")
        ],
        [
           InlineKeyboardButton("🙏Help", callback_data="help"),
           InlineKeyboardButton("🏠Home", callback_data="home"),
           InlineKeyboardButton("🔐Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        about_text,
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("help"))
async def help_meh(_, query):
    buttons = [
        [
           InlineKeyboardButton("🗣️Group", url="https://telegram.dog/Mo_Tech_Group"),
           InlineKeyboardButton("📃Bot List", url="https://telegram.dog/Mo_Tech_YT"),
           InlineKeyboardButton("✳️Source", url="https://github.com/PR0FESS0R-99/Image-Upload")
        ],
        [
           InlineKeyboardButton("👨‍💼About", callback_data="about"),
           InlineKeyboardButton("🏠Home", callback_data="home"),
           InlineKeyboardButton("🔐Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        help_text,
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("home"))
async def go_to_home(_, query):
    buttons = [
        [
           InlineKeyboardButton("🗣️Group", url="https://telegram.dog/Mo_Tech_Group"),
           InlineKeyboardButton("📃Bot List", url="https://telegram.dog/Mo_Tech_YT"),
           InlineKeyboardButton("✳️Source", url="https://github.com/PR0FESS0R-99/Image-Upload")
        ],
        [
           InlineKeyboardButton("🙏Help", callback_data="help"),
           InlineKeyboardButton("👨‍💼About", callback_data="about"),
           InlineKeyboardButton("🔐Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        home_text.format(query.message.chat.first_name, query.message.chat.id),
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("closeit"))
async def closeme(_, query):
    await query.message.delete()
    await query.answer()


Mo_tech_yt.run()
