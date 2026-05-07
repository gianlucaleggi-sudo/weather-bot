import cmb_full as cmb
import tkn

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

user_city = {}

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Scrivi la tua città (es: Roma)")

def save_city(update, context):
    chat_id = update.effective_chat.id
    city = update.message.text.strip()

    geo = cmb.geocoding(city)

    if not geo:
        context.bot.send_message(chat_id=chat_id, text="Città non trovata 😔")
        return

    user_city[chat_id] = geo

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Oraria", callback_data="oraria")],
        [InlineKeyboardButton("Giornaliera", callback_data="daily")]
    ])

    context.bot.send_message(chat_id=chat_id, text=f"Città impostata: {city} ✅", reply_markup=keyboard)

def callback_handler(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "oraria":
        oraria(query.message.chat.id, context)
    else:
        daily(query.message.chat.id, context)

def oraria(chat_id, context):
    if chat_id not in user_city:
        context.bot.send_message(chat_id=chat_id, text="Scrivi prima la città con /start")
        return

    geo = user_city[chat_id]

    ico = cmb.get_ico(geo["lat"], geo["lon"])

    forecast = [ico.diz_extrac_h(i) for i in range(3)]
    icons = ico.icon_h(forecast)

    for i in range(3):
        context.bot.send_message(chat_id=chat_id, text=cmb.txt_bot.textme_bot_h(i, forecast, icons))



def meteo(update, context):
    chat_id = update.effective_chat.id

    if not context.args:
        context.bot.send_message(chat_id=chat_id, text="Usa: /meteo Roma")
        return

    city = " ".join(context.args)
    geo = cmb.geocoding(city)

    if not geo:
        context.bot.send_message(chat_id=chat_id, text="Città non trovata 😔")
        return

    ico = cmb.get_ico(geo["lat"], geo["lon"])

    forecast = [ico.diz_extrac_h(i) for i in range(3)]
    icons = ico.icon_h(forecast)

    for i in range(3):
        context.bot.send_message(chat_id=chat_id, text=cmb.txt_bot.textme_bot_h(i, forecast, icons))

def daily(chat_id, context):
    if chat_id not in user_city:
        context.bot.send_message(chat_id=chat_id, text="Scrivi prima la città con /start")
        return

    geo = user_city[chat_id]
    ico = cmb.get_ico(geo["lat"], geo["lon"])
    forecast = [ico.diz_extrac_d(i) for i in range(1, 3)]

    # 🌙 icone luna
    lunar_icons = ico.lunar_phase(forecast)

    # 🌦 icone meteo
    weather_icons = ico.icon_d(forecast)

    for i, f in enumerate(forecast):
        wind_name = ico.wind_direction(f.get('wind_deg'))
        rain = f.get('rain', 0)

        txt = (
            f"📊 GIORNALIERA 📊\n\n"
            f"📅 {f['dt']}\n"
            f"{weather_icons[i]} {f['description'].capitalize()}\n\n"
            f"🌡 {f['max']}° / {f['min']}°\n"
            f"🌬 {f['wind_speed']} m/s - {wind_name}\n"
            f"🌧 {rain} mm\n\n"
            f"🌞 {f['sunrise']} → {f['sunset']}\n"
            f"🌙 {lunar_icons[i]}"
        )

        context.bot.send_message(chat_id=chat_id, text=txt)

def main():
    updater = Updater(token=tkn.tkn, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("meteo", meteo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_city))
    dp.add_handler(CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
