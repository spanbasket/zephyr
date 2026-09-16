import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Bot ayarları (Message content intent açık olmalı)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓 Bot aktif ve çalışıyor.")

# Tek komutla otomatik log kanallarını kurma sistemi
@bot.command(name="logkur")
@commands.has_permissions(administrator=True)
async def logkur(ctx):
    guild = ctx.guild
    
    # Kurulacak log kanallarının listesi
    log_kanallari = [
        "🔮-giriş-çıkış-log",
        "💬-mesaj-log",
        "✨-isim-log",
        "💎-seviye-log",
        "⛔-ban-log",
        "🚷-jail-log",
        "📞-talep-log",
        "🛑-ceza-log",
        "🔐-mod-log",
        "🔗-davet-log",
        "🔊-ses-log",
        "😊-emoji-log"
    ]
    
    # Loglar için özel bir kategori oluştur
    kategori = await guild.create_category("📊 | LOG KANALLARI")
    
    kurulanlar = 0
    for kanal_adi in log_kanallari:
        # Normal üyelerin görmemesi için gizli (özel) kanal ayarları
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        await guild.create_text_channel(kanal_adi, category=kategori, overwrites=overwrites)
        kurulanlar += 1
        
    await ctx.send(f"✅ Başarıyla **{kurulanlar}** adet log kanalı ve kategorisi oluşturuldu! (Kanalları sadece yöneticiler görebilir)")

@logkur.error
async def logkur_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın!")

# 7/24 aktif tutma servisi
keep_alive()

# Botu çalıştır
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
