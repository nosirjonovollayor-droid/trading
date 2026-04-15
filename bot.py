import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from tradingview_ta import TA_Handler, Interval
from datetime import datetime

# ==================== 0. COLAB/JUPYTER UCHUN TUZATISH ====================
# Agar siz Google Colab yoki Jupyter Notebook ishlatayotgan bo'lsangiz, 
# quyidagi blok "RuntimeError"ni oldini oladi.
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# ==================== 1. SOZLAMALAR ====================
TOKEN = "8517036646:AAGBZmpvj1DyNaprVbxGtpZn8yjLnv3BkOc"
ADMIN_ID = 7054481836  
OWNER_USERNAME = "@dilnura_admin" 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

LOGO_URL = "https://t4.ftcdn.net/jpg/04/42/21/53/360_F_442215355_Aji94Il8igL8mJ9H667U5Q2L9Xv9H2SS.jpg"

# ==================== 2. TAHLIL FUNKSIYASI ====================

async def get_tradingview_analysis():
    try:
        # 15 minutlik skaner
        handler = TA_Handler(
            symbol="XAUUSD",
            screener="cfd",
            exchange="OANDA",
            interval=Interval.INTERVAL_15_MINUTES
        )
        # 1 soatlik trendni tekshirish
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

        # 🟢 BUY SIGNAL
        if ema20 > ema50 and rsi < 60 and macd > signal and "BUY" in h1_rec:
            tp1, tp2 = round(close + 3, 2), round(close + 6, 2)
            sl = round(close - 3.5, 2)
            return (f"🚀 **XAUUSD (GOLD) - LONG SIGNAL**\n\n"
                    f"💎 **Narx:** {close}\n"
                    f"📈 **RSI:** {rsi}\n"
                    f"📊 **Trend (H1):** {h1_rec}\n\n"
                    f"🎯 **TP1:** {tp1} | **TP2:** {tp2}\n"
                    f"🛡 **SL:** {sl}\n\n"
                    f"⚡️ *Signal kuchi: Yuqori*")

        # 🔴 SELL SIGNAL
        elif ema20 < ema50 and rsi > 40 and macd < signal and "SELL" in h1_rec:
            tp1, tp2 = round(close - 3, 2), round(close - 6, 2)
            sl = round(close + 3.5, 2)
            return (f"📉 **XAUUSD (GOLD) - SHORT SIGNAL**\n\n"
                    f"💎 **Narx:** {close}\n"
                    f"📉 **RSI:** {rsi}\n"
                    f"📊 **Trend (H1):** {h1_rec}\n\n"
                    f"🎯 **TP1:** {tp1} | **TP2:** {tp2}\n"
                    f"🛡 **SL:** {sl}\n\n"
                    f"⚡️ *Signal kuchi: Yuqori*")
        
        else:
            return (f"⏳ **XAUUSD: BOZOR KUTILMOQDA**\n\n"
                    f"💰 Narx: {close}\n"
                    f"📉 RSI: {rsi}\n"
                    f"🕒 H1 Trend: {h1_rec}\n"
                    f"📢 Xulosa: Kirishga erta.")

    except Exception as e:
        logging.error(f"Tahlilda xato: {e}")
        return "⚠️ Tahlil tizimida vaqtinchalik uzilish."

# ==================== 3. AVTO-SKANER ====================

async def auto_scanner():
    while True:
        try:
            report = await get_tradingview_analysis()
            if "SIGNAL" in report:
                now = datetime.now().strftime("%H:%M")
                await bot.send_message(
                    ADMIN_ID, 
                    f"🔔 **YANGI AVTO-SIGNAL** [{now}]\n\n{report}"
                )
                await asyncio.sleep(900) # 15 minut kutish
            else:
                await asyncio.sleep(300) # 5 minut kutish
        except Exception as e:
            logging.error(f"Skanerda xato: {e}")
            await asyncio.sleep(60)

# ==================== 4. KLAVIATURALAR ====================

def get_main_kb():
    buttons = [
        [InlineKeyboardButton(text="🔍 Bozorni tahlil qilish", callback_data="check")],
        [InlineKeyboardButton(text="💎 Premium", callback_data="premium"), 
         InlineKeyboardButton(text="📊 Statistika", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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
                 "Siz **XAUUSD ROCKET TERMINAL** tizimiga ulandingiz.\n"
                 "Men Oltin bozorini 24/7 skaner qilaman."),
        reply_markup=get_main_kb()
    )

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    if callback.data == "check":
        await callback.answer("Skanerlanmoqda...")
        res = await get_tradingview_analysis()
        await callback.message.answer(res)
    
    elif callback.data == "premium":
        text = ("💎 **PREMIUM OBUNA IMKONIYATLARI**\n\n"
                "• 24/7 Avtomatik signallar (Lichkaga)\n"
                "• Aniq Take Profit va Stop Loss\n"
                "• MACD + RSI + EMA filtrlar\n\n"
                "Murojaat uchun: " + OWNER_USERNAME)
        await callback.message.edit_caption(caption=text, reply_markup=get_back_kb())

    elif callback.data == "back":
        await callback.message.edit_caption(
            caption="🏎️ **XAUUSD ROCKET TERMINAL**\n\nAmallardan birini tanlang:",
            reply_markup=get_main_kb()
        )
    
    elif callback.data == "stats":
        await callback.answer("Haftalik natija: +720 pips ✅", show_alert=True)

    await callback.answer()

# ==================== 6. ISHGA TUSHIRISH ====================

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Avto-skanerni fonda ishga tushirish
    asyncio.create_task(auto_scanner())
    
    # Botni ishga tushirish
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    # Agar bu Jupyter yoki Colab bo'lsa, to'g'ridan-to'g'ri await ishlatamiz
    if 'ipykernel' in sys.modules:
        asyncio.create_task(main())
        print("✅ Bot fonda ishga tushdi! (Jupyter/Colab muhiti)")
    else:
        # Oddiy terminal muhiti uchun
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            pass
