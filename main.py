import os
import sys
import discord
from discord.ext import commands
import aiohttp
from keep_alive import keep_alive

# Bot ayarları (Varsayılan help komutunu kapattık, her şey prefixli)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None, reconnect=True)

@bot.event
async def on_ready():
    print(f"Bot olarak giriş yapıldı: {bot.user}")

# ==========================================
# YARDIM & TEMEL KOMUTLAR
# ==========================================

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 Gecikme: {round(bot.latency * 1000)}ms")

@bot.command(name="help")
async def cmd_help(ctx):
    embed = discord.Embed(
        title="🤖 Zephyr Komut Merkezi",
        description="Marpel'in yerini alan tam yetkili prefix botunuzun komut listesi:",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="🛡️ Moderasyon & Yönetim",
        value=(
            "`!ban @üye sebep` - Üyeyi yasaklar.\n"
            "`!unban [ID]` - Üyenin yasağını kaldırır.\n"
            "`!kick @üye sebep` - Üyeyi atar.\n"
            "`!mute @üye [dk]` - Üyeyi susturur.\n"
            "`!sil [sayı]` - Toplu mesaj siler.\n"
            "`!nick @üye [isim]` - Kullanıcı adını değiştirir.\n"
            "`!lock / !unlock` - Kanalı kilitler / açar.\n"
            "`!logkur` - Tüm log kanallarını otomatik kurar."
        ),
        inline=False
    )
    embed.add_field(
        name="📊 Bilgi & Eğlence",
        value=(
            "`!avatar [@üye]` - Profil fotoğrafını gösterir.\n"
            "`!bitcoin` - Güncel kripto kurlarını gösterir.\n"
            "`!depremler` - Son deprem listesini gösterir.\n"
            "`!start` - Botun durumunu kontrol eder.\n"
            "`!restart` - Botu yeniden başlatır."
        ),
        inline=False
    )
    embed.set_footer(text="Zephyr Bot v2.0 - Tamamen Prefix Modu!")
    await ctx.send(embed=embed)

@bot.command(name="start")
async def cmd_start(ctx):
    await ctx.send("🚀 Bot aktif, sistemler kusursuz çalışıyor!")

@bot.command(name="restart")
@commands.has_permissions(administrator=True)
async def cmd_restart(ctx):
    await ctx.send("🔄 Bot yeniden başlatılıyor...")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.command(name="avatar")
