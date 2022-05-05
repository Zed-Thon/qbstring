from asyncio.exceptions import TimeoutError
from Data import Data
from pyrogram import Client, filters
from telethon import TelegramClient
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

ERROR_MESSAGE = "**- أُووبـس! هنالك خطـأ!** \n\n**الخطـأ هـو -** : {} " \
            "\n\n**- الرجاء التواصل @zzzzl1l واعلامه بالخطـأ** " \
            "**- إذا كنت تريد الإبلاغ عن هذا كـ**" \
            "**- لم يتم تسجيل رسالة الخطأ هذه بواسطتنا!**"


@Client.on_message(filters.private & ~filters.forwarded & filters.command('generate'))
async def main(_, msg):
    await msg.reply(
        "**- اختـر تليثـون لاستخـراج كـود تيرمكـس زدثــون**",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("بايـروجـرام", callback_data="pyrogram"),
            InlineKeyboardButton("تليثــون", callback_data="telethon")
        ]])
    )


async def generate_session(bot, msg, telethon=False):
    await msg.reply("**- استخـراج كـود {}  يـوزربـوت..**".format("تليثـون" if telethon else "بايروجـرام"))
    user_id = msg.chat.id
    api_id_msg = await bot.ask(user_id, '**- قم ارسال كـود APP_ID**', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply('**- خطـأ بكود API_ID .. يرجى إنشاء جلسة جديدة مرة أخرى.**', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    api_hash_msg = await bot.ask(user_id, '**- قم ارسال كـود الايبي هـاش API_HASH**', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    api_hash = api_hash_msg.text
    phone_number_msg = await bot.ask(user_id, '**- قم بارسـال رقـم هاتف حسابـك تيليجـرام مع مفتـاح الدولـه**\n\n**- مثـال :** +967xxxxxxx', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    phone_number = phone_number_msg.text
    await msg.reply("**بـدء استخـراج الجلسـه 𝙕𝙀𝘿𝙏𝙝𝙤𝙣 ⌬....**")
    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    else:
        client = Client(":memory:", api_id, api_hash)
    await client.connect()
    try:
        if telethon:
            code = await client.send_code_request(phone_number)
        else:
            code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply('**- خطـأ بالاكـواد API_ID و API_HASH خطأ .. يرجى إنشاء جلسة جديدة مرة أخرى.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply('**- رقم الهاتف او مفتاح الدولة خاطئ .. حاول التحقق وإجراء جلسة جديدة مرة أخرى.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    try:
        phone_code_msg = await bot.ask(user_id, "**- يرجى التحقق من كود الدخول من حسابك تيليجرام ، إذا كان رمز الدخول بهذا الشكل 12345**\n**- قم بارساله بالشكل الاتي (خلي مسافه بين كل رقم والثاني)  1 2 3 4 5**", filters=filters.text, timeout=600)
        if await cancelled(api_id_msg):
            return
    except TimeoutError:
        await msg.reply('**- انتظـر دقيقتين . ثم قم بـ إنشاء جلسة جديدة.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    phone_code = phone_code_msg.text.replace(" ", "")
    try:
        if telethon:
            await client.sign_in(phone_number, phone_code, password=None)
        else:
            await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await msg.reply('**- كود الدخول غير صالح ، يرجى إنشاء جلسة أخرى.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await msg.reply('**- كود الدخول منتهي الصلاحية. الرجاء إنشاء جلسة أخرى.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            two_step_msg = await bot.ask(user_id, '**- حسابك يوجد فيه التحقق بـ خطوتين ، يرجى ادخال كلمة المرور.**', filters=filters.text, timeout=300)
        except TimeoutError:
            await msg.reply('**- انتظـر دقيقتين . ثم قم بـ إنشاء جلسة جديدة.**', reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        try:
            password = two_step_msg.text
            if telethon:
                await client.sign_in(password=password)
            else:
                await client.check_password(password=password)
            if await cancelled(api_id_msg):
                return
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await two_step_msg.reply('**- كلمة المرور خاطئـه. الرجاء إنشاء جلسة أخرى.**', quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = "**- كـود تيرمكـس {} 𝗭𝗧𝗵𝗼𝗻** \n\n{} \n\n**- تم الاستخـراج بواسطـة** @ZedThon\n**- تحياتـي .. زلــزال الهيبــه** @zzzzl1l".format("تليثـون" if telethon else "بايروجـرام", string_session)
    await client.send_message("me", text)
    await client.disconnect()
    await phone_code_msg.reply("**- تم إنشاء جلسة تيرمكس {} 𝗭𝗧𝗵𝗼𝗻 بنجاح ..** \n\n**- يرجى التحقق من حافظـة حسابـك واخذ الكود!**\n\n**- لا تقم بمشاركـة هذا الكود مع احـد ⚠️**\n\n".format("تليثـون" if telethon else "بايروجـرام"))


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("**- تم إلغـاء العمليـة!**", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("**- جـاري إعادة تشغيل البـوت!**", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return True
    elif msg.text.startswith("/"):  # BOT COMMAND
        await msg.reply("**- تم إلغـاء عمليـة الاستخـراج!**", quote=True)
        return True
    else:
        return False


# @Client.on_message(filters.private & ~filters.forwarded & filters.command(['cancel', 'restart']))
# async def formalities(_, msg):
#     if "/cancel" in msg.text:
#         await msg.reply("membatalkan proses!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
#         return True
#     elif "/restart" in msg.text:
#         await msg.reply("memulai ulang bot!", quote=True, reply_markup=InlineKeyboardMarkup(Data.generate_button))
#         return True
#     else:
#         return False
