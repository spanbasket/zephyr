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

# İstediğin özel simgeli log kanal isimleriyle otomatik kurulum (!logkur)
@bot.command(name="logkur")
@commands.has_permissions(administrator=True)
async def logkur(ctx):
    guild = ctx.guild
    
    log_kanallari = [
        "🔮・giriş-çıkış-log",
        "💬・mesaj-log",
        "✨・isim-log",
        "💎・seviye-log",
        "⛔・ban-log",
        "🚷・jail-log",
        "📞・talep-log",
        "🛑・ceza-log",
        "🔐・mod-log",
        "🔗・davet-log",
        "🔊・ses-log",
        "😊・emoji-log"
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
# BAN KOMUTU VE BAN LOG SİSTEMİ
# ==========================================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=lambda: "Sebep belirtilmedi"):
    # Sebep string kontrolü
    if callable(reason):
        reason = "Sebep belirtilmedi"
        
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ **{member}** başarıyla sunucudan yasaklandı!")
        
        # ⛔・ban-log kanalına otomatik bildir
        log_kanal = discord.utils.get(ctx.guild.text_channels, name="⛔・ban-log")
        if log_kanal:
            embed = discord.Embed(title="⛔ Üye Yasaklandı (Ban)", color=discord.Color.dark_red())
            embed.add_field(name="Yasaklanan Kullanıcı", value=f"{member} (`{member.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
            embed.add_field(name="Sebep", value=reason, inline=True)
            await log_kanal.send(embed=embed)
            
    except Exception as e:
        await ctx.send(f"❌ Ban işlemi uygulanamadı! Hata: {e}")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için **Üyeleri Yasakla** yetkisine sahip olmalısın!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Lütfen yasaklanacak kişiyi etiketle! Örnek: `!ban @kullanici sebep`")

# ==========================================
# DİĞER LOG DİNLEYİCİLERİ
# ==========================================
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    
    log_kanal = discord.utils.get(message.guild.text_channels, name="💬・mesaj-log")
    if log_kanal:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
        embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
        embed.add_field(name="Silinen Mesaj", value=message.content or "*(Boş veya Sadece Görsel)*", inline=False)
        await log_kanal.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
        
    log_kanal = discord.utils.get(before.guild.text_channels, name="💬・mesaj-log")
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
