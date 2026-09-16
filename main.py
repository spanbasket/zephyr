import os
import sys
import discord
from discord.ext import commands
from keep_alive import keep_alive

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, reconnect=True)

@bot.event
async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash komutları senkronize edildi: {len(synced)} komut.")
    except Exception as e:
        print(e)

# Klasik ping komutu
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓 Bot aktif ve çalışıyor.")

# Slash komutlar
@bot.tree.command(name="start", description="Botun durumunu kontrol eder.")
async def slash_start(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 Bot aktif, komut sistemi çalışıyor!", ephemeral=True)

@bot.tree.command(name="restart", description="Botu tamamen yeniden başlatır.")
async def slash_restart(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Bot yeniden başlatılıyor...", ephemeral=True)
    os.execl(sys.executable, sys.executable, *sys.argv)

# Tek komutla otomatik log kanallarını kurma
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

# ==========================================
# ZEPHYR KENDİ LOG SİSTEMİ (Marpel yerine)
# ==========================================

# 1. Silinen Mesajları Loglama
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return  # Botların mesajlarını yok say
    
    # Sunucudaki "💬-mesaj-log" kanalını bul
    log_kanal = discord.utils.get(message.guild.text_channels, name="💬-mesaj-log")
    if log_kanal:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
        embed.add_field(name="Silinen Mesaj", value=message.content or "*(Boş veya Sadece Görsel)*", inline=False)
        await log_kanal.send(embed=embed)

# 2. Düzenlenen Mesajları Loglama
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
        
    log_kanal = discord.utils.get(before.guild.text_channels, name="💬-mesaj-log")
    if log_kanal:
        embed = discord.Embed(title="✏️ Mesaj Düzenlendi", color=discord.Color.orange())
        embed.add_field(name="Kullanıcı", value=before.author.mention, inline=True)
        embed.add_field(name="Kanal", value=before.channel.mention, inline=True)
        embed.add_field(name="Eski Hali", value=before.content or "*(Boş)*", inline=False)
        embed.add_field(name="Yeni Hali", value=after.content or "*(Boş)*", inline=False)
        await log_kanal.send(embed=embed)

# 7/24 aktif tutma servisi
keep_alive()

# Botu çalıştır
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
