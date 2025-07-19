import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
from discord import TextChannel

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

guild_languages = {}
language_set = set()
manual_roles = {}

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
    if not isinstance(channel, TextChannel):
        return
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

@bot.command(name="idioma", aliases=["language", "lang", "idiomas", "languages"])
async def idioma(ctx):
    guild_id = str(ctx.guild.id)
    embed = create_language_embed()
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")
    if guild_id in language_set:
        language_set.remove(guild_id)
    await ctx.message.delete()

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

@bot.command(name="verificar", aliases=["check"])
async def verificar(ctx):
    guild = ctx.guild
    guild_id = str(guild.id)
    lang = guild_languages.get(guild_id, "ptbr")
    roles = [role.name for role in guild.roles if role.name != "@everyone"]
    if not roles:
        desc = (
            "⚠️ **Nenhum cargo foi encontrado.**\nVocê pode usar `!Manual` para adicionar cargos manualmente."
            if lang == "ptbr"
            else "⚠️ **No roles found.**\nYou can use `!Manual` to add roles manually."
        )
    else:
        desc = (
            "📌 **Cargos encontrados no servidor:**\n\n"
            if lang == "ptbr"
            else "📌 **Roles found in this server:**\n\n"
        )
        desc += "\n".join([f"- {role}" for role in roles])
        desc += "\n\n⚙️ *Modos criados:* *(em breve será listado aqui...)*"
    embed = discord.Embed(description=desc, color=discord.Color.orange())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="manual")
