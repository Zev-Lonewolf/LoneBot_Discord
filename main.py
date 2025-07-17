import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

# Flask app para manter o bot online
app = Flask('')

@app.route('/')
def home():
    return "LoneBot está online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Inicializa o bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Armazena idioma dos servidores (temporário)
server_languages = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_guild_join(guild):
    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
    if not channel:
        return

    embed = discord.Embed(
        title="🌍 Choose your language / Escolha seu idioma",
        description="React with 🇨🇷 for English or 🇧🇷 para Português.",
        color=discord.Color.blurple()
    )
    message = await channel.send(embed=embed)
    await message.add_reaction("\U0001F1FA\U0001F1F8")  # 🇺🇸
    await message.add_reaction("\U0001F1E7\U0001F1F7")  # 🇧🇷

    def check(reaction, user):
        return (
            user != bot.user and
            str(reaction.emoji) in ["\U0001F1FA\U0001F1F8", "\U0001F1E7\U0001F1F7"] and
            reaction.message.id == message.id
        )

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await channel.send("⏱️ Tempo esgotado. Você pode reiniciar a configuração com `!setup`.")
        return

    lang = "pt" if str(reaction.emoji) == "\U0001F1E7\U0001F1F7" else "en"
    server_languages[guild.id] = lang

    await send_intro(channel, lang)

async def send_intro(channel, lang):
    if lang == "pt":
        embed = discord.Embed(
            title="👋 Olá! Eu sou o LoneBot!",
            description=(
                "Sou um bot modular e versátil que ajuda a **organizar modos personalizados** no seu servidor.\n\n"
                "**Comandos principais:**\n"
                "`!setup` → iniciar configuração de modos\n"
                "`!modo_nome` → ativa o modo configurado\n\n"
                "**Site:** Em breve: [LoneBot](https://exemplo.com)\n"
                "Deseja iniciar agora a configuração dos modos?"
            ),
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="👋 Hello! I'm LoneBot!",
            description=(
                "I'm a modular and flexible bot that helps you **organize custom modes** in your server.\n\n"
                "**Main Commands:**\n"
                "`!setup` → start modes setup\n"
                "`!mode_name` → activates the configured mode\n\n"
                "**Website:** Coming soon: [LoneBot](https://example.com)\n"
                "Would you like to start configuring the modes now?"
            ),
            color=discord.Color.green()
        )

    embed.set_footer(text="Responda com !setup para começar." if lang == "pt" else "Type !setup to begin.")
    await channel.send(embed=embed)

# Rodar web server e bot
keep_alive()

token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("❌ ERRO: Token não encontrado no .env!")