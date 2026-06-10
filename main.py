import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)

# Environment Variable ကနေ Token ယူမယ်
TOKEN = os.getenv("BOT_TOKEN")

# Application တည်ဆောက်ခြင်း
telegram_app = Application.builder().token(TOKEN).build()

# --- ကုဒ်ထဲကနေ Telegram ဆီ Command List လှမ်းသတ်မှတ်မည့် Function ---
async def set_bot_commands():
    try:
        commands = [
            BotCommand("id", "မိမိ၏ Telegram ID နှင့် Bio အချက်အလက်များကို ကြည့်ရန်"),
            BotCommand("search", "တခြားသူ၏ Username ကို ရိုက်ရှာပြီး ID နှင့် Bio စစ်ဆေးရန်")
        ]
        # Telegram Server ဆီ Menu commands list ကို လှမ်းပို့ပြီး သတ်မှတ်ခြင်း
        await telegram_app.bot.set_my_commands(commands)
        print("Bot commands successfully updated via code!")
    except Exception as e:
        print(f"Failed to set commands: {e}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    message = (
        f"မင်္ဂလာပါ {user_name} 🙏\n\n"
        "ဒီ Bot လေးကတော့ မိမိကိုယ်တိုင်သာမက တခြားသူတွေရဲ့ ID၊ Bio နဲ့ Channel ID တွေကိုပါ ရှာဖွေနိုင်ပါတယ်။\n\n"
        "💡 **အသုံးပြုနိုင်သော စနစ်များ:**\n"
        "✨ /id - မိမိရဲ့ ကိုယ်ပိုင် Telegram Profile အချက်အလက်များကို ကြည့်ရန်\n"
        "✨ `/search @username` - တခြားသူရဲ့ Username ကို ရိုက်ရှာပြီး ID နှင့် Bio ကို စစ်ဆေးရန်\n"
        "✨ **Forward Message** - တခြားသူတစ်ယောက်ယောက် (သို့) Channel/Group က ပို့ထားတဲ့စာကို ဒီ Bot ဆီ Forward လှမ်းပို့ရုံဖြင့် သူတို့ရဲ့ ID ကို ချက်ချင်း စစ်ဆေးပေးမှာ ဖြစ်ပါတယ်။"
    )
    await update.message.reply_text(text=message, parse_mode="Markdown")

# /id command (မိမိကိုယ်ပိုင် Info + Bio)
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "မရှိပါ"
    
    try:
        full_chat = await context.bot.get_chat(user_id)
        bio = full_chat.description if full_chat.description else "ရေးမထားပါ"
    except Exception:
        bio = "မသိနိုင်ပါ (Privacy ပိတ်ထားခြင်းကြောင့် ဖြစ်နိုင်သည်)"

    message = (
        "📊 **သင့်ရဲ့ Telegram Profile အချက်အလက်များ**\n\n"
        "👤 **အမည်:** `{}`\n"
        "🎯 **Telegram ID:** `{}`\n"
        "🌐 **Username:** {}\n"
        "📝 **Bio Description:**\n_{}_\n\n"
        "_(ID ကို နှိပ်လိုက်ရုံဖြင့် အလိုအလျောက် Copy ကူးပြီးသား ဖြစ်သွားပါမည်)_"
    ).format(user.first_name, user_id, username, bio)
    
    await update.message.reply_text(text=message, parse_mode="Markdown")