async def cmd_avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name} adlı kişinin avatarı", color=discord.Color.blurple())
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="bitcoin")
async def cmd_bitcoin(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,try") as resp:
            if resp.status == 200:
                data = await resp.json()
                btc_usd = data['bitcoin']['usd']
                btc_try = data['bitcoin']['try']
                eth_usd = data['ethereum']['usd']
                eth_try = data['ethereum']['try']
                
                embed = discord.Embed(title="🪙 Güncel Kripto Kurları", color=discord.Color.gold())
                embed.add_field(name="Bitcoin (BTC)", value=f"💵 ${btc_usd:,.2f}\n🇹🇷 ₺{btc_try:,.2f}", inline=False)
                embed.add_field(name="Ethereum (ETH)", value=f"💵 ${eth_usd:,.2f}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Kurlar şu an alınamıyor.")

@bot.command(name="depremler")
async def cmd_depremler(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.orhanaydogdu.com.tr/deprem/live.php?limit=5") as resp:
            if resp.status == 200:
                res = await resp.json()
                depremler = res.get("result", [])
                
                embed = discord.Embed(title="🚨 Son Depremler (Türkiye)", color=discord.Color.red())
                for dep in depremler:
                    yer = dep.get("title")
                    buyukluk = dep.get("mag")
                    tarih = dep.get("date")
                    embed.add_field(name=f"Büyüklük: {buyukluk}", value=f"📍 **Yer:** {yer}\n📅 **Tarih:** {tarih}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Deprem verileri şu an çekilemiyor.")

# ==========================================
# OTOMATİK LOG KURULUMU (!logkur)
# ==========================================
@bot.command(name="logkur")
@commands.has_permissions(administrator=True)
async def logkur(ctx):
    guild = ctx.guild
    log_kanallari = [
        "🔮・giriş-çıkış-log", "💬・mesaj-log", "✨・isim-log", 
        "💎・seviye-log", "⛔・ban-log", "🚷・jail-log", 
        "📞・talep-log", "🛑・ceza-log", "🔐・mod-log", 
        "🔗・davet-log", "🔊・ses-log", "😊・emoji-log"
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
        await ctx.send("❌ Bu komut için Yönetici yetkin olmalı!")

# ==========================================
# MODERASYON KOMUTLARI
# ==========================================

@bot.command(name="sil")
@commands.has_permissions(manage_messages=True)
async def cmd_sil(ctx, limit: int):
    if limit < 1:
        return
    deleted = await ctx.channel.purge(limit=limit + 1)
    msg = await ctx.send(f"🗑️ **{len(deleted) - 1}** adet mesaj silindi.")
    await msg.delete(delay=3)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def cmd_ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.ban(reason=reason)
    await ctx.send(f"✅ **{member}** yasaklandı.")
    log_kanal = discord.utils.get(ctx.guild.text_channels, name="⛔・ban-log")
    if log_kanal:
        embed = discord.Embed(title="⛔ Üye Yasaklandı", color=discord.Color.dark_red())
        embed.add_field(name="Kullanıcı", value=str(member), inline=False)
        embed.add_field(name="Sebep", value=reason, inline=True)
        await log_kanal.send(embed=embed)

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def cmd_unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ **{user}** yasağı kaldırıldı.")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def cmd_kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    await member.kick(reason=reason)
    await ctx.send(f"✅ **{member}** atıldı.")
    log_kanal = discord.utils.get(ctx.guild.text_channels, name="🛑・ceza-log")
    if log_kanal:
        embed = discord.Embed(title="👢 Üye Atıldı", color=discord.Color.orange())
        embed.add_field(name="Kullanıcı", value=str(member), inline=False)
        embed.add_field(name="Sebep", value=reason, inline=True)
        await log_kanal.send(embed=embed)

@bot.command(name="mute")
@commands.has_permissions(moderate_members=True)
async def cmd_mute(ctx, member: discord.Member, dakika: int, *, reason="Sebep yok"):
    import datetime
    delta = datetime.timedelta(minutes=dakika)
    await member.timeout(delta, reason=reason)
    await ctx.send(f"🔇 **{member}** {dakika} dakika süreyle susturuldu.")

@bot.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def cmd_nick(ctx, member: discord.Member, *, yeni_isim=None):
    await member.edit(nick=yeni_isim)
    await ctx.send(f"✅ İsim güncellendi.")

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def cmd_lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal kilitlendi.")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def cmd_unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal kilidi açıldı.")

# ==========================================
# LOG DİNLEYİCİLERİ (EVENTS)
# ==========================================

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_kanal = discord.utils.get(message.guild.text_channels, name="💬・mesaj-log")
    if log_kanal:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Kullanıcı", value=message.author.mention, inline=True)
        embed.add_field(name="Silinen", value=message.content or "*(Görsel/Boş)*", inline=False)
        await log_kanal.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    log_kanal = discord.utils.get(before.guild.text_channels, name="💬・mesaj-log")
    if log_kanal:
        embed = discord.Embed(title="✏️ Mesaj Düzenlendi", color=discord.Color.orange())
        embed.add_field(name="Eski", value=before.content or "*(Boş)*", inline=False)
        embed.add_field(name="Yeni", value=after.content or "*(Boş)*", inline=False)
        await log_kanal.send(embed=embed)

@bot.event
async def on_member_join(member):
    log_kanal = discord.utils.get(member.guild.text_channels, name="🔮・giriş-çıkış-log")
    if log_kanal:
        embed = discord.Embed(title="📥 Üye Katıldı", description=f"{member.mention} sunucuya katıldı!", color=discord.Color.green())
        await log_kanal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_kanal = discord.utils.get(member.guild.text_channels, name="🔮・giriş-çıkış-log")
    if log_kanal:
        embed = discord.Embed(title="📤 Üye Ayrıldı", description=f"{member.mention} sunucudan ayrıldı.", color=discord.Color.dark_red())
        await log_kanal.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    log_kanal = discord.utils.get(member.guild.text_channels, name="🔊・ses-log")
    if not log_kanal:
        return
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(title="🔊 Sese Katıldı", description=f"{member.mention} -> **{after.channel.name}** kanalına girdi.", color=discord.Color.blurple())
        await log_kanal.send(embed=embed)
    elif before.channel is not None and after.channel is None:
        embed = discord.Embed(title="🔇 Sesden Ayrıldı", description=f"{member.mention} ses kanalından çıktı.", color=discord.Color.dark_grey())
        await log_kanal.send(embed=embed)

# 7/24 Aktif Tutma
keep_alive()

TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
