import importlib
import re
import time
import asyncio
from platform import python_version as y
from sys import argv
from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import DAXXROBOT.modules.no_sql.users_db as sql
from DAXXROBOT import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)
from DAXXROBOT.modules import ALL_MODULES


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)


    def main():
    global x
    x=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❣️ 𝐀𝙳𝙳 𝙼𝐞 𝐁𝙰𝙱𝚈 ❣️",
                            url="https:/t.me/HINATA_N_ROBOT?startgroup=true"
                            )
                       ]
                ]
                     )
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@BOTSUPPORT_CHAT",
                photo=f"{START_IMG}",
                caption=f"""
✨ㅤ{BOT_NAME} ɪs ᴀʟɪᴠᴇ ʙᴀʙʏ.
━━━━━━━━━━━━━
**ᴍᴀᴅᴇ Βy**[Dιcтaтor](https://t.me/SAIF_DICTATOR)
**ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:** `{y()}`
**ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ:** `{telever}`
**ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:** `{tlhver}`
**ᴩʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ:** `{pyrover}`
━━━━━━━━━━━━━
""",reply_markup=x,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        daxxabout_callback, pattern=r"daxx", run_async=True
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )
    music_callback_handler = CallbackQueryHandler(
        Music_about_callback, pattern=r"Music_",run_async=True
    )
    DAXXROBOT_main_handler = CallbackQueryHandler(
        DAXXROBOT_Main_Callback, pattern=r".*_help",run_async=True)
    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(music_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)
    dispatcher.add_handler(DAXXROBOT_main_handler)
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(source_callback_handler)
    LOGGER.info("Naruto robot depoly successfully 💖")
    updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded naruto robot modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
