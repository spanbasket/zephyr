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
# GELİŞMİŞ MODERASYON KOMUTLARI
# ==========================================

# 1. !sil Komutu (Toplu Mesaj Silme)
@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def cmd_sil(ctx, limit: int):
    if limit < 1:
        await ctx.send("❌ En az 1 mesaj silebilirsin!", delete_after=5)
        return
    
    try:
        # Komut mesajının kendisini de dahil ederek belirtilen sayı kadar mesajı siler
        deleted = await ctx.channel.purge(limit=limit + 1)
        msg = await ctx.send(f"🗑️ Başarıyla **{len(deleted) - 1}** adet mesaj temizlendi!")
        await msg.delete(by_pass_perms=True, delay=4) # 4 saniye sonra bildirim mesajını da siler
    except Exception as e:
        await ctx.send(f"❌ Mesajlar silinemezken bir hata oluştu: {e}")

@cmd_sil.error
async def cmd_sil_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komut için **Mesajları Yönet** yetkin olmalı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik kullanım! Örnek: `!sil 10`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Lütfen geçerli bir sayı yaz! Örnek: `!sil 5`")

# 2. !ban Komutu
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def cmd_ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ **{member}** başarıyla sunucudan yasaklandı!")
        
        log_kanal = discord.utils.get(ctx.guild.text_channels, name="⛔・ban-log")
        if log_kanal:
            embed = discord.Embed(title="⛔ Üye Yasaklandı (Ban)", color=discord.Color.dark_red())
            embed.add_field(name="Yasaklanan", value=f"{member} (`{member.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
            embed.add_field(name="Sebep", value=reason, inline=True)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ İşlem başarısız! Hata: {e}")

@cmd_ban.error
async def cmd_ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komut için **Üyeleri Yasakla** yetkin olmalı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik kullanım! Örnek: `!ban @kullanici sebep`")

# 3. !unban Komutu (Yasak Kaldırma)
@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def cmd_unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ **{user}** adlı kullanıcının yasağı kaldırıldı!")
        
        log_kanal = discord.utils.get(ctx.guild.text_channels, name="⛔・ban-log")
        if log_kanal:
            embed = discord.Embed(title="🟢 Üyenin Yasağı Kaldırıldı (Unban)", color=discord.Color.green())
            embed.add_field(name="Kullanıcı", value=f"{user} (`{user.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Kullanıcıun yasağı kaldırılamadı! (ID'yi yanlış yazmış olabilirsin): {e}")

@cmd_unban.error
async def cmd_unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komut için **Üyeleri Yasakla** yetkin olmalı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik kullanım! Örnek: `!unban 123456789012345678`")

# 4. !kick Komutu
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def cmd_kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ **{member}** sunucudan atıldı!")
        
        log_kanal = discord.utils.get(ctx.guild.text_channels, name="🛑・ceza-log")
        if log_kanal:
            embed = discord.Embed(title="👢 Üye Sunucudan Atıldı (Kick)", color=discord.Color.orange())
            embed.add_field(name="Atılan Üye", value=f"{member} (`{member.id}`)", inline=False)
            embed.add_field(name="Yetkili", value=ctx.author.mention, inline=True)
            embed.add_field(name="Sebep", value=reason, inline=True)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ İşlem başarısız! Hata: {e}")

@cmd_kick.error
async def cmd_kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komut için **Üyeleri At** yetkin olmalı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik kullanım! Örnek: `!kick @kullanici sebep`")

# 5. !nick Komutu
@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def cmd_nick(ctx, member: discord.Member, *, yeni_isim=None):
    try:
        eski_isim = member.display_name
        await member.edit(nick=yeni_isim)
        await ctx.send(f"✅ **{member.name}** adlı üyenin ismi güncellendi!")
        
        log_kanal = discord.utils.get(ctx.guild.text_channels, name="✨・isim-log")
        if log_kanal:
            embed = discord.Embed(title="✨ Kullanıcı İsmi Değiştirildi", color=discord.Color.blue())
            embed.add_field(name="Kullanıcı", value=member.mention, inline=False)
            embed.add_field(name="Eski İsim", value=eski_isim, inline=True)
            embed.add_field(name="Yeni İsim", value=yeni_isim or "*(Orijinal İsim)*", inline=True)
            embed.add_field(name="Yetkili", value=ctx.author.mention, inline=False)
            await log_kanal.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ İsim değiştirilemedi! (Botun yetkisi yetmiyor veya hedef kişi sunucu sahibi)")

@cmd_nick.error
async def cmd_nick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komut için **Kullanıcı Adlarını Yönet** yetkin olmalı!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Eksik kullanım! Örnek: `!nick @kullanici YeniIsim`")

# 6. !lock ve !unlock Komutları (Kanalı Kilitleme / Açma)
@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def cmd_lock(ctx):
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Bu kanal üyelerin mesaj yazmasına **kapatıldı**.")
    except Exception as e:
        await ctx.send(f"❌ Kanal kilitlenemedi: {e}")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def cmd_unlock(ctx):
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Bu kanal üyelerin mesaj yazmasına **açıldı**.")
    except Exception as e:
        await ctx.send(f"❌ Kanal kilidi açılamadı: {e}")

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
