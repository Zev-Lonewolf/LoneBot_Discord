import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Carregar variáveis de ambiente
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

guild_languages = {}  # Dicionário para armazenar a linguagem de cada servidor
language_set = set()  # Servidores que já escolheram o idioma

def create_language_embed():
    embed = discord.Embed(
        title="🌐 Choose your language / Escolha seu idioma",
        description=(
            "🇺🇸 React with this emoji for English\n"
            "🇧🇷 Reaja com este emoji para Português (BR)"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="🔍 Detecting roles automatically... / Detectando cargos automaticamente...")
    return embed

def create_intro_embed(lang):
    if lang == "ptbr":
        embed = discord.Embed(
            title="👋Olá! Eu sou o LoneBot!",
            description=(
                "Sou um bot modular e versátil que ajuda a organizar modos personalizados no seu servidor. Me diz, o que você quer fazer agora?\n\n"
                "Comandos principais:\n"
                "```text\n!setup → iniciar configuração de modos\n!idioma → ativa a seleção de idiomas\n```\n\n"
                "Site: Em breve..."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="🔍 Confirmando cargos para evitar erros...")
    else:
        embed = discord.Embed(
            title="👋Hello! I'm LoneBot!",
            description=(
                "I'm a modular and versatile bot that helps organize custom modes in your server. So, what do you want to do now?\n\n"
                "Main commands:\n"
                "```text\n!setup → start mode configuration\n!language → activates the language selection screen\n```\n\n"
                "Site: Coming soon..."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="🔍 Confirming roles to avoid errors...")
    return embed

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} está online!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Como assim erro na linha 33?"))

@bot.event
async def on_guild_join(guild):
    general = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            general = channel
            break

    if general and str(guild.id) not in language_set:
        embed = create_language_embed()
        msg = await general.send(embed=embed)
        await msg.add_reaction("🇺🇸")
        await msg.add_reaction("🇧🇷")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    guild_id = str(payload.guild_id)
    if guild_id in language_set:
        return

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    if payload.emoji.name == "🇺🇸":
        guild_languages[guild_id] = "en"
        embed = create_intro_embed("en")
        await channel.send(embed=embed)
        language_set.add(guild_id)
    elif payload.emoji.name == "🇧🇷":
        guild_languages[guild_id] = "ptbr"
        embed = create_intro_embed("ptbr")
        await channel.send(embed=embed)
        language_set.add(guild_id)

@bot.command(name="idioma")
async def idioma(ctx):
    guild_id = str(ctx.guild.id)
    embed = create_language_embed()
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")
    if guild_id in language_set:
        language_set.remove(guild_id)

@bot.command(name="language")
async def language(ctx):
    await idioma(ctx)

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return

    await bot.process_commands(message)

# Manter web server e iniciar o bot
keep_alive()

token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("❌ ERRO: Token não encontrado no .env!")