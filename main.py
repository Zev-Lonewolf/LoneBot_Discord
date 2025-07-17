import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

guild_languages = {}
language_set = set()

app = Flask('')

@app.route('/')
def home():
    return "LoneBot está no ar!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

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
                "**Sou um bot modular e versátil** que ajuda a **organizar modos personalizados** no seu servidor. Me diz, o que você quer fazer agora?\n\n"
                "**Comandos principais:**\n"
                "`!setup` → iniciar configuração de modos\n"
                "`!idioma` → ativa a seleção de idiomas\n\n"
                "**Site:** Em breve..."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="🔍 Confirmando cargos para evitar erros...")
    else:
        embed = discord.Embed(
            title="👋Hello! I'm LoneBot!",
            description=(
                "**I'm a modular and versatile bot** that helps **organize custom modes** in your server. So, what do you want to do now?\n\n"
                "**Main commands:**\n"
                "`!setup` → start mode configuration\n"
                "`!language` → activates the language selection screen\n\n"
                "**Site:** Coming soon..."
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
    await ctx.message.delete()

@bot.command(name="language")
async def language(ctx):
    await idioma(ctx)

@bot.command(name="setup")
async def setup(ctx):
    guild_id = str(ctx.guild.id)
    lang = guild_languages.get(guild_id)
    if lang not in ["ptbr", "en"]:
        lang = "en"

    await ctx.message.delete()
    await ctx.channel.purge(limit=10, check=lambda m: m.author == bot.user)

    if lang == "ptbr":
        title = "📘 Painel de Configuração"
        description = (
            "Bem-vindo ao **modo de configuração**!\n\n"
            "**Comandos principais:**\n"
            "`!Criar` → Inicia o modo de criação de modos\n"
            "`!Editar` → Inicia o modo para editar os modos já configurados\n"
            "`!Verificar` → Verificar cargos detectados e os modos já criados\n"
            "`!Funções` → Lista os comandos disponíveis (em desenvolvimento)\n"
            "`!Sobre` → Informações sobre o projeto e seu criador\n"
            "**Site:** Em breve...\n\n"
            "Use `!idioma` para trocar o idioma."
        )
    else:
        title = "📘 Setup Panel"
        description = (
            "Welcome to the **setup mode**!\n\n"
            "**Main Commands:**\n"
            "`!Create` → Starts creation mode\n"
            "`!Edit` → Starts editing existing modes\n"
            "`!Check` → Check detected roles and created modes\n"
            "`!Functions` → Lists available commands (work in progress)\n"
            "`!About` → Information about the project and its creator\n"
            "**Site:** Coming soon...\n\n"
            "Use `!language` to change language."
        )

    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    embed.set_footer(text="⏳ Apagando mensagens anteriores pra manter o canal limpo")

    await ctx.send(embed=embed)

@bot.command(name="funções", aliases=["functions"])
async def funcoes(ctx):
    guild_id = str(ctx.guild.id)
    lang = guild_languages.get(guild_id, "ptbr")

    if lang == "ptbr":
        desc = (
            "📘 **Funções disponíveis**\n\n"
            "O projeto ainda está em andamento, então essa parte não está finalizada.\n"
            "Fique ligado para novidades!"
        )
    else:
        desc = (
            "📘 **Available Functions**\n\n"
            "The project is still under development, so this part is not finalized yet.\n"
            "Stay tuned for updates!"
        )

    embed = discord.Embed(description=desc, color=discord.Color.blurple())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="sobre", aliases=["about"])
async def sobre(ctx):
    guild_id = str(ctx.guild.id)
    lang = guild_languages.get(guild_id, "ptbr")

    if lang == "ptbr":
        desc = (
            "🤖 **Sobre o LoneBot**\n\n"
            "O LoneBot nasceu da vontade de facilitar a organização de servidores com múltiplos 'modos'.\n"
            "Seu criador, **Gleidson Gonzaga, conhecido como Zev**, decidiu criar um bot modular, inteligente e adaptável a qualquer tipo de comunidade.\n\n"
            "Este projeto está em constante evolução e é um reflexo direto da paixão por bots, roleplay e automação de servidores.\n\n"
            "🔗 GitHub: https://github.com/zev-lonewolf"
        )
    else:
        desc = (
            "🤖 **About LoneBot**\n\n"
            "LoneBot was created to make it easier to organize servers with multiple 'modes'.\n"
            "Its creator, **Gleidson Gonzaga, known as Zev**, decided to create a modular, smart, and adaptable bot for any community.\n\n"
            "This project is always evolving and reflects a strong passion for bots, roleplay, and server automation.\n\n"
            "🔗 GitHub: https://github.com/zev-lonewolf"
        )

    embed = discord.Embed(description=desc, color=discord.Color.green())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return
    await bot.process_commands(message)

keep_alive()

token = os.getenv("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("❌ ERRO: Token não encontrado no .env!")