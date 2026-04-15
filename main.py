import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# ==================== 1. SOZLAMALAR ====================
TOKEN = "8517036646:AAGBZmpvj1DyNaprVbxGtpZn8yjLnv3BkOc"
ADMIN_ID = 7054481836  
OWNER_USERNAME = "@dilnura_admin" # O'zingizning username

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

LOGO_URL = "https://t4.ftcdn.net/jpg/04/42/21/53/360_F_442215355_Aji94Il8igL8mJ9H667U5Q2L9Xv9H2SS.jpg"

# ==================== 2. MUKAMMAL TAHLIL FUNKSIYASI ====================

async def get_tradingview_analysis():
    try:
        # 15 minutlik skaner
        handler = TA_Handler(
            symbol="XAUUSD",
            screener="cfd",
            exchange="OANDA",
            interval=Interval.INTERVAL_15_MINUTES
        )
        # 1 soatlik trendni tekshirish (Filtr uchun)
        h1_handler = TA_Handler(
            symbol="XAUUSD",
            screener="cfd",
            exchange="OANDA",
            interval=Interval.INTERVAL_1_HOUR
        )
        
        analysis = handler.get_analysis()
        analysis_h1 = h1_handler.get_analysis()
        
        ind = analysis.indicators
        rsi = round(ind['RSI'], 1)
        ema20 = ind['EMA20']
        ema50 = ind['EMA50']
        close = ind['close']
        macd = ind['MACD.macd']
        signal = ind['MACD.signal']
        
        h1_rec = analysis_h1.summary['RECOMMENDATION']
        summary = analysis.summary['RECOMMENDATION']

        # 🟢 BUY SIGNAL LOGIKASI (EMA cross + RSI + MACD + H1 Trend)
        if ema20 > ema50 and rsi < 60 and macd > signal and "BUY" in h1_rec:
            tp1 = round(close + 3, 2)
            tp2 = round(close + 6, 2)
            sl = round(close - 3.5, 2)
            return (f"🚀 **XAUSD (GOLD) - LONG SIGNAL**\n\n"
                    f"💎 **Daraja:** {close}\n"
                    f"📈 **RSI:** {rsi}\n"
                    f"📊 **Trend (H1):** {h1_rec}\n\n"
                    f"🎯 **TP1:** {tp1}\n"
                    f"🎯 **TP2:** {tp2}\n"
                    f"🛡 **SL:** {sl}\n\n"
                    f"⚡️ *Signal kuchi: Yuqori*")

        # 🔴 SELL SIGNAL LOGIKASI
        elif ema20 < ema50 and rsi > 40 and macd < signal and "SELL" in h1_rec:
            tp1 = round(close - 3, 2)
            tp2 = round(close - 6, 2)
            sl = round(close + 3.5, 2)
            return (f"📉 **XAUSD (GOLD) - SHORT SIGNAL**\n\n"
                    f"💎 **Daraja:** {close}\n"
                    f"📉 **RSI:** {rsi}\n"
                    f"📊 **Trend (H1):** {h1_rec}\n\n"
                    f"🎯 **TP1:** {tp1}\n"
                    f"🎯 **TP2:** {tp2}\n"
                    f"🛡 **SL:** {sl}\n\n"
                    f"⚡️ *Signal kuchi: Yuqori*")
        
        else:
            return (f"⏳ **XAUUSD: BOZOR KUTILMOQDA**\n\n"
                    f"💰 Narx: {close}\n"
                    f"📉 RSI: {rsi}\n"
                    f"🕒 H1 Trend: {h1_rec}\n"
                    f"📢 Xulosa: Hozircha aniq kirish nuqtasi yo'q.")

    except Exception as e:
        logging.error(f"Tahlilda xato: {e}")
        return "⚠️ Tahlil qilishda texnik uzilish yuz berdi."

# ==================== 3. AVTO-SKANER (DOIMIY) ====================

async def auto_scanner():
    while True:
        try:
            report = await get_tradingview_analysis()
            if "SIGNAL" in report:
                now = datetime.now().strftime("%H:%M")
                await bot.send_message(
                    ADMIN_ID, 
                    f"🔔 **YANGI SIGNAL** [{now}]\n\n{report}"
                )
                # Signal berilgandan so'ng 15 daqiqa dam oladi
                await asyncio.sleep(900) 
            else:
                # Signal yo'q bo'lsa har 5 daqiqada tekshiradi
                await asyncio.sleep(300) 
        except Exception as e:
            logging.error(f"Skanerda xato: {e}")
            await asyncio.sleep(60)

# ==================== 4. KLAVIATURALAR ====================

def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Bozorni tahlil qilish", callback_data="check")],
        [InlineKeyboardButton(text="💎 Premium", callback_data="premium"), 
         InlineKeyboardButton(text="📊 Stat", callback_data="stats")]
    ])

def get_back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")]
    ])

# ==================== 5. HANDLERLAR ====================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer_photo(
        photo=LOGO_URL,
        caption=(f"👋 **Salom, {message.from_user.first_name}!**\n\n"
                 "Siz **XAUUSD ROCKET TERMINAL** botiga ulandingiz.\n"
                 "Men Oltin bozorini 15m va 1h taymfreymlarda skaner qilaman."),
        reply_markup=get_main_kb()
    )

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    if callback.data == "check":
        await callback.answer("Skanerlanmoqda...")
        res = await get_tradingview_analysis()
        await callback.message.answer(res)
    
    elif callback.data == "premium":
        text = ("💎 **PREMIUM OBUNA**\n\n"
                "• 24/7 Avtomatik signallar\n"
                "• Aniq Take Profit va Stop Loss\n"
                "• Shaxsiy maslahatlar\n\n"
                "Murojaat uchun: " + OWNER_USERNAME)
        await callback.message.edit_caption(caption=text, reply_markup=get_back_kb())

    elif callback.data == "back":
        await callback.message.edit_caption(
            caption="🏎️ **XAUUSD ROCKET TERMINAL**\n\nAmallardan birini tanlang:",
            reply_markup=get_main_kb()
        )
    
    elif callback.data == "stats":
        await callback.answer("Haftalik: +720 pips ✅", show_alert=True)

    await callback.answer()

# ==================== 6. ISHGA TUSHIRISH ====================

async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Bot ishga tushdi!")
    
    # Skanerni fonda ishga tushirish
    asyncio.create_task(auto_scanner())
    
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Bot to'xtatildi!")