
import json
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "MASUKKAN_TOKEN_BOT_KAMU"

DATABASE = "database.json"

def load_db():
    try:
        with open(DATABASE, "r") as f:
            return json.load(f)
    except:
        return {
            "laporan": {},
            "menu": {
                "barista": {
                    "harga_jual": 12000,
                    "modal": 7500
                },
                "americano": {
                    "harga_jual": 12000,
                    "modal": 4000
                },
                "latte": {
                    "harga_jual": 14000,
                    "modal": 9000
                }
            }
        }

def save_db(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

def rupiah(angka):
    return f"Rp{angka:,.0f}".replace(",", ".")

keyboard = [
    ["☕ Menu", "📊 Laporan"],
    ["🔥 Terlaris"]
]

markup = ReplyKeyboardMarkup(
    keyboard,
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    teks = '''
☕ CAFE POS PREMIUM VVIP

Bot aktif ✅

Perintah:
jual barista 2
jual americano 1
jual latte 3
'''

    await update.message.reply_text(
        teks,
        reply_markup=markup
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    if text == "☕ menu".lower():

        teks = "☕ MENU CAFE\n\n"

        for nama, data in db["menu"].items():

            teks += (
                f"• {nama.upper()}\n"
                f"Harga : {rupiah(data['harga_jual'])}\n\n"
            )

        await update.message.reply_text(teks)

    elif text == "📊 laporan".lower():

        hari = datetime.now().strftime("%Y-%m-%d")

        laporan = db["laporan"].get(hari)

        if not laporan:

            await update.message.reply_text(
                "Belum ada penjualan."
            )

            return

        detail = ""

        for nama, jumlah in laporan["detail"].items():
            detail += f"• {nama} : {jumlah} cup\n"

        teks = f'''
📊 LAPORAN HARI INI

📅 {hari}

{detail}

💰 Omzet : {rupiah(laporan['omzet'])}
📦 Modal : {rupiah(laporan['modal'])}
🟢 Profit : {rupiah(laporan['profit'])}
'''

        await update.message.reply_text(teks)

    elif text == "🔥 terlaris".lower():

        ranking = {}

        for tanggal, laporan in db["laporan"].items():

            for menu, jumlah in laporan["detail"].items():
                ranking[menu] = ranking.get(menu, 0) + jumlah

        if not ranking:
            await update.message.reply_text(
                "Belum ada data."
            )
            return

        urut = sorted(
            ranking.items(),
            key=lambda x: x[1],
            reverse=True
        )

        teks = "🔥 MENU TERLARIS\n\n"

        for i, item in enumerate(urut, start=1):
            teks += f"{i}. {item[0]} = {item[1]} cup\n"

        await update.message.reply_text(teks)

    elif text.startswith("jual"):

        try:

            pecah = text.split()

            nama = pecah[1]
            jumlah = int(pecah[2])

            if nama not in db["menu"]:

                await update.message.reply_text(
                    "Menu tidak ditemukan"
                )

                return

            hari = datetime.now().strftime("%Y-%m-%d")

            if hari not in db["laporan"]:

                db["laporan"][hari] = {
                    "omzet": 0,
                    "modal": 0,
                    "profit": 0,
                    "detail": {}
                }

            harga = db["menu"][nama]["harga_jual"]
            modal = db["menu"][nama]["modal"]

            omzet = harga * jumlah
            total_modal = modal * jumlah
            profit = omzet - total_modal

            db["laporan"][hari]["omzet"] += omzet
            db["laporan"][hari]["modal"] += total_modal
            db["laporan"][hari]["profit"] += profit

            if nama not in db["laporan"][hari]["detail"]:
                db["laporan"][hari]["detail"][nama] = 0

            db["laporan"][hari]["detail"][nama] += jumlah

            save_db(db)

            teks = f'''
✅ TRANSAKSI BERHASIL

☕ Menu : {nama}
🧾 Jumlah : {jumlah}

💰 Omzet : {rupiah(omzet)}
🟢 Profit : {rupiah(profit)}
'''

            await update.message.reply_text(teks)

        except:

            await update.message.reply_text(
                "Contoh:\njual barista 2"
            )

    else:

        await update.message.reply_text(
            "Perintah tidak dikenal"
        )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

print("☕ BOT CAFE BERJALAN...")
app.run_polling()
