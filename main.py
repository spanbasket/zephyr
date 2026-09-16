import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Botun yetkilerini (intents) ayarlıyoruz
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} olarak giriş yapıldı!")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓 Bot aktif ve çalışıyor.")

# Flask sunucusunu başlat (Render'ın botu uyutmaması için)
keep_alive()

# Botu güvenli bir şekilde token ile çalıştır
TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("HATA: DISCORD_TOKEN bulunamadı! Lütfen ortam değişkenlerini kontrol edin.")