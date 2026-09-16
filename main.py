import os
import sys
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Bot ayarları (Intent'ler tam yetkiyle açıldı)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

# Reconnect özelliğini güçlendirilmiş bot tanımı
bot = commands.Bot(command_prefix="!", intents=intents, reconnect=True)

@bot.event
async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")
    # Bot açıldığında tüm sunucularda senkronizasyon yapabilmesi için
    try:
        synced = await bot.tree.sync()
        print(f"Slash komutları senkronize edildi: {len(synced)} komut.")
    except Exception as e:
        print(e)

# Klasik ping komutu
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓 Bot aktif ve çalışıyor.")

# Slash komut olarak /start (Botun aktif olduğunu ve çalıştığını test eder)
@bot.tree.command(name="start", description="Botun durumunu kontrol eder.")
async def slash_start(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 Bot aktif, komut sistemi çalışıyor!", ephemeral=True)

# Slash komut olarak /restart (Botu yeniden başlatır - Sadece bot sahibine özel yapılabilir)
@bot.tree.command(name="restart", description="Botu tamamen yeniden başlatır.")
async def slash_restart(interaction: discord.Interaction):
    # İsteğe bağlı: Sadece kendi ID'ni yazarak güvenli hale getirebilirsin
    # if interaction.user.id != KENDI_DISCORD_ID_NEDIR:
    #     await interaction.response.send_message("Bu komutu sadece bot sahibi kullanabilir!", ephemeral=True)
    #     return

    await interaction.response.send_message("🔄 Bot yeniden başlatılıyor...", ephemeral=True)
    print("Yeniden başlatma komutu algılandı, sistem kapatılıyor...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Tek komutla otomatik log kanallarını kurma sistemi (!logkur)
@bot.command(name="logkur")
@commands.has_permissions(administrator=True)
async def logkur(ctx):
    guild = ctx.guild
    
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
    
    kategori = await guild.create_category("📊 | LOG KANALLARI")
    
    kurulanlar = 0
    for kanal_adi in log_kanallari:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        await guild.create_text_channel(kanal_adi, category=kategori, overwrites=overwrites)
        kurulanlar += 1
        
    await ctx.send(f"✅ Başarıyla **{kurulanlar}** adet log kanalı ve kategorisi oluşturuldu!")

@logkur.error
async def logkur_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın!")

# 7/24 aktif tutma servisi
keep_alive()

# Botu çalıştır
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
