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
from DAXXROBOT.modules.helper_funcs.chat_status import is_user_admin
from DAXXROBOT.modules.helper_funcs.misc import paginate_modules


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

    return ping_time
PM_START_TEX = """
ʜᴇʟʟᴏ `{}`, ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ \nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙʀᴏ . . . 
"""


PM_START_TEXT = """ 
*ʜᴇʏ* {} , 🥀
*๏ ɪ'ᴍ {} ʜᴇʀᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs!
ʜɪᴛ ʜᴇʟᴘ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ɪɴ ᴍʏ ғᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ!*
➻ *ᴛʜᴇ ᴍᴏsᴛ ᴩᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ  💖 ᴍᴜsɪᴄ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴀɴᴅ ɪ ʜᴀᴠᴇ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.*
─────────────────
   *➻ ᴜsᴇʀs »* {}
   *➻ ᴄʜᴀᴛs »* {}
─────────────────
"""

buttons = [
    [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
    [
        InlineKeyboardButton(
            text="❣️ 𝐀ᴅᴅ 𝐌ᴇ 𝐁ᴀʙʏ ❣️",
            url=f"https://t.me/NARUTO_X_ROBOT?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="📚 ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs", callback_data="Main_help"),
    ],
    

]

HELP_STRINGS = f"""
» *{BOT_NAME}  ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴀʙᴏᴜᴛ sᴘᴇᴄɪғɪᴄs ᴄᴏᴍᴍᴀɴᴅ*"""

DONATE_STRING = f"""ʜᴇʏ ʙᴀʙʏ,
  ʜᴀᴩᴩʏ ᴛᴏ ʜᴇᴀʀ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴅᴏɴᴀᴛᴇ."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("DAXXROBOT.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_photo(
        chat_id=chat_id,
        photo=START_IMG,
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )

def start(update: Update, context: CallbackContext):
    args = context.args
    global uptime
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="◁", callback_data="help_back")]]
                    ),
                )
            elif args[0].lower() == "markdownhelp":
                IMPORTED["𝐄xᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "𝐑ᴜʟᴇs" in IMPORTED:
                IMPORTED["𝐑ᴜʟᴇs"].send_rules(update, args[0], from_pm=True)



def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        prnt("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):

def daxxabout_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "daeeffsxx":
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_caption(f"*ʜᴇʏ,*🥀\n  *ᴛʜɪs ɪs {dispatcher.bot.first_name}*"
            "\n*ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ 💖 ᴍᴜsɪᴄ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀꜱɪʟʏ ᴀɴᴅ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ꜱᴄᴀᴍᴍᴇʀꜱ ᴀɴᴅ ꜱᴘᴀᴍᴍᴇʀꜱ.*"
            "\n*ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ sǫʟᴀʟᴄʜᴇᴍʏ ᴀɴᴅ ᴍᴏɴɢᴏᴅʙ ᴀs ᴅᴀᴛᴀʙᴀsᴇ.*"
            "\n\n────────────────────"
            f"\n*➻ ᴜᴩᴛɪᴍᴇ »* {uptime}"
            f"\n*➻ ᴜsᴇʀs »* {sql.num_users()}"
            f"\n*➻ ᴄʜᴀᴛs »* {sql.num_chats()}"
            "\n────────────────────"
            "\n\n➲  ɪ ᴄᴀɴ ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀꜱ."
            "\n➲  ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ꜰʟᴏᴏᴅ ꜱʏꜱᴛᴇᴍ."
            "\n➲  ɪ ᴄᴀɴ ɢʀᴇᴇᴛ ᴜꜱᴇʀꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀɴᴅ ᴇᴠᴇɴ ꜱᴇᴛ ᴀ ɢʀᴏᴜᴘ'ꜱ ʀᴜʟᴇꜱ."
            "\n➲  ɪ ᴄᴀɴ ᴡᴀʀɴ ᴜꜱᴇʀꜱ ᴜɴᴛɪʟ ᴛʜᴇʏ ʀᴇᴀᴄʜ ᴍᴀx ᴡᴀʀɴꜱ, ᴡɪᴛʜ ᴇᴀᴄʜ ᴘʀᴇᴅᴇꜰɪɴᴇᴅ ᴀᴄᴛɪᴏɴꜱ ꜱᴜᴄʜ ᴀꜱ ʙᴀɴ, ᴍᴜᴛᴇ, ᴋɪᴄᴋ, ᴇᴛᴄ."
            "\n➲  ɪ ʜᴀᴠᴇ ᴀ ɴᴏᴛᴇ ᴋᴇᴇᴘɪɴɢ ꜱʏꜱᴛᴇᴍ, ʙʟᴀᴄᴋʟɪꜱᴛꜱ, ᴀɴᴅ ᴇᴠᴇɴ ᴘʀᴇᴅᴇᴛᴇʀᴍɪɴᴇᴅ ʀᴇᴘʟɪᴇꜱ ᴏɴ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅꜱ."
            f"\n\n➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ {dispatcher.bot.first_name}.",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
                    [
                        InlineKeyboardButton(
                            text="🚩𝐒ᴜᴩᴩᴏʀᴛ", callback_data="daxxsupport"
                        ),
                        InlineKeyboardButton(
                            text="𝐂ᴏᴍᴍᴀɴᴅs 💁", callback_data="Main_help"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="👨‍💻 𝐎ᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="🥀 𝐒ᴏᴜʀᴄᴇ",
                            callback_data="source_",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="daxxback"),
                    ],
                ]
            ),
        )
    elif query.data == "daxxeetsupport":
        query.message.edit_caption("**๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʜᴇʟᴩ ᴀɴᴅ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀ**"
            f"\n\nɪғ ʏᴏᴜ ғᴏᴜɴᴅ ᴀɴʏ ʙᴜɢ ɪɴ {dispatcher.bot.first_name} ᴏʀ ɪғ ʏᴏᴜ ᴡᴀɴɴᴀ ɢɪᴠᴇ ғᴇᴇᴅʙᴀᴄᴋ ᴀʙᴏᴜᴛ ᴛʜᴇ {dispatcher.bot.first_name}, ᴩʟᴇᴀsᴇ ʀᴇᴩᴏʀᴛ ɪᴛ ᴀᴛ sᴜᴩᴩᴏʀᴛ ᴄʜᴀᴛ.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
                    [
                        InlineKeyboardButton(
                            text="🏡 𝐒ᴜᴩᴩᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="𝐀ʙᴏᴜᴛ 🍷", url=f"https://t.me/SAIFALLBOT"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="𝐎ᴡɴᴇʀ 🥀", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="𝐆ʀᴏᴜᴘ🍹", url=f"https://t.me/BOTSUPPORT_CHAT"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="◁", callback_data="daxx"),
                    ],
                ]
            ),
        )
    elif query.data == "daxxeryback":
        first_name = update.effective_user.first_name 
        query.message.edit_caption(PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )
def DAXXROBOT_Main_Callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "Maiggn_help":
        query.message.edit_caption(f"""
 ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ {BOT_NAME}
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="📕 𝐌ᴀɴᴀɢᴇᴍᴇɴᴛ", callback_data="help_back"),
                        InlineKeyboardButton(text="𝐌ᴜsɪᴄ 🎧", callback_data="Music_")
                    ],
                    [
                        InlineKeyboardButton(text="❣️ 𝐍ᴀʀᴜᴛᴏ", callback_data="basic_help"),
                        InlineKeyboardButton(text="𝐄xᴘᴇʀᴛ📱", callback_data="expert_help")
                    ],
                    [
                        InlineKeyboardButton(text="🍹 𝐀ᴅᴠᴀɴᴄᴇ", callback_data="advance_help"),
                        InlineKeyboardButton(text="𝐀ɪ 𝐁ᴏᴛ", callback_data="donation_help") 
                    ],
                    [InlineKeyboardButton(text="• 𝐇ᴏᴍᴇ •", callback_data="daxxback")]
                ]
            ),
        )
    elif query.data=="basiggc_help":
        query.message.edit_caption("""
       ╔═════════════════╗
   🍃🌹 𝐈 𝐀ᴍ 𝐍αяυтσ ✘ 𝐑σвσт 𝐀  𝐀ᴅᴠᴀɴᴄᴇ 𝐀ɴɪᴍᴇ  𝐁ᴀsᴇᴅ  𝐌ᴀɴᴀɢᴍᴇɴᴛ 𝐁ᴏᴛ. 🌼💐

🌲 𝙰𝙱𝙾𝚄𝚃 𝙽𝙰𝚁𝚄𝚃𝙾 🌲 :- 
Иαяʋтσ Ʋʓʋмακι, α нʏρɛяαcтιʏɛ αи∂ κиʋcκℓɛ-нɛα∂ɛ∂ иιиʝα, ℓιʏɛƨ ιи Ƙσиσнαɢακʋяɛ, тнɛ Ħι∂∂ɛи ˩ɛαғ ʏιℓℓαɢɛ. Μσмɛитƨ ρяισя тσ нιƨ вιятн, α нʋɢɛ ∂ɛмσи κиσωи as тнɛ Ƙʏʋʋвι, тнɛ Иιиɛ-тαιℓɛ∂ Ғσϰ, αттαcκɛ∂ Ƙσиσнαɢακʋяɛ αи∂ ωяɛακɛ∂ нαʏσc. Ɩи σя∂ɛя тσ ρʋт αи ɛи∂ тσ тнɛ Ƙʏʋʋвι'ƨ яαмραɢɛ, the ℓɛα∂ɛя σғ тнɛ ʏιℓℓαɢɛ, тнɛ 4тн Ħσκαɢɛ, ƨαcяιғιcɛ∂ нιƨ ℓιғɛ αи∂ ƨɛαℓɛ∂ тнɛ мσиƨтяσʋƨ вɛαƨт ιиƨι∂ɛ тнɛ иɛωвσяи Иαяʋтσ. 
Ƨнʋииɛ∂ вɛcαʋƨɛ σғ тнɛ ρяɛƨɛиcɛ σғ тнɛ Ƙʏʋʋвι ιиƨι∂ɛ нιм, Иαяʋтσ ƨтяʋɢɢℓɛƨ тσ ғιи∂ нιƨ ρℓαcɛ ιи тнɛ ʏιℓℓαɢɛ. Ħɛ ƨтяιʏɛƨ тσ вɛcσмɛ тнɛ Ħσκαɢɛ σғ Ƙσиσнαɢακʋяɛ, αи∂ нɛ мɛɛтƨ мαиʏ ғяιɛи∂ƨ αи∂ ғσɛƨ αℓσиɢ тнɛ ωαʏ.  🍂💫
       ╚═════════════════╝.""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Main_help"),InlineKeyboardButton(text="• 𝐒ᴜᴘᴘᴏʀᴛ •", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
            )
    elif query.data=="daxxbgyack":
        query.message.edit_caption("""Exᴘᴇʀᴛ ᴄᴏᴍᴍᴀɴᴅs

👥 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs
👮🏻 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs & Mᴏᴅᴇʀᴀᴛᴏʀs.
🕵🏻 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs

🕵🏻  /unbanall ᴍᴇᴍʙᴇʀs ғʀᴏᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘs
👮🏻  /unmuteall ᴜɴᴍᴜᴛᴇᴀʟʟ ᴀʟʟ ғʀᴏᴍ Yᴏᴜʀ Gʀᴏᴜᴘ

Pɪɴɴᴇᴅ Mᴇssᴀɢᴇs
🕵🏻  /pin [ᴍᴇssᴀɢᴇ] sᴇɴᴅs ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ Bᴏᴛ ᴀɴᴅ ᴘɪɴs ɪᴛ.
🕵🏻  /pin ᴘɪɴs ᴛʜᴇ ᴍᴇssᴀɢᴇ ɪɴ ʀᴇᴘʟʏ
🕵🏻  /unpin ʀᴇᴍᴏᴠᴇs ᴛʜᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ.
🕵🏻  /adminlist ʟɪsᴛ ᴏғ ᴀʟʟ ᴛʜᴇ sᴘᴇᴄɪᴀʟ ʀᴏʟᴇs ᴀssɪɢɴᴇᴅ ᴛᴏ ᴜsᴇʀs.

◽️ /bug: (ᴍᴇssᴀɢᴇ) ᴛᴏ Sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴇʀʀᴏʀs ᴡʜɪᴄʜ ʏᴏᴜ ᴀʀᴇ ғᴀᴄɪɴɢ 
ᴇx: /bug Hᴇʏ Tʜᴇʀᴇ Is ᴀ Sᴏᴍᴇᴛʜɪɴɢ Eʀʀᴏʀ @username ᴏғ ᴄʜᴀᴛ! .""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Main_help"),InlineKeyboardButton(text="• 𝐒ᴜᴘᴘᴏʀᴛ •", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
            )                                        
    elif query.data=="advancyye_help":
        query.message.edit_caption("""Aᴅᴠᴀɴᴄᴇᴅ Cᴏᴍᴍᴀɴᴅs

👮🏻Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs & Mᴏᴅᴇʀᴀᴛᴏʀs.
🕵🏻Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs.
🛃 Aᴠᴀɪʟᴀʙʟᴇ ᴛᴏ Aᴅᴍɪɴs & Cʟᴇᴀɴᴇʀs

Wᴀʀɴ Mᴀɴᴀɢᴇᴍᴇɴᴛ
👮🏻  /warn ᴀᴅᴅs ᴀ ᴡᴀʀɴ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ
👮🏻  /unwarn ʀᴇᴍᴏᴠᴇs ᴀ ᴡᴀʀɴ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ
👮🏻  /warns ʟᴇᴛs ʏᴏᴜ sᴇᴇ ᴀɴᴅ ᴍᴀɴᴀɢᴇ ᴜsᴇʀ ᴡᴀʀɴs

🛃  /del ᴅᴇʟᴇᴛᴇs ᴛʜᴇ sᴇʟᴇᴄᴛᴇᴅ ᴍᴇssᴀɢᴇ
🛃  /purge ᴅᴇʟᴇᴛᴇs ғʀᴏᴍ ᴛʜᴇ sᴇʟᴇᴄᴛᴇᴅ ᴍᴇssᴀɢᴇ.""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Main_help"),InlineKeyboardButton(text="• 𝐒ᴜᴘᴘᴏʀᴛ •", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
            )
    elif query.data=="expeyyrt_help":
        query.message.edit_caption(f"""━━━━━━━━━━━━━━━━━━━━
ᴍᴀᴋᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇꜰꜰᴇᴄᴛɪᴠᴇ ɴᴏᴡ :
🎉 ᴄᴏɴɢʀᴀɢᴜʟᴀᴛɪᴏɴꜱ 🎉
[{BOT_NAME}]("https://t.me/{BOT_USERNAME}") ɴᴏᴡ ʀᴇᴀᴅʏ ᴛᴏ
ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ.

ᴀᴅᴍɪɴ ᴛᴏᴏʟꜱ :
ʙᴀꜱɪᴄ ᴀᴅᴍɪɴ ᴛᴏᴏʟꜱ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ
ᴘʀᴏᴛᴇᴄᴛ & ᴘᴏᴡᴇʀᴜᴘ ʏᴏᴜʀ ɢʀᴏᴜᴘ.
ʏᴏᴜ ᴄᴀɴ ʙᴀɴ, ᴋɪᴄᴋ, ᴘʀᴏᴍᴏᴛᴇ
ᴍᴇᴍʙᴇʀꜱ ᴀꜱ ᴀᴅᴍɪɴ ᴛʜʀᴏᴜɢʜ ʙᴏᴛ.

ɢʀᴇᴇᴛɪɴɢꜱ :
ʟᴇᴛꜱ ꜱᴇᴛ ᴀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ
ᴡᴇʟᴄᴏᴍᴇ ɴᴇᴡ ᴜꜱᴇʀꜱ ᴄᴏᴍɪɴɢ ᴛᴏ
ʏᴏᴜʀ ɢʀᴏᴜᴘ.
ꜱᴇɴᴅ /setwelcome ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ
ꜱᴇᴛ ᴀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇꜱꜱᴀɢᴇ!""",parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Main_help"),InlineKeyboardButton(text="• 𝐒ᴜᴘᴘᴏʀᴛ •", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
            )
    elif query.data=="donatijjon_help":
        query.message.edit_caption("""cℓιcκ [𝐀ɪ 𝐁ᴏᴛ](https://t.me/GOJO_AIBOT) """,parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [ [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
                    [
                        InlineKeyboardButton(text=" 𝐃ᴏɴᴀᴛᴇ ", url="https://t.me/SAIFALLBOT/18"),InlineKeyboardButton(text="• 𝐒ᴜᴘᴘᴏʀᴛ •", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
            )  
def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "sour_":
        query.message.edit_caption(
            f"""
*ʜᴇʏ,
 ᴛʜɪs ɪs {BOT_NAME},
ᴀɴ ᴏᴩᴇɴ sᴏᴜʀᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.*

ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ : [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon)
[ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)
[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)
ᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.


*ʜᴇʀᴇ ɪs ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ :* [ɢɪᴛʜᴜʙ](https://github.com/SAIFDEAD)


{BOT_NAME} ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](68©74©74©70©73©3A©2F©2F©67©69©74©68©75©62©2E©63©6F©6D©2F©44©41©58©58©54©45©41©4D©2F©59©75©6D©69©6B©6F©6F©52©6F©62©6F©74/blob/main/LICENSE).
© 2023 - 2024 | [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://t.me/{SUPPORT_CHAT}), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ.
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [[
        InlineKeyboardButton(text="𝐒ᴏᴜʀᴄᴇ", url=f"https://github.com/SAIFDEAD/SAIFROBOT")
                ],
                 [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],[InlineKeyboardButton(text="◁", callback_data="source_back")]]
            ),
        )
    elif query.data == "souce_back":
        first_name = update.effective_user.first_name
        query.message.edit_caption(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME,sql.num_users(),sql.num_chats()),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            
        )

        
def Music_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "Musc_":
        query.message.edit_caption(f"""
 ʜᴇʀᴇ ɪꜱ ʜᴇʟᴘ ᴍᴇɴᴜ ꜰᴏʀ ᴍᴜꜱɪᴄ 
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
        InlineKeyboardButton(text="🏡", callback_data="daxxback"),
        InlineKeyboardButton(text="🛡️", callback_data="daxx"),
        InlineKeyboardButton(text="💳", callback_data="source_"),
        InlineKeyboardButton(text="🧑‍💻", url=f"tg://user?id={OWNER_ID}"),
        InlineKeyboardButton(text="🖥️", callback_data="Main_help"),
     ],
                    [
                        InlineKeyboardButton(
                            text=" 𝐀ᴅᴍɪɴ", callback_data="Music_admin"
                        ),
                        InlineKeyboardButton(
                            text="𝐏ʟᴀʏ ", callback_data="Music_play"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text=" 𝐁ᴏᴛ ", callback_data="Music_bot"),
                        InlineKeyboardButton(
                            text="𝐌ᴜsɪᴄ 𝐁ᴏᴛ", callback_data="Music_extra"),
                    ],
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Main_help")
                    ],
                ]
            ),
        )
    elif query.data == "Mustic_admin":
        query.message.edit_caption(f"*» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ «*"
            f"""
ᴊᴜsᴛ ᴀᴅᴅ *ᴄ* ɪɴ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ᴜsᴇ ᴛʜᴇᴍ ғᴏʀ ᴄʜᴀɴɴᴇʟ.

/pause : ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.

/resume : ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ.

/skip : sᴋɪᴩ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ.

/end ᴏʀ /stop : ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ.

/player : ɢᴇᴛ ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴩʟᴀʏᴇʀ ᴩᴀɴᴇʟ.

/queue : sʜᴏᴡs ᴛʜᴇ ǫᴜᴇᴜᴇᴅ ᴛʀᴀᴄᴋs ʟɪsᴛ.
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" 𝐁ᴀᴄᴋ ", callback_data="Music_"),InlineKeyboardButton(text="𝐒ᴜᴘᴘᴏʀᴛ", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
        )
    elif query.data == "Musigc_play":
        query.message.edit_caption(f"*» ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅꜱ «*"
            f"""
/play or /vplay or /cplay  - ʙᴏᴛ ᴡɪʟʟ ꜱᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ʏᴏᴜʀ ɢɪᴠᴇɴ ϙᴜᴇʀʏ on ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴏʀ ꜱᴛʀᴇᴀᴍ ʟɪᴠᴇ ʟɪɴᴋꜱ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛꜱ.

/playforce or /vplayforce or /cplayforce -  ғᴏʀᴄᴇ ᴘʟᴀʏ ꜱᴛᴏᴘꜱ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏɪɴɢ ᴛʀᴀᴄᴋ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀɴᴅ ꜱᴛᴀʀᴛꜱ ᴘʟᴀʏɪɴɢ ᴛʜᴇ ꜱᴇᴀʀᴄʜᴇᴅ ᴛʀᴀᴄᴋ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜᴏᴜᴛ ᴅɪꜱᴛᴜʀʙɪɴɢ/clearing queue.

/channelplay [ᴄʜᴀᴛ ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ] ᴏʀ [ᴅɪꜱᴀʙʟᴇ] - ᴄᴏɴɴᴇᴄᴛ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ᴍᴜꜱɪᴄ ᴏɴ ᴄʜᴀɴɴᴇʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ғʀᴏᴍ ʏᴏᴜʀ ɢʀᴏᴜᴘ.


*ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ*
 ʙᴏᴛ  ꜱᴇʀᴠᴇʀ ᴘʟᴀʏʟɪꜱᴛꜱ:
/playlist  - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴘʟᴀʏʟɪꜱᴛ ᴏɴ ꜱᴇʀᴠᴇʀꜱ.
/deleteplaylist - ᴅᴇʟᴇᴛᴇ ᴀɴʏ ꜱᴀᴠᴇᴅ ᴍᴜꜱɪᴄ ɪɴ ʏᴏᴜʀ ᴘʟᴀʏʟɪꜱᴛ
/play  - ꜱᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴘʟᴀʏʟɪꜱᴛ ғʀᴏᴍ ꜱᴇʀᴠᴇʀꜱ.
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="• 𝐁ᴀᴄᴋ •", callback_data="Music_"),InlineKeyboardButton(text="𝐒ᴜᴘᴘᴏʀᴛ", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
        )
    elif query.data == "Musiic_bot":
        query.message.edit_caption(f"*» ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ «*"
            f"""
/stats - ɢᴇᴛ ᴛᴏᴘ 10 ᴛʀᴀᴄᴋꜱ ɢʟᴏʙᴀʟ ꜱᴛᴀᴛꜱ, ᴛᴏᴘ 10 ᴜꜱᴇʀꜱ ᴏғ ʙᴏᴛ, ᴛᴏᴘ 10 ᴄʜᴀᴛꜱ ᴏɴ ʙᴏᴛ, ᴛᴏᴘ 10 ᴘʟᴀʏᴇᴅ ɪɴ ᴀ ᴄʜᴀᴛ ᴇᴛᴄ ᴇᴛᴄ.

/sudolist - ᴄʜᴇᴄᴋ sᴜᴅᴏ ᴜsᴇʀs ᴏғ ᴀʙɢ  ʙᴏᴛ

/lyrics [ᴍᴜsɪᴄ ɴᴀᴍᴇ] - sᴇᴀʀᴄʜᴇs ʟʏʀɪᴄs ғᴏʀ ᴛʜᴇ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴍᴜsɪᴄ ᴏɴ ᴡᴇʙ.

/song [ᴛʀᴀᴄᴋ ɴᴀᴍᴇ] or [ʏᴛ ʟɪɴᴋ] - ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴʏ ᴛʀᴀᴄᴋ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ɪɴ ᴍᴘ3 or ᴍᴘ4 ғᴏʀᴍᴀᴛꜱ.

/player -  ɢᴇt ᴀ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴘʟᴀʏɪɴɢ ᴘᴀɴᴇʟ.

c ꜱᴛᴀɴᴅꜱ ꜰᴏʀ ᴄʜᴀɴɴᴇʟ ᴘʟᴀʏ.

/queue ᴏʀ /cqueue- ᴄʜᴇᴄᴋ Qᴜᴇᴜᴇ ʟɪꜱᴛ ᴏꜰ ᴍᴜꜱɪᴄ.
""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" 𝐁ᴀᴄᴋ ", callback_data="Music_"),InlineKeyboardButton(text="𝐒ᴜᴘᴘᴏʀᴛ", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
        )
    elif query.data == "Mussic_extra":
        query.message.edit_caption(f"*» ᴇxᴛʀᴀ ᴄᴏᴍᴍᴀɴᴅꜱ «*"
            f"""
𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐫𝐞 𝐭𝐨 𝐠𝐞𝐭 𝐦𝐮𝐬𝐢𝐜 𝐛𝐨𝐭 :- [𝙼𝚄𝚂𝙸𝙲](https://t.me/HINATA_N_BOT)


""",
            parse_mode=ParseMode.MARKDOWN,
            
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=" 𝐁ᴀᴄᴋ ", callback_data="Music_"),InlineKeyboardButton(text="𝐒ᴜᴘᴘᴏʀᴛ", url=f"https://t.me/BOTSUPPORT_CHAT")
                    ]
                ]
            ),
        )
    elif query.data == "Music_back":
        first_name = update.effective_user.first_name
        query.message.edit_caption(PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,

        )


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_photo(START_IMG,
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=" ʜᴇʟᴘ ​",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_photo(START_IMG,"» Wʜᴇʀᴇ ᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ?.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="💖 ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ",
                            url="https://t.me/{}?start=help".format(context.bot.username),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❣️ ᴏᴩᴇɴ ʜᴇʀᴇ",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="◁", callback_data="help_back"),InlineKeyboardButton(text="𝐒ᴜᴘᴘᴏʀᴛ", url=f" https://t.me/BOTSUPPORT_CHAT")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="◁",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what "
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(text=
                """Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text("""Hi there! There are quite a few settings for {} - go ahead and pick what 
                you're interested in.""".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ᴛʜɪs ᴄʜᴀᴛ's sᴇᴛᴛɪɴɢs ᴀs ᴡᴇʟʟ ᴀs ʏᴏᴜʀs"
            msg.reply_photo(START_IMG,text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs​",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs"

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 6585111267:
            update.effective_message.reply_text(
                f"» ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴩᴇʀ ᴏғ {dispatcher.bot.first_name} sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ ɪs [ɢɪᴛʜᴜʙ](https://github.com/SAIFDEAD/SAIFROBOT)",
                parse_mode=ParseMode.MARKDOWN,
                
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                
            )

            update.effective_message.reply_text(
                "ɪ'ᴠᴇ ᴘᴍ'ᴇᴅ ʏᴏᴜ ᴀʙᴏᴜᴛ ᴅᴏɴᴀᴛɪɴɢ ᴛᴏ ᴍʏ ᴄʀᴇᴀᴛᴏʀ!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ғɪʀsᴛ ᴛᴏ ɢᴇᴛ ᴅᴏɴᴀᴛɪᴏɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated naruto robot !")
    raise DispatcherHandlerStop


def main():
    global x
    x=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="❣️ 𝐀𝙳𝙳 𝙼𝐞 𝐁𝙰𝙱𝚈 ❣️",
                            url="https:/t.me/HINATA_N_BOT?startgroup=true"
                            )
                       ]
                ]
                     )
    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@SAIFHELPGC",
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
