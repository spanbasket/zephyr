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

# /start Komutu
@bot.tree.command(name="start", description="Botun durumunu kontrol eder.")
async def slash_start(interaction: discord.Interaction):
    await interaction.response.send_message("🚀 Bot aktif, komut sistemi çalışıyor!", ephemeral=True)

# /restart Komutu
@bot.tree.command(name="restart", description="Botu tamamen yeniden başlatır.")
async def slash_restart(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Bot yeniden başlatılıyor...", ephemeral=True)
    os.execl(sys.executable, sys.executable, *sys.argv)

# Otomatik log kanalları kurma (!logkur)
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
# TAB DESTEKLİ SLASH MODERASYON KOMUTLARI
# ==========================================

# 1. /ban Komutu (Tab ile üye seçmeli)
@bot.tree.command(name="ban", description="Bir üyeyi sunucudan yasaklar.")
@discord.app_commands.describe(uye="Yasaklanacak üye", sebep="Yasaklanma sebebi")
async def slash_ban(interaction: discord.Interaction, uye: discord.Member, sebep: str = "Sebep belirtilmedi"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Bu komutu kullanmak için **Üyeleri Yasakla** yetkin olmalı!", ephemeral=True)
        return

    try:
        await uye.ban(reason=sebep)
        await interaction.response.send_message(f"✅ **{uye}** başarıyla yasaklandı!")
        
        # Ban log kanalına bildir
        log_kanal = discord.utils.get(interaction.guild.text_channels, name="⛔・ban-log")
        if log_kanal:
            embed = discord.Embed(title="⛔ Üye Yasaklandı (Ban)", color=discord.Color.dark_red())
            embed.add_field(name="Yasaklanan", value=f"{uye} (`{uye.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
            embed.add_field(name="Sebep", value=sebep, inline=True)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ İşlem başarısız! Hata: {e}", ephemeral=True)

# 2. /kick Komutu (Tab ile üye seçmeli)
@bot.tree.command(name="kick", description="Bir üyeyi sunucudan atar.")
@discord.app_commands.describe(uye="Atılacak üye", sebep="Atılma sebebi")
async def slash_kick(interaction: discord.Interaction, uye: discord.Member, sebep: str = "Sebep belirtilmedi"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Bu komutu kullanmak için **Üyeleri At** yetkin olmalı!", ephemeral=True)
        return

    try:
        await uye.kick(reason=sebep)
        await interaction.response.send_message(f"✅ **{uye}** sunucudan atıldı!")
        
        # Ceza/Mod log kanalına bildir
        log_kanal = discord.utils.get(interaction.guild.text_channels, name="🛑・ceza-log")
        if log_kanal:
            embed = discord.Embed(title="👢 Üye Sunucudan Atıldı (Kick)", color=discord.Color.orange())
            embed.add_field(name="Atılan Üye", value=f"{uye} (`{uye.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
            embed.add_field(name="Sebep", value=sebep, inline=True)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ İşlem başarısız! Hata: {e}", ephemeral=True)

# 3. /nick Komutu (Tab ile üye seçmeli ve yeni isim verme)
@bot.tree.command(name="nick", description="Bir üyenin sunucu içindeki takma adını değiştirir.")
@discord.app_commands.describe(uye="İsmi değiştirilecek üye", yeni_isim="Yeni takma ad (boş bırakılırsa sıfırlanır)")
async def slash_nick(interaction: discord.Interaction, uye: discord.Member, yeni_isim: str = None):
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message("❌ Bu komutu kullanmak için **Kullanıcı Adlarını Yönet** yetkin olmalı!", ephemeral=True)
        return

    try:
        eski_isim = uye.display_name
        await uye.edit(nick=yeni_isim)
        await interaction.response.send_message(f"✅ **{uye.name}** adlı üyenin ismi başarıyla güncellendi!")
        
        # İsim log kanalına bildir
        log_kanal = discord.utils.get(interaction.guild.text_channels, name="✨・isim-log")
        if log_kanal:
            embed = discord.Embed(title="✨ Kullanıcı İsmi Değiştirildi", color=discord.Color.blue())
            embed.add_field(name="Kullanıcı", value=uye.mention, inline=False)
            embed.add_field(name="Eski İsim", value=eski_isim, inline=True)
            embed.add_field(name="Yeni İsim", value=yeni_isim or "*(Orijinal İsim)*", inline=True)
            embed.add_field(name="Yetkili", value=interaction.user.mention, inline=False)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ İsim değiştirilemedi! (Botun yetkisi yetmiyor olabilir ya da hedef kişi botun sahibinden üst rütbede)", ephemeral=True)

# ==========================================
# MESAJ LOG DİNLEYİCİLERİ
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