# /search @username command (တခြားသူကို ရှာဖွေခြင်း)
async def search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(text="⚠️ ကျေးဇူးပြု၍ ရှာချင်တဲ့ Username ကို တွဲရိုက်ပေးပါ။\nဥပမာ- `/search @durov`", parse_mode="Markdown")
        return

    target_username = context.args[0].replace("@", "")
    
    try:
        chat = await context.bot.get_chat(f"@{target_username}")
        chat_id = chat.id
        first_name = chat.first_name if chat.first_name else chat.title
        bio = chat.description if chat.description else "ရေးမထားပါ"
        chat_type = "User 👤" if chat.type == "private" else chat.type.capitalize()

        response = (
            f"🔍 **ရှာဖွေမှု ရလဒ် ({chat_type})**\n\n"
            f"📛 **အမည်:** `{first_name}`\n"
            f"🆔 **ID:** `{chat_id}`\n"
            f"🌐 **Username:** @{target_username}\n"
            f"📝 **Bio Description:**\n_{bio}_\n"
        )
        await update.message.reply_text(text=response, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(
            text="❌ **ရှာမတွေ့ပါ!**\n\n"
                 "ဖြစ်နိုင်ချေအကြောင်းရင်းများ -\n"
                 "၁။ Username မှားနေခြင်း။\n"
                 "၂။ ထိုသူသည် ဤ Bot ကို တစ်ကြိမ်မှ မသုံးဖူးသေးခြင်း သို့မဟုတ် Bot နှင့် Group တစ်ခုတည်းတွင် အတူမရှိခြင်း။\n"
                 "💡 _အကြံပြုချက်- ထိုသူ၏ စာတစ်စောင်ကို Bot ဆီသို့ တိုက်ရိုက် **Forward** လုပ်ပြီး ပိုမိုသေချာစွာ စစ်ဆေးနိုင်ပါတယ်_"
        )

# Forward လုပ်လာသည့် Message များကို ဖမ်းမည့်စနစ်
async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
    # ၁။ Channel သို့မဟုတ် Group ကနေ Forward လုပ်လာလျှင်
    if msg.forward_from_chat:
        chat = msg.forward_from_chat
        chat_id = chat.id
        chat_title = chat.title
        chat_username = f"@{chat.username}" if chat.username else "Private Channel/Group"
        chat_type = "Channel 📢" if chat.type == "channel" else "Group 👥"
        
        try:
            full_chat = await context.bot.get_chat(chat_id)
            bio = full_chat.description if full_chat.description else "ရေးမထားပါ"
        except Exception:
            bio = "မသိနိုင်ပါ"

        response = (
            f"🔍 **Forward စစ်ဆေးမှု ရလဒ် ({chat_type})**\n\n"
            f"📛 **အမည်:** `{chat_title}`\n"
            f"🆔 **ID:** `{chat_id}`\n"
            f"🌐 **Username:** {chat_username}\n"
            f"📝 **Description:**\n_{bio}_\n"
        )
        await update.message.reply_text(text=response, parse_mode="Markdown")
        
    # ၂။ လူပုဂ္ဂိုလ် (User) တစ်ဦးချင်းစီဆီက Forward လုပ်လာလျှင်
    elif msg.forward_from:
        fwd_user = msg.forward_from
        fwd_id = fwd_user.id
        username = f"@{fwd_user.username}" if fwd_user.username else "မရှိပါ"
        
        try:
            full_chat = await context.bot.get_chat(fwd_id)
            bio = full_chat.description if full_chat.description else "ရေးမထားပါ"
        except Exception:
            bio = "မသိနိုင်ပါ (User မှ Privacy ပိတ်ထားခြင်းကြောင့် ဖြစ်နိုင်သည်)"

        response = (
            f"🔍 **Forward User စစ်ဆေးမှု ရလဒ် 👤**\n\n"
            f"👤 **အမည်:** `{fwd_user.first_name}`\n"
            f"🎯 **User ID:** `{fwd_id}`\n"
            f"🌐 **Username:** {username}\n"
            f"📝 **Bio Description:**\n_{bio}_\n"
        )
        await update.message.reply_text(text=response, parse_mode="Markdown")
    
    # ၃။ User က Forward Privacy ပိတ်ထားလျှင်
    elif msg.forward_sender_name:
        await update.message.reply_text(
            text=f"🔍 **Forward စစ်ဆေးမှု ရလဒ်**\n\n"
                 f"👤 **အမည်:** `{msg.forward_sender_name}`\n"
                 f"⚠️ **သတိပေးချက်:** ဒီအသုံးပြုသူက Privacy ပိတ်ထားတဲ့အတွက် ID ကို ဆွဲယူခွင့် မပေးပါဘူးခင်ဗျာ။"
        )
    else:
        await update.message.reply_text(text="⚠️ ID ကို စစ်ဆေးဖို့အတွက် တခြားသူရဲ့စာ သို့မဟုတ် Channel ထဲကစာကို ဒီ Bot ဆီ Forward လုပ်ပြီး လှမ်းပို့ပေးရမှာ ဖြစ်ပါတယ်ခင်ဗျာ။")

# Handlers များကို Register လုပ်ခြင်း
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("id", get_id))
telegram_app.add_handler(CommandHandler("search", search_user))
telegram_app.add_handler(MessageHandler(filters.FORWARDED, handle_forward))

# Webhook Endpoint (ဒီနေရာမှာ Command List ကိုပါ တစ်ခါတည်း Initialize လုပ်သွားမှာပါ)
@app.route('/', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            req_json = request.get_json(force=True)
            update = Update.de_json(req_json, telegram_app.bot)
            
            # Application နှင့် Command များကို အလိုအလျောက် သတ်မှတ်ခြင်း
            loop.run_until_complete(telegram_app.initialize())
            loop.run_until_complete(set_bot_commands()) # <--- ဒီနေရာကနေ လှမ်းခေါ်သွားတာပါ
            loop.run_until_complete(telegram_app.process_update(update))
            
            return "OK", 200
        except Exception as e:
            print(f"Error occurred: {e}")
            return "Internal Error", 500
            
    return "Invalid Request", 400

@app.route('/', methods=['GET'])
def index():
    return "Advanced ID Finder Bot is running fine with Code-set Commands!", 200

# Vercel handler
def handler(environ, start_response):
    return app(environ, start_response)