async def manual(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    desc = (
        "✍️ Para adicionar um cargo manualmente, use o comando:\n"
        "`!manual_cargo @Cargo`\n\n"
        "Você pode repetir esse processo para adicionar mais cargos.\n"
        "Quando terminar, clique na reação ✅ na mensagem gerada pelo comando `!manual_cargo` para continuar."
        if lang == "ptbr"
        else
        "✍️ To manually add a role, use the command:\n"
        "`!manual_cargo @Role`\n\n"
        "You can repeat this process to add more roles.\n"
        "When finished, click the ✅ reaction on the message generated by the `!manual_cargo` command to continue."
    )
    embed = discord.Embed(title="📘 Modo Manual", description=desc, color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name="manual_cargo")
async def manual_cargo(ctx, role: discord.Role = None):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    guild_id = str(ctx.guild.id)
    if role is None:
        msg = (
            "❌ Você precisa mencionar um cargo válido após o comando.\n"
            "Exemplo: `!manual_cargo @Jogador`"
            if lang == "ptbr"
            else
            "❌ You need to mention a valid role after the command.\n"
            "Example: `!manual_cargo @Player`"
        )
        await ctx.send(msg)
        return
    if guild_id not in manual_roles:
        manual_roles[guild_id] = []
    if role in manual_roles[guild_id]:
        msg = (
            f"⚠️ O cargo `{role.name}` já está na lista de cargos manuais."
            if lang == "ptbr"
            else
            f"⚠️ The role `{role.name}` is already in the manual roles list."
        )
        await ctx.send(msg)
        return
    manual_roles[guild_id].append(role)
    roles_names = "\n".join(f"- {r.name}" for r in manual_roles[guild_id])
    desc = (
        f"✅ Cargo `{role.name}` adicionado manualmente!\n\n"
        f"📋 Cargos manuais atualmente adicionados:\n{roles_names}\n\n"
        "Quando terminar, clique na reação ✅ para continuar."
        if lang == "ptbr"
        else
        f"✅ Role `{role.name}` manually added!\n\n"
        f"📋 Currently added manual roles:\n{roles_names}\n\n"
        "When finished, click the ✅ reaction to continue."
    )
    embed = discord.Embed(
        title="📘 Cargos Manuais" if lang == "ptbr" else "📘 Manual Roles",
        description=desc,
        color=discord.Color.green()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")
    def check(reaction, user):
        return str(reaction.emoji) == "✅" and user == ctx.author and reaction.message.id == msg.id
    try:
        await bot.wait_for('reaction_add', timeout=300.0, check=check)
        next_msg = (
            "🔜 Continuando o processo de criação de modos!"
            if lang == "ptbr"
            else "🔜 Continuing mode creation process!"
        )
        await ctx.send(next_msg)
    except Exception:
        timeout_msg = (
            "⌛ Tempo esgotado. Se quiser continuar, repita o processo."
            if lang == "ptbr"
            else "⌛ Time expired. If you want to continue, repeat the process."
        )
        await ctx.send(timeout_msg)

@bot.command(name="criar", aliases=["create"])
async def criar(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    guild = ctx.guild
    guild_id = str(guild.id)
    roles = [role for role in guild.roles if role.name != "@everyone"]
    if guild_id not in manual_roles:
        manual_roles[guild_id] = []
    combined_roles = roles + [r for r in manual_roles[guild_id] if r not in roles]
    if not combined_roles:
        desc = (
            "⚠️ Nenhum cargo encontrado! Use o comando `!manual` para adicionar cargos manualmente."
            if lang == "ptbr"
            else "⚠️ No roles found! Use the `!manual` command to add roles manually."
        )
        embed = discord.Embed(
            title="⚠️ Nenhum cargo encontrado!" if lang == "ptbr" else "⚠️ No roles found!",
            description=desc,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    roles_names = "\n".join(f"- {role.name}" for role in combined_roles)
    desc = (
        f"✨ Você tem os seguintes cargos detectados:\n\n{roles_names}\n\n"
        "**Use `!criar_modo` para criar um novo modo.**\n"
        "Se quiser adicionar cargos manualmente, use `!manual`."
        if lang == "ptbr"
        else
        f"✨ You have the following detected roles:\n\n{roles_names}\n\n"
        "**Use `!create_mode` to create a new mode.**\n"
        "If you want to add roles manually, use `!manual`."
    )
    embed = discord.Embed(
        title="✨ Cargos detectados!" if lang == "ptbr" else "✨ Detected roles!",
        description=desc,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="criar_modo", aliases=["create_mode"])
async def criar_modo(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    desc = (
        "✨ **Modo de Criação de Modos**\n\n"
        "Aqui você poderá criar seu primeiro modo ou o próximo. (Funcionalidade em desenvolvimento)"
        if lang == "ptbr"
        else
        "✨ **Mode Creation Mode**\n\n"
        "Here you can create your first or next mode. (Feature under development)"
    )
    embed = discord.Embed(title="✨ Criar Modo" if lang == "ptbr" else "✨ Create Mode", description=desc, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name="editar", aliases=["edit"])
async def editar(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    embed = discord.Embed(
        title="📝 Modo de Edição" if lang == "ptbr" else "📝 Edit Mode",
        description=(
            "Aqui você poderá editar os modos personalizados existentes. (em breve)"
            if lang == "ptbr" else
            "Here you will be able to edit existing custom modes. (coming soon)"
        ),
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="funções", aliases=["functions"])
async def funcoes(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    desc = (
        "📘 **Funções disponíveis**\n\nO projeto ainda está em andamento, então essa parte não está finalizada.\nFique ligado para novidades!"
        if lang == "ptbr"
        else "📘 **Available Functions**\n\nThe project is still under development, so this part is not finalized yet.\nStay tuned for updates!"
    )
    embed = discord.Embed(description=desc, color=discord.Color.blurple())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command(name="sobre", aliases=["about"])
async def sobre(ctx):
    lang = guild_languages.get(str(ctx.guild.id), "ptbr")
    desc = (
        "🤖 **Sobre o LoneBot**\n\nO LoneBot nasceu da vontade de facilitar a organização de servidores com múltiplos 'modes'.\n"
        "Seu criador, **Gleidson Gonzaga, conhecido como Zev**, decidiu criar um bot modular, inteligente e adaptável a qualquer tipo de comunidade.\n\n"
        "Este projeto está em constante evolução e é um reflexo direto da paixão por bots, roleplay e automação de servidores.\n\n"
        "🔗 GitHub: https://github.com/zev-lonewolf"
        if lang == "ptbr"
        else "🤖 **About LoneBot**\n\nLoneBot was created to make it easier to organize servers with multiple 'modes'.\n"
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