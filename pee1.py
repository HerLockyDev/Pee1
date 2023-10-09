import asyncio
import random
import time
import datetime
import aiohttp
import re
import discord
from discord.ext import commands
from discord.ext import tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandPermissionType

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="?", intents=intents)
slash = SlashCommand(
    bot,
    sync_commands=True)
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Logged in as : ", bot.user.name)
    print("ID : ", bot.user.id)
    print("NB serveur : ", len(bot.guilds))
    changeStatus.start()

bot.server_settings = {}  # Dictionnaire pour stocker les paramètres des serveurs (canaux d'annonce)
bot.report_settings = {}  # Dictionnaire pour stocker les paramètres des rapports

@tasks.loop(seconds=5)
async def changeStatus():
    status = [f"?help | Surveille {len(bot.guilds)} serveurs",
          "?help | A votre service",
          "?help | Version : 2.0",
          "?help | Développeur :HerLocky",
          "?help | Support : https://discord.gg/MhPfY9qaw4",
          f"?help | Surveille {len(bot.users)} membres"]
    game = discord.Game(random.choice(status))
    await bot.change_presence(status=discord.Status.online, activity=game)

#bot added
@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(title=f"**__{guild.name}__ viens d'ajouter Pee1 !**", description="", color=65280)
    embed.add_field(name="__Nombre de membres__", value=f"{guild.member_count}")
    embed.add_field(name="__Créé le__", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="__Propriétaire__", value=f"{guild.owner}")
    embed.add_field(name="__Nombre de serveurs__", value=f"{len(bot.guilds)}")
    embed.add_field(name="__Nombre de channels__", value=f"{len(guild.channels)}")

    await bot.get_channel(1121148997160148992).send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(title=f"**Pee1 n'est plus sur __{guild.name}__ !**", description="", color=16711680)
    embed.add_field(name="__Nombre de membre__", value=f"{guild.member_count}")
    embed.add_field(name="__Créé le__", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="__Propriétaire__", value=f"{guild.owner}")
    embed.add_field(name="__Nombre de serveur__", value=f"{len(bot.guilds)}")

    await bot.get_channel(1121148997160148992).send(embed=embed)


#membre join

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    join_channel_id = None

    # Lire les paramètres depuis le fichier server_settings.txt
    with open("server_settings.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id + ":join_channel:"):
                join_channel_id = line.split(":")[2]
                break

    if join_channel_id:
        join_channel = member.guild.get_channel(int(join_channel_id))
        if join_channel:
            embed = discord.Embed(title="Nouveau membre", description=f"**{member.name}** a rejoint le serveur, nous sommes maintenant : {member.guild.member_count} membres sur le serveur.", color=discord.Color.green())
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="ID du membre", value=member.id, inline=False)
            embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
            await join_channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)
    leave_channel_id = None

    # Lire les paramètres depuis le fichier server_settings.txt
    with open("server_settings.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id + ":leave_channel:"):
                leave_channel_id = line.split(":")[2]
                break

    if leave_channel_id:
        leave_channel = member.guild.get_channel(int(leave_channel_id))
        if leave_channel:
            embed = discord.Embed(title="Membre parti", description=f"**{member.name}** a quitté le serveur.", color=discord.Color.red())
            embed.set_thumbnail(url=member.avatar_url)
            await leave_channel.send(embed=embed)



#logs
@bot.event
async def on_message_delete(message):
    if message.guild:
        guild_id = str(message.guild.id)
        with open("logs_channels.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith(guild_id):
                    _, channel_id = line.split(":")
                    channel = bot.get_channel(int(channel_id))
                    if channel:
                        embed = discord.Embed(title="Message Supprimé", color=discord.Color.red())
                        embed.add_field(name="Auteur", value=message.author.mention, inline=False)
                        embed.add_field(name="Contenu", value=message.content, inline=False)
                        embed.set_footer(text=f"Canal: #{message.channel.name}")
                        
                        await channel.send(embed=embed)
                        break

@bot.event
async def on_message_edit(before, after):
    if before.guild:
        guild_id = str(before.guild.id)
        with open("logs_channels.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith(guild_id):
                    _, channel_id = line.split(":")
                    channel = bot.get_channel(int(channel_id))
                    if channel:
                        embed = discord.Embed(title="Message Modifié", color=discord.Color.gold())
                        embed.add_field(name="Auteur", value=before.author.mention, inline=False)
                        embed.add_field(name="Contenu avant", value=before.content, inline=False)
                        embed.add_field(name="Contenu après", value=after.content, inline=False)
                        embed.set_footer(text=f"Canal: #{before.channel.name}")
                        
                        await channel.send(embed=embed)
                        break

@bot.event
async def on_member_ban(guild, user):
    guild_id = str(guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                channel = bot.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(title="Membre Banni", color=discord.Color.dark_red())
                    embed.add_field(name="Membre", value=user.name, inline=False)
                    await channel.send(embed=embed)
                    break

@bot.event
async def on_member_unban(guild, user):
    guild_id = str(guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                channel = bot.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(title="Membre Débanni", color=discord.Color.dark_green())
                    embed.add_field(name="Membre", value=user.name, inline=False)
                    await channel.send(embed=embed)
                    break

@bot.event
async def on_voice_state_update(member, before, after):
    guild_id = str(member.guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                channel = bot.get_channel(int(channel_id))
                if channel:
                    if before.channel is None and after.channel is not None:
                        embed = discord.Embed(title="Salon Vocal Rejoint", color=discord.Color.green())
                        embed.add_field(name="Membre", value=member.mention, inline=False)
                        embed.add_field(name="Salon", value=after.channel.name, inline=False)
                        
                        await channel.send(embed=embed)
                    elif before.channel is not None and after.channel is None:
                        embed = discord.Embed(title="Salon Vocal Quitté", color=discord.Color.orange())
                        embed.add_field(name="Membre", value=member.mention, inline=False)
                        embed.add_field(name="Salon", value=before.channel.name, inline=False)
                        
                        await channel.send(embed=embed)
                    break

@bot.event
async def on_guild_role_create(role):
    guild_id = str(role.guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                channel = bot.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(title="Rôle Créé", color=discord.Color.green())
                    embed.add_field(name="Nom", value=role.name, inline=False)
                    
                    await channel.send(embed=embed)
                    break

@bot.event
async def on_guild_role_delete(role):
    guild_id = str(role.guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                channel = bot.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(title="Rôle Supprimé", color=discord.Color.dark_red())
                    embed.add_field(name="Nom", value=role.name, inline=False)
                    
                    await channel.send(embed=embed)
                    break

@bot.event
async def on_guild_channel_create(channel):
    guild_id = str(channel.guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                log_channel = bot.get_channel(int(channel_id))
                if log_channel:
                    embed = discord.Embed(title="Channel Créé", color=discord.Color.green())
                    embed.add_field(name="Nom", value=channel.name, inline=False)
                    
                    await log_channel.send(embed=embed)
                    break

@bot.event
async def on_guild_channel_delete(channel):
    guild_id = str(channel.guild.id)
    with open("logs_channels.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith(guild_id):
                _, channel_id = line.split(":")
                log_channel = bot.get_channel(int(channel_id))
                if log_channel:
                    embed = discord.Embed(title="Channel Supprimé", color=discord.Color.dark_red())
                    embed.add_field(name="Nom", value=channel.name, inline=False)
                    
                    await log_channel.send(embed=embed)
                    break

#autres
@slash.slash(name="ping", description="calcul la latence du bot")
async def ping(ctx):
    start = time.perf_counter()
    msg = await ctx.send(content="calcul en cours....")
    end = time.perf_counter()
    duration = (end-start) * 1000
    embed = discord.Embed(title="Ping", description=":ping_pong: Pong!")
    embed.add_field(name="__Ping__ :" ,value=f"**{bot.ws.latency * 1000:.0f} ms**", inline=False)

    await msg.edit(content=None, embed=embed)

#configurable

@slash.slash(name="set_logs", description="Définir le channel des logs")
async def set_logs(ctx, channel_id: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Vous devez être administrateur pour utiliser cette commande.")
        return
    
    channel = bot.get_channel(channel_id)
    if not channel:
        channel = await bot.fetch_channel(channel_id)  
        if not channel:
            await ctx.send("Impossible de trouver le canal spécifié.")
            return
    
    with open("logs_channels.txt", "a") as file:
        file.write(f"{ctx.guild.id}:{channel.id}\n")
    
    await ctx.send(f"Le canal de logs a été défini sur {channel.mention}")

@slash.slash(name="set_report", description="Définir le canal de rapport")
@commands.has_permissions(manage_channels=True)
async def set_report(ctx, report_channel: discord.TextChannel):
    # Enregistrer les informations dans le fichier report_info.txt
    with open("report_info.txt", "a") as file:
        file.write(f"{ctx.guild.id}:{report_channel.id}\n")
    
    await ctx.send(f"Le canal de rapport a été défini sur {report_channel.mention} pour ce serveur.")

@slash.slash(name="set_join", description="Définir le canal d'annonce d'arrivée")
async def set_join(ctx, channel: discord.TextChannel):
    # Vérifiez si l'utilisateur a les permissions appropriées (par exemple, administrateur)
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Vous devez être administrateur pour utiliser cette commande.")
        return

    # Enregistrez l'ID du canal d'annonce d'arrivée dans les paramètres du serveur
    guild_id = str(ctx.guild.id)
    join_channel_id = str(channel.id)

    # Enregistrez les paramètres dans un fichier .txt
    with open("server_settings.txt", "a") as file:
        file.write(f"{guild_id}:join_channel:{join_channel_id}\n")

    await ctx.send(f"Le canal d'annonce d'arrivée a été défini sur {channel.mention}")


@slash.slash(name="set_leave", description="Définir le canal d'annonce de départ")
async def set_leave(ctx, channel: discord.TextChannel):
    # Vérifiez si l'utilisateur a les permissions appropriées (par exemple, administrateur)
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Vous devez être administrateur pour utiliser cette commande.")
        return

    # Enregistrez l'ID du canal d'annonce de départ dans les paramètres du serveur
    guild_id = str(ctx.guild.id)
    leave_channel_id = str(channel.id)

    # Enregistrez les paramètres dans un fichier .txt
    with open("server_settings.txt", "a") as file:
        file.write(f"{guild_id}:leave_channel:{leave_channel_id}\n")

    await ctx.send(f"Le canal d'annonce de départ a été défini sur {channel.mention}")



#utils

@slash.slash(name="tos", description="Règle du bot")
async def tos(ctx):
    dictEmbed = {
        "title": "Bienvenue sur les conditions d'utilisations de Pee1",
        "description": '''
    Pour commencer, en utilisant le bot vous accepter toutes ces conditions d'utilisation !

``1.`` Les bugs trouvés devront être rapportés immédiatement.
``2.`` Toutes tentatives d'utilisations de commandes de catégorie Owner est prohibé.
``3.`` Les ToS sont aussi à respecter.
``4.`` Le partage de toutes informations à propos du personnel ou du bot (IP, mot de passe, ...) est prohibé !
Bonne utilisation du bot :grin:
    ''',
        "color": 14398228}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))


@slash.slash(name="user_info", description="Obtient des informations sur un utilisateur")
async def userinfo(ctx, user: discord.Member = None):
    user = user or ctx.author
    playinggame = user.activity
    roles = [role for role in user.roles]
    embed = discord.Embed(colour=user.color)

    embed.set_author(
        name=f"User Info - {user}",
        icon_url=user.avatar_url
    )
    embed.set_thumbnail(url=user.avatar_url)
    embed.set_footer(text=f"Demandé(e) par {ctx.author}", icon_url=ctx.author.avatar_url)

    embed.add_field(name="🆎Nom", value=f"{user.name}", inline=False)
    embed.add_field(name="🔠NickName", value=f"{user.nick}" if user.nick else "Pas de Nickname", inline=False)
    embed.add_field(name=":1234:・Tag :", value=f"{user.discriminator}", inline=False)
    embed.add_field(name="🆔ID", value=f"{user.id}", inline=False)
    embed.add_field(name="🖼Avatar", value=f"[avatar link]({user.avatar_url})", inline=False)
    embed.add_field(name=":beginner:・Status de jeu :", value=f"{playinggame}", inline=False)
    embed.add_field(name="🔜Compte créé le", value=user.created_at.strftime("%d/%m/%Y à  %H heures, %M minutes et %S secondes"), inline=False)
    embed.add_field(name="🔜Rejoind le",
                    value=user.joined_at.strftime("%d/%m/%Y à  %H heures, %M minutes et %S secondes"), inline=False)

    embed.add_field(name="🔝Role le plus haut", value=f"{user.top_role.mention}", inline=False)
    embed.add_field(name=f"↔Roles ({len(roles)})", value=" ".join({role.mention for role in roles})[0:1000],
                    inline=False)

    embed.add_field(name="👨‍💻Bot ?", value="Oui" if user.bot else "Non", inline=False)
    await ctx.send(embed=embed)


@slash.slash(name="server_info", description="Obtient des informations sur le serveur")
async def serverinfo(ctx):
    allchannels = len(ctx.guild.channels)
    allvoice = len(ctx.guild.voice_channels)
    alltext = len(ctx.guild.text_channels)
    embed = discord.Embed(title="ServerInfo", description="Informations sur le serveur", color=0xeee657)
    embed.set_author(name=f"Serveur Info - {ctx.guild.name}")
    embed.set_thumbnail(url=ctx.guild.icon_url)
    roles = [role for role in ctx.guild.roles]
    embed.add_field(name=":ab:Nom", value=f"{ctx.guild.name}", inline=False)
    embed.add_field(name=":id:ID", value=f"{ctx.guild.id}", inline=False)
    embed.add_field(name=":earth_americas:Région", value=f"{ctx.guild.region}", inline=False)
    embed.add_field(name=":frame_photo:Icon", value=f"[icon link]({ctx.guild.icon_url})", inline=False)
    embed.add_field(name=":crown:Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name=":octagonal_sign:Niveau de vérification", value=f"{ctx.guild.verification_level}", inline=False)
    embed.add_field(name=":office:Nombre de membre total", value=f"{ctx.guild.member_count}")
    embed.add_field(name=":soon:Créé le",
                    value=ctx.guild.created_at.strftime("%d/%m/%Y à  %H heures, %M minutes et %S secondes"),
                    inline=False)
    embed.add_field(name=f":left_right_arrow:Roles ({len(roles)})",
                    value=" ".join({role.mention for role in roles})[0:1024], inline=False)
    embed.add_field(name=f":1234:Nombre d'emojis", value=len(ctx.guild.emojis), inline=False)
    embed.add_field(name=f":firecracker::sparkles:Serveur Boost",
                    value=f"Niveau : **{ctx.guild.premium_tier}** ({ctx.guild.premium_subscription_count} boost)",
                    inline=False)
    embed.add_field(name=f":musical_keyboard:・Nombre total de salon", value=f"**{allchannels}**", inline=False)
    embed.add_field(name=f":microphone2:・Salons vocaux :", value=f"**{allvoice}**", inline=False)
    embed.add_field(name=f":speech_left:・Salons textuels :", value=f"**{alltext}**", inline=False)
    embed.set_footer(text=f"Demandé(e) par {ctx.author}", icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)


@slash.slash(name="avatar", description="Obtient l'avatar d'un membre")
async def avatar(ctx, user: discord.Member = None):
    user = user or ctx.author
    embed = discord.Embed(title="Avatar",
                          description=f"Voici l'avatar de {user.mention} et voici sont lien [avatar link]({user.avatar_url})",
                          color=0xeee657)
    embed.set_image(url=user.avatar_url)

    await ctx.send(embed=embed)

@slash.slash(name="role_info", description="Obtient des informations sur un role")
async def roleinfo(ctx, role: discord.Role):
    embed = discord.Embed(title="Role Info", description=f"Role Info - {role.name}", color=0xeee657)
    embed.add_field(name="🆎Nom", value=f"{role.name}", inline=False)
    embed.add_field(name="🆔ID", value=f"{role.id}", inline=False)
    embed.add_field(name="↕Position", value=str(role.position), inline=False)
    embed.add_field(name="🔧Modifiable", value=f"Oui" if role.managed else "Non", inline=False)
    embed.add_field(name="👑Permission", value=f"{role.permissions}", inline=False)
    embed.add_field(name="🔜Créer le", value=role.created_at.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="🔘Couleur", value=f"{role.color}", inline=False)
    embed.add_field(name="‼Mention", value=f"{role.mention}", inline=False)
    embed.add_field(name="🔊Mentionable", value="Oui" if role.mentionable else "Non", inline=False)
    embed.add_field(name="↔Afficher séparément", value="Oui" if role.hoist else "Non", inline=False)
    embed.add_field(name="👨‍💼Membres", value=str(len(role.members)))

    await ctx.send(embed=embed)




@slash.slash(name="report", description="Signaler un problème")
async def report(ctx, *, message: str):
    # Charger les informations du fichier report_info.txt
    with open("report_info.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            guild_id, report_channel_id = line.strip().split(":")
            if guild_id == str(ctx.guild.id):
                report_channel = ctx.guild.get_channel(int(report_channel_id))
                if report_channel:
                    embed = discord.Embed(title="Nouveau rapport", description=message, color=discord.Color.orange())
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                    await report_channel.send(embed=embed)
                    await ctx.send("Votre rapport a été envoyé avec succès.")
                    return
                else:
                    await ctx.send("Le canal de rapport n'a pas été configuré correctement.")
                    return
        await ctx.send("Le canal de rapport n'a pas été configuré pour ce serveur.")




@slash.slash(name="botinfo", description="donne les information sur le bot")
async def botinfo(ctx):
    embed = discord.Embed(title="Pee1", description=f'''
            Pee1 est un bot 100% français de types multifonctions avec ses 41 commandes :
        -Administration- : 2 commandes
        -Modules- : 5 commandes
        -Modération- : 6 commandes
        -Utils- : 10 commandes
        -Fun- : 18 commandes
        Il peut vous etre utile pour tous grace a ses modules préconfigurer vous n'avez rien a faire juste a les activer :wink:!
        **🔰Statistiques** :
            ► __Nombre de serveurs__ : **{len(bot.guilds)}**
            ► __Nombre de membres__ : **{len(bot.users)}**
            ► __Ping Moyen__ : **{bot.ws.latency * 1000:.0f} ms**
        **⁉Informations**
            ► __Version__ : **2.0**
            ► __Language de programation__ : [Python](https://www.python.org/)
            ► __Librairy__ : [discord.py](https://discordpy.readthedocs.io/)
            ► __Développeur__ : **HerLocky**
        **🔁Liens**
            ► __GitHub__ : [click](https://github.com/Her-Locky/Proton)
            ► __Support__ : [click](https://discord.gg/MhPfY9qaw4)
            ► __Invite le bot__ : [click](https://discord.com/oauth2/authorize?client_id=1100474364262101032&scope=bot&permissions=8)
            ''', color=0xeee657)
    await ctx.send(embed=embed)


#help

@slash.slash(name="help", description="Liste les commandes du bot")
async def help(ctx):
        embed = discord.Embed(title="📜HELP", description='''Les différentes catégories de commandes de Pee1 sont : (total de *41 commandes**)
            ► Administration :computer:
            ``/help_admin`` (**2 commandes**)
            ► Modérations :rotating_light: 
            ``/help_mod`` (**6 commandes**)
            ► Modérations :rotating_light: 
            ``/help_modules`` (**5 commandes**)
            ► Utils 🔱
            ``/help_utils`` (**10 commandes**)
            ► Fun :tada:
            ``/help_fun`` (**18 commandes**)
            ''',
            color=255)
        await ctx.send(embed=embed)




@slash.slash(name="help_admin", description="Liste les commandes admin du bot")
async def help_admin(ctx):
    dictEmbed = {
        "title": ":computer:Administration Help:computer:",
        "description": ''' 
    **Arguments : [obligatoire] (optionnels)**
    ``✅/clear [votre nombre]`` : supprime les messages (1000 d'un coup maximum).
    ``✅/poll [message] ``: créé un sondage.
    ''',
        "color": 16711680}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))



@slash.slash(name="help_mod", description="Liste les commandes de modération du bots")
async def help_mod(ctx):
    dictEmbed = {
        "title": ":rotating_light:Moderation Help:rotating_light:",
        "description": '''
    **MODERATION** : 
    **Arguments : [obligatoire] (optionnels)**
    ``✅/mute [@user] [raison]`` : Mute le membre mentionné.
    ``✅/tempmute [@user] [durée en minute] [raison]`` : Mute le membre mentionné pendant un temps donnée.
    ``✅/unmute [@user]`` : Unmute le membre mentionné.
    ``✅/kick [@user]`` : Kick le membre mentionné.
    ``✅/ban [@user] [raison]`` : Ban le membre mentionné.
    ``✅/unban [@user]`` : Unban le membre mentionné.
    ''',
        "color": 11403055}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))

@slash.slash(name="help_modules",  description="Liste les modules du bot")
async def help_modules(ctx):
    dictEmbed = {
        "title": ":computer:Modules Help:computer:",
        "description": ''' 
    **Arguments : [obligatoire] (optionnels)**
    ``✅/set_join [channel]`` : Configuration du système de join.
    ``✅/set_leave [channel]`` : Configuration du système de leave.
    ``✅/set_logs [id channel]`` : Configuration du système de logs.
    ``✅/set_repport [id channel]`` : Configuration du système de report.
    ``✅/set_mute [role]`` : Configuration le rôle de mute.
    ''',
        "color": 16711680}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))

@slash.slash(name="help_utils", description="Liste les commandes utilitaires du bot")
async def help_utils(ctx):
    dictEmbed = {
        "title": ":man_frowning:Utils Help:man_frowning:",
        "description": '''
    **Arguments : [obligatoire] (optionnels)**
    ``✅/userinfo (@user)`` : donne des informations sur le membre mentionné.
    ``✅/roleinfo [@role]`` : donne des informations sur le rôle mentionné.
    ``✅/avatar (@user)`` : donne l'avatar du membre mentionné.
    ``✅/serverinfo`` : donne des informations sur le serveur.
    ``✅/ping`` : Donne le ping du bot.
    ``✅/botinfo`` : donne des informations sur Pee1.
    ``✅/report [raison]`` : report un membre au staff.
    ``✅/tos`` : donne les conditions générales d'utilisation de Pee1.
    ``✅/invite`` : donne le lien d'invitation de Pee1.
    ``✅/support`` : donne le lien du discord de support de pee1.
    ''',
        "color": 14108820}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))


@slash.slash(name="help_fun", description="Liste les commandes fun du bot")
async def help_fun(ctx):
    dictEmbed = {
        "title": ":tada:Fun Help:tada:",
        "description": '''
    **Arguments : [obligatoire] (optionnel)**
    ``✅?q`` : Pose une question au bot.
    ``✅?calcul_help``: Liste des calculs que le bot peut faire.
    ``✅?emoji`` : donne un emoji au hasard.
    ``✅?joke`` : vous raconte une blague.
    ``✅?lovecalc (@user)`` : calcule ton amour avec un membre.
    ``✅?qi (@user)`` : calcul ton QI ou celui des autre.
    ``✅?reverse [text]`` : donne un texte le bot te le donnera en verlant.
    ``✅?calin [@user]`` : fait un calin.
    ``✅?kiss [@user]`` : fait un bisous.
    ``✅?clap [@user]`` : pour applaudit.
    ``✅?claque [@user]`` : donne une claque.
    ``✅?pleurer`` : quand tu pleure.
    ``✅?angry`` : quand tu est énerver .
    ``✅?shock`` : quand tu est choquer.
    ``✅?rougir`` : quand tu rougis.
    ``✅?shrug`` : quand tu hausse les épaules.
    ``✅?smile`` : quand tu souris.
    ``✅?thinking`` : quand tu pense.
    ''',
        "color": 16734208}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))


#Modération

@slash.slash(name="kick", description="Expulser un membre du serveur")
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, sujet):
    await user.kick()
    
    embed = discord.Embed(title="KICK", description=f"**{user.name}/ID:{user.id}** a été expulsé", color=discord.Color.red())
    embed.add_field(name="Auteur de l'expulsion", value=ctx.author.name)
    embed.add_field(name="Raison", value=sujet)
    await ctx.send(embed=embed)
    
    logs_channel_id = bot.server_settings.get(str(ctx.guild.id), {}).get("logs_channel")
    if logs_channel_id:
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if logs_channel:
            logs_embed = discord.Embed(title="KICK", description=f"**{user.name}/ID:{user.id}** a été expulsé", color=discord.Color.red())
            logs_embed.add_field(name="Auteur de l'expulsion", value=ctx.author.name)
            logs_embed.add_field(name="Raison", value=sujet)
            await logs_channel.send(embed=logs_embed)
    
    await user.create_dm()
    await user.dm_channel.send(f'''
    **{ctx.guild.name}**: Vous avez été 👢 expulsé
    **Raison**: {sujet}
    **Staff**: {ctx.author.mention}
    ''')

@slash.slash(name="ban", description="Bannir un membre du serveur")
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, sujet):
    await ctx.guild.ban(user)
    
    embed = discord.Embed(title="BAN", description=f"**{user.name}/ID:{user.id}** a été banni définitivement", color=discord.Color.red())
    embed.add_field(name="Auteur du bannissement", value=ctx.author.name)
    embed.add_field(name="Raison", value=sujet)
    await ctx.send(embed=embed)
    
    logs_channel_id = bot.server_settings.get(str(ctx.guild.id), {}).get("logs_channel")
    if logs_channel_id:
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if logs_channel:
            logs_embed = discord.Embed(title="BAN", description=f"**{user.name}/ID:{user.id}** a été banni définitivement", color=discord.Color.red())
            logs_embed.add_field(name="Auteur du bannissement", value=ctx.author.name)
            logs_embed.add_field(name="Raison", value=sujet)
            await logs_channel.send(embed=logs_embed)
    
    await user.create_dm()
    await user.dm_channel.send(f'''
    **{ctx.guild.name}**: Vous avez été 🔨 banni
    **Raison**: {sujet}
    **Staff**: {ctx.author.mention}
    ''')

@slash.slash(name="unban", description="Débannir un membre du serveur")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, sujet):
    await ctx.guild.unban(user)
    
    embed = discord.Embed(title="UNBAN", description=f"**{user.name}/ID:{user.id}** a été débanni", color=discord.Color.green())
    embed.add_field(name="Auteur du débannissement", value=ctx.author.name)
    embed.add_field(name="Raison", value=sujet)
    await ctx.send(embed=embed)
    
    logs_channel_id = bot.server_settings.get(str(ctx.guild.id), {}).get("logs_channel")
    if logs_channel_id:
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if logs_channel:
            logs_embed = discord.Embed(title="UNBAN", description=f"**{user.name}/ID:{user.id}** a été débanni", color=discord.Color.green())
            logs_embed.add_field(name="Auteur du débannissement", value=ctx.author.name)
            logs_embed.add_field(name="Raison", value=sujet)
            await logs_channel.send(embed=logs_embed)


@slash.slash(name="set_mute", description="Définir le rôle de mute")
@commands.has_permissions(manage_roles=True)
async def set_mute(ctx, role: discord.Role):
    server_id = str(ctx.guild.id)
    bot.server_settings.setdefault(server_id, {})
    bot.server_settings[server_id]["mute_role"] = role.id
    with open("set_mute.txt", "w") as file:
        file.write(f"{server_id}:{role.id}")
    await ctx.send(f"Le rôle de mute a été défini sur {role.name} pour ce serveur.")


@slash.slash(name="mute", description="Muter un membre du serveur")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, sujet):
    mute_role_id = bot.server_settings.get(str(ctx.guild.id), {}).get("mute_role")
    if not mute_role_id:
        await ctx.send("Le rôle de mute n'a pas été défini.")
        return
    
    mute_role = ctx.guild.get_role(mute_role_id)
    if not mute_role:
        await ctx.send("Impossible de trouver le rôle de mute.")
        return
    
    await member.add_roles(mute_role)
    
    embed = discord.Embed(title="MUTE", description=f"**{member.name}/ID:{member.id}** a été muté", color=discord.Color.orange())
    embed.add_field(name="Auteur du mute", value=ctx.author.name)
    embed.add_field(name="Raison", value=sujet)
    await ctx.send(embed=embed)
    
    logs_channel_id = bot.server_settings.get(str(ctx.guild.id), {}).get("logs_channel")
    if logs_channel_id:
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if logs_channel:
            logs_embed = discord.Embed(title="MUTE", description=f"**{member.name}/ID:{member.id}** a été muté", color=discord.Color.orange())
            logs_embed.add_field(name="Auteur du mute", value=ctx.author.name)
            logs_embed.add_field(name="Raison", value=sujet)
            await logs_channel.send(embed=logs_embed)

@slash.slash(name="unmute", description="Démuter un membre du serveur")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    mute_role_id = bot.server_settings.get(str(ctx.guild.id), {}).get("mute_role")
    if not mute_role_id:
        await ctx.send("Le rôle de mute n'a pas été défini.")
        return
    
    mute_role = ctx.guild.get_role(mute_role_id)
    if not mute_role:
        await ctx.send("Impossible de trouver le rôle de mute.")
        return
    
    await member.remove_roles(mute_role)
    
    embed = discord.Embed(title="UNMUTE", description=f"**{member.name}/ID:{member.id}** a été démuté", color=discord.Color.green())
    embed.add_field(name="Auteur du démute", value=ctx.author.name)
    await ctx.send(embed=embed)
    
    logs_channel_id = bot.server_settings.get(str(ctx.guild.id), {}).get("logs_channel")
    if logs_channel_id:
        logs_channel = ctx.guild.get_channel(logs_channel_id)
        if logs_channel:
            logs_embed = discord.Embed(title="UNMUTE", description=f"**{member.name}/ID:{member.id}** a été démuté", color=discord.Color.green())
            logs_embed.add_field(name="Auteur du démute", value=ctx.author.name)
            await logs_channel.send(embed=logs_embed)

@slash.slash(name="tempmute", description="Mute temporairement un membre")
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, temps: int, *, sujet):
    guild_id = str(ctx.guild.id)
    mute_role_id = bot.server_settings.get(guild_id, {}).get("mute_role")
    if mute_role_id:
        mute_role = ctx.guild.get_role(mute_role_id)
        if mute_role:
            await member.add_roles(mute_role)
            embed = discord.Embed(title="TEMPMUTE", description=f"``{member.name}/ID:{member.id}`` a été tempmute pour {temps} minutes", color=discord.Color.orange())
            embed.add_field(name="Auteur du tempmute", value=ctx.author.name)
            embed.add_field(name="Durée", value=f"{temps} minutes")
            embed.add_field(name="Raison", value=sujet)
            await ctx.send(embed=embed)
            
            logs_channel_id = bot.server_settings.get(guild_id, {}).get("logs_channel")
            if logs_channel_id:
                logs_channel = ctx.guild.get_channel(logs_channel_id)
                if logs_channel:
                    logs_embed = discord.Embed(title="TEMPMUTE", description=f"``{member.name}/ID:{member.id}`` a été tempmute pour {temps} minutes", color=discord.Color.orange())
                    logs_embed.add_field(name="Auteur du tempmute", value=ctx.author.name)
                    logs_embed.add_field(name="Durée", value=f"{temps} minutes")
                    logs_embed.add_field(name="Raison", value=sujet)
                    await logs_channel.send(embed=logs_embed)
            
            await member.create_dm()
            await member.dm_channel.send(f'''
            **{ctx.guild.name}**: Vous avez été tempmute pour {temps} minutes.
            **Raison**: {sujet}
            **Staff**: {ctx.author.mention}
            ''')

            await asyncio.sleep(temps * 60)
            await member.remove_roles(mute_role)
            unmuted_embed = discord.Embed(title="UNMUTE", description=f"``{member.name}/ID:{member.id}`` a été unmute après le tempmute", color=discord.Color.green())
            unmuted_embed.add_field(name="Auteur de l'unmute", value="Système de temporisation")
            unmuted_embed.add_field(name="Raison", value="Durée du mute terminée")
            await logs_channel.send(embed=unmuted_embed)
            await member.create_dm()
            await member.dm_channel.send(f'''
            **{ctx.guild.name}**: Vous avez été unmute après le tempmute.
            **Raison**: Durée du mute terminée
            ''')
        else:
            await ctx.send("Le rôle de mute n'a pas été configuré pour ce serveur.")
    else:
        await ctx.send("Le rôle de mute n'a pas été configuré pour ce serveur.")



#fun
@slash.slash(name="reverse", description="écris en inverser", guild_ids=[997984526460538950])
async def reverse(ctx, *, text: str):
    t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
    await ctx.send(f"🔁 {t_rev}")



@slash.slash(name="love_calc", description="Calcule ton amour potentiel avec quelqu'un (humour)")
async def lovecalc(ctx, *, user: discord.Member = None):
    user = user or ctx.author

    random.seed(user.id)
    r = random.randint(1, 100)
    hot = r / 1.17

    emoji = "💔, l'amour n'est pas présent ici"
    if hot > 25:
        emoji = "❤, l'amour risque d'être dificile mais l'amitier est présent"
    if hot > 50:
        emoji = "💖, une relation est possible"
    if hot > 75:
        emoji = "💞, c'est l'amour de ta vie cours le/la rejoindre"

    embed = discord.Embed(
        description=f'''
    **{user.mention}** ton niveau d'amour avec {ctx.author.mention} est de **{hot:.2f}%**
    **{emoji}**
    ''',
        color=0xeee657
    )

    await ctx.send(embed=embed)




@slash.slash(name="coinflip", description="lance une pièce")
async def coinflip(ctx):
    coinsides = ['Pile', 'Face']
    await ctx.send(f"**{ctx.author.name}** lance une pièce. Et tombe sur : **{random.choice(coinsides)}**!")


@slash.slash(name="qi", description="Calcul ton qi (humour)")
async def qi(ctx, *, user: discord.Member = None):
    user = user or ctx.author

    random.seed(user.id)
    r = random.randint(-60, 250)
    hot = r / 1.17

    emoji = ""
    if hot < 0:
        emoji = "Mais... mais... mais il est pas intelligent lui ?! En dessous de 0 ?? La loose ! Mais non je rigole, c'est le bot qui a (encore) du buguer :unamused:"
    if hot > 0:
        emoji = "Bon, t'es pas très très intéligent toi dit donc!"
    if hot > 78:
        emoji = "Bon, t'es pas débile mais... c'est la l'extra-intelligence non plus quoi !"
    if hot > 100:
        emoji = "Mais on a affaire à un bébé génie on dirait ! **WOUHOU** !"
    if hot > 250:
        emoji = "**OMG** ! Permettez moi de vous appeler *MAÎTRE* ! Ah non, pardon, c'est juste un bug, je retire ce que je viens de dire :P"

    embed = discord.Embed(
        description=f'''
    Son QI est de **{hot:.2f}**!
    {emoji}
    ''',
        color=0xeee657
    )
    embed.set_author(
        name=f"Voici le QI de {user} !",
        icon_url=user.avatar_url
    )

    await ctx.send(embed=embed)

@slash.slash(name="pleurer", description="si tu es entrain de pleurer")
async def pleurer(ctx):
    await ctx.send(f"{ctx.author} **est entrain de pleurer... 😥**")
    await ctx.send(random.choice(["https://giphy.com/gifs/ROF8OQvDmxytW",
                                  "https://giphy.com/gifs/4NuAILyDbmD16",
                                  "https://giphy.com/gifs/AI7yqKC5Ov0B2",
                                  "https://giphy.com/gifs/87HkPDUOtN0TC",
                                  "https://giphy.com/gifs/yHeHqyoRLBBSM",
                                  "https://giphy.com/gifs/RUZZqXiGgTyec",
                                  "https://giphy.com/gifs/59d1zo8SUSaUU",
                                  "https://tenor.com/vUP8.gif",
                                  "https://tenor.com/vvmF.gif",
                                  "https://tenor.com/vt2y.gif",
                                  "https://tenor.com/xSzl.gif",
                                  "https://tenor.com/7pvS.gif", ]))


@slash.slash(name="hangry", description="si tu es en colère")
async def angry(ctx):
    await ctx.send(f"{ctx.author} **est en colère 😡**")
    await ctx.send(random.choice(["https://giphy.com/gifs/k63gNYkfIxbwY",
                                  "https://giphy.com/gifs/TEJe85dPYW0Uw",
                                  "https://giphy.com/gifs/X3VrxPijowGC4",
                                  "https://giphy.com/gifs/TEqzDIP8FDbnG",
                                  "https://giphy.com/gifs/2pTl1XyGnkflu",
                                  "https://giphy.com/gifs/ejhkhcFuR0zni",
                                  "https://giphy.com/gifs/9w9Z2ZOxcbs1a",
                                  "https://giphy.com/gifs/T3Vvyi6SHJtXW",
                                  "https://giphy.com/gifs/UUjkoeNhnn0K4", ]))


@slash.slash(name="shock", description="si tu es choqué")
async def shock(ctx):
    await ctx.send(f"{ctx.author} **est choqué 😲**")
    await ctx.send(random.choice(["https://giphy.com/gifs/3o7btN8AC43aOlKL6M",
                                  "https://giphy.com/gifs/zgGrSqSi3SSqs",
                                  "https://giphy.com/gifs/13lRBLnBpXXsS4",
                                  "https://giphy.com/gifs/ckNPhjpC1C7jAOdjVX",
                                  "https://giphy.com/gifs/BDN8BqYikeV2g",
                                  "https://giphy.com/gifs/HkUey32gK29RS",
                                  "https://giphy.com/gifs/3og0IHCELv0TRg3afK",
                                  "https://giphy.com/gifs/mm1QxNmKWPupO", ]))


@slash.slash(name="rougir", description="si tu rougi(e)")
async def rougir(ctx):
    await ctx.send(f"{ctx.author} ** rougi(e) 😊**")
    await ctx.send(random.choice(["https://tenor.com/LN7I.gif",
                                  "https://tenor.com/bd9B5.gif",
                                  "https://tenor.com/7pij.gif",
                                  "https://tenor.com/TgQ9.gif",
                                  "https://tenor.com/xm9S.gif",
                                  "https://tenor.com/2TWP.gif",
                                  "https://tenor.com/6Clt.gif",
                                  "https://tenor.com/EGSz.gif",
                                  "https://tenor.com/xUjU.gif",
                                  "https://tenor.com/xIfR.gif", ]))


@slash.slash(name="shrug", description="hausse les épaules")
async def shrug(ctx):
    await ctx.send(f"{ctx.author} **hausse les épaules** :person_shrugging:")
    await ctx.send(random.choice(["https://tenor.com/baJXt.gif",
                                  "https://tenor.com/9wVw.gif",
                                  "https://tenor.com/6HAF.gif",
                                  "https://tenor.com/ZIsy.gif",
                                  "https://tenor.com/be3cF.gif",
                                  "https://tenor.com/wUnM.gif",
                                  "https://tenor.com/5rCO.gif",
                                  "https://tenor.com/bfviE.gif"
                                  "https://tenor.com/H6uP.gif", ]))


@slash.slash(name="smile", description="si tu souris")
async def smile(ctx):
    await ctx.send(f"{ctx.author} **souri** :smile:")
    await ctx.send(random.choice(["https://tenor.com/beqAZ.gif",
                                  "https://tenor.com/zowN.gif",
                                  "https://tenor.com/ya9o.gif",
                                  "https://tenor.com/2aaI.gif",
                                  "https://tenor.com/6Gc0.gif",
                                  "https://tenor.com/Zqqm.gif",
                                  "https://tenor.com/H2r4.gif",
                                  "https://tenor.com/PzBz.gif",
                                  "https://tenor.com/bfG3V.gif",
                                  "https://tenor.com/usZY.gif",
                                  "https://tenor.com/wuOu.gif",
                                  "https://tenor.com/AbDb.gif",
                                  "https://tenor.com/HlMg.gif", ]))


@slash.slash(name="think", description="Quand tu pense")
async def thinking(ctx):
    await ctx.send(f"{ctx.author} **réfléchi** :thinking:")
    await ctx.send(random.choice(["https://tenor.com/5FxL.gif",
                                  "https://tenor.com/bgSGM.gif",
                                  "https://tenor.com/bgSGM.gif",
                                  "https://tenor.com/1P4R.gif",
                                  "https://tenor.com/4CnT.gif",
                                  "https://tenor.com/Yoa9.gif",
                                  "https://tenor.com/bm5xf.gif",
                                  "https://tenor.com/bjkoo.gif",
                                  "https://tenor.com/bicea.gif",
                                  "https://tenor.com/bmPwW.gif",
                                  "https://tenor.com/XXdw.gif", ]))


# a voir
@slash.slash(name="calin", description="Pour faire un calin")
async def calin(ctx, member: discord.Member):
    await ctx.send(f"{ctx.author} **fait un câlin à** {member.mention} 🙌 ")
    await ctx.send(random.choice(["https://giphy.com/gifs/QFPoctlgZ5s0E",
                                  "https://giphy.com/gifs/Y8wCpaKI9PUBO",
                                  "https://giphy.com/gifs/JUwliZWcyDmTQZ7m9L",
                                  "https://giphy.com/gifs/3bqtLDeiDtwhq",
                                  "https://giphy.com/gifs/l2QDM9Jnim1YVILXa",
                                  "https://giphy.com/gifs/rSNAVVANV5XhK",
                                  "https://giphy.com/gifs/yziFo5qYAOgY8",
                                  "https://giphy.com/gifs/DjczAlIcyK1Co",
                                  "https://giphy.com/gifs/VXP04aclCaUfe",
                                  "https://tenor.com/FQNP.gif",
                                  "https://tenor.com/7Wko.gif",
                                  "https://tenor.com/QWw1.gif", ]))


@slash.slash(name="clap", description="Pour applaudir")
async def clap(ctx, member: discord.Member):
    await ctx.send(f"{ctx.author} **applaudi** 👏 ")
    await ctx.send(random.choice(["https://giphy.com/gifs/klQrJUcrfMsTK",
                                  "https://giphy.com/gifs/vQB6Rf1M9hsjK",
                                  "https://giphy.com/gifs/KsPC9t0ToZhqU",
                                  "https://i.gifer.com/7ddb.gif",
                                  "https://tenor.com/bbPUh.gif",
                                  "https://tenor.com/be6kV.gif",
                                  "https://tenor.com/behUB.gif",
                                  "https://tenor.com/66ti.gif",
                                  "https://tenor.com/bmbic.gif",
                                  "https://tenor.com/Tws9.gif",
                                  "https://tenor.com/uWAq.gif", ]))


@slash.slash(name="claque", description="pour frapper quelqu'un")
async def claque(ctx, member: discord.Member):
    await ctx.send(f" {ctx.author} **frappe** {member.mention} 👊 ")
    await ctx.send(random.choice(["https://tenor.com/E1MC.gif",
                                  "https://tenor.com/xhlc.gif",
                                  "https://tenor.com/bbHX6.gif",
                                  "https://tenor.com/T3nh.gif",
                                  "https://tenor.com/8ps1.gif",
                                  "https://tenor.com/T3n1.gif",
                                  "https://tenor.com/wtQ8.gif",
                                  "https://tenor.com/HyAC.gif",
                                  "https://tenor.com/bkOur.gif",
                                  "https://tenor.com/6sAc.gif",
                                  "https://tenor.com/bmv00.gif", ]))

@slash.slash(name="kiss", description="pour embrasser quelqu'un")
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"{ctx.author} **fait un bisous à** {member.mention} :kiss: ")
    await ctx.send(random.choice(["https://giphy.com/gifs/G3va31oEEnIkM",
                                  "https://giphy.com/gifs/nyGFcsP0kAobm",
                                  "https://giphy.com/gifs/bGm9FuBCGg4SY",
                                  "https://giphy.com/gifs/vUrwEOLtBUnJe",
                                  "https://giphy.com/gifs/zkppEMFvRX5FC",
                                  "https://giphy.com/gifs/bm2O3nXTcKJeU",
                                  "https://giphy.com/gifs/hnNyVPIXgLdle",
                                  "https://giphy.com/gifs/ofF5ftkB75n2",
                                  "https://tenor.com/Z93A.gif",
                                  "https://tenor.com/6fqy.gif",
                                  "https://tenor.com/xRO8.gif",
                                  "https://tenor.com/uX8n.gif", ]))
    

@slash.slash(name="add", description="Fait une addition avec le bot")
async def add(ctx, a: int, b: int):
    embed = discord.Embed(title=f"**Calculator 2000**", description="ADDITION", color=16711680)
    embed.add_field(name="Votre calcul", value=f" {a} + {b}", inline=True)
    embed.add_field(name="``Voici le résultat``", value=(a + b), inline=True)

    await ctx.send(embed=embed)

@slash.slash(name="multiplication", description="Fait une multiplication avec le bot")
async def multiply(ctx, a: int, b: int):
    embed = discord.Embed(title=f"**Calculator 2000**", description="MULTIPLICATION", color=16711680)
    embed.add_field(name="Votre calcul", value=f" {a} * {b}", inline=True)
    embed.add_field(name="``Voici le résultat``", value=(a * b), inline=True)

    await ctx.send(embed=embed)


@slash.slash(name="division", description="Fait une division avec le bot")
async def divise(ctx, a: int, b: int):
    embed = discord.Embed(title=f"**Calculator 2000**", description="DIVISION", color=16711680)
    embed.add_field(name="Votre calcul", value=f" {a} / {b}", inline=True)
    embed.add_field(name="``Voici le résultat``", value=(a / b), inline=True)

    await ctx.send(embed=embed)


@slash.slash(name="puissance", description="Calcul des puissance avec le bot")
async def puissance(ctx, a: int, b: int):
    embed = discord.Embed(title=f"**Calculator 2000**", description="DIVISION", color=16711680)
    embed.add_field(name="Votre calcul", value=f" {a} puissance {b}", inline=True)
    embed.add_field(name="``Voici le résultat``", value=(a ** b), inline=True)

    await ctx.send(embed=embed)


@slash.slash(name="sous", description="Fait une soustraction avec le bot")
async def sous(ctx, a: int, b: int):
    embed = discord.Embed(title=f"**Calculator 2000**", description="SOUSTRACTION", color=16711680)
    embed.add_field(name="Votre calcul", value=f" {a} - {b}", inline=True)
    embed.add_field(name="``Voici le résultat``", value=(a - b), inline=True)

    await ctx.send(embed=embed)


@slash.slash(name="question", description="pose une question au bot")
async def q(ctx, *, question):
    reponses = ['**Oui :-D**',
                '**Non pas du tout**',
                '**Peut être...**',
                '**Tu as raison**',
                '**Surement !!!**',
                '**Je ne sais pas**',
                '**Je ne peux pas répondre!**'
                '**Certainement**']
    await ctx.send(f'{random.choice(reponses)}')

@slash.slash(name="joke", description="Fait une blague")
async def joke(ctx):
    reponses = ["**Que dit-on de quelqu'un qui joue aux jeux vidéo quand il est triste ? ||On dit qu il se console||**",
                '**Quel est le dessert préféré des pompiers ? ||La crème brûlée||**',
                '**Vous connaissez la blague sur les magasins ? ||C est une blague qui a supermarché||**',
                "**Qu'est ce qui peut faire le tour du monde en restant dans son coin ? ||C est un timbre||**",
                "**Pourquoi les pêcheurs ne sont pas gros ? ||Parce qu'ils surveillent leur ligne !||**",
                '**Comment appelle-t-on un chien qui a des lunettes ? ||Un optichien||**',
                '**Quel est le point commun entre un déménageur et un arbitre de football ? ||Ils aiment tous les deux sortir des cartons||**',
                '**Comment appelle-t-on un chat tout terrain ||Un CatCat (4x4)||**',
                "**Donald Duck et Marie Duck se battent, qu'est-ce que cela fait ? ||Un confit de cannard||**",
                "**Que fait un chien sans patte quand on l'appelle ? ||Il ne bouge pas||**",
                ]
    await ctx.send(f'{random.choice(reponses)}')


@slash.slash(name="emoji", description="Obtient un émoji au hasard")
async def emoji(ctx):
    reponses = ['**😀**',
                '**😁**',
                '**😂**',
                '**🤣**',
                '**😃**',
                '**😄**',
                '**😅**',
                '**😆**',
                '**😉**',
                '**😊**']
    await ctx.send(f'{random.choice(reponses)}')


@slash.slash(name="calcul_help", description="List des calculs que le bot sait faire")
async def calcul_help(ctx):
    dictEmbed = {
        "title": "Calcul help",
        "description": '''
   **Arguments : [obligatoire] (optionnel)**
    ``✅📭?add [a] [b]`` : (remplacer a et b par les chiffres que vous voulez) fait une addition.
    ``✅📭?sous [a] [b]`` : (remplacer a et b par les chiffres que vous voulez) fait une soustraction.
    ``✅📭?multiply [a] [b]`` : (remplacer a et b par les chiffres que vous voulez) fait une multiplication.
    ``✅📭?divise [a] [b]`` : (remplacer a et b par les chiffres que vous voulez) fait une division.
    ``✅📭?puissance [a] [b]`` : (remplacer a et b par les chiffres que vous voulez) calcul les puissances.
    ''',
        "color": 14398228}
    await ctx.send(embed=discord.Embed.from_dict(dictEmbed))



#admin
@slash.slash(name="poll", description="Lancer un sondage")

async def poll(ctx, *, sujet):
    dictEmbed = {
        "title": "Sondage",
        "description": sujet,
        "footer": {
            "text": f"Auteur : {ctx.author.display_name}"
        }
    }
    message = await ctx.send(embed=discord.Embed.from_dict(dictEmbed))
    await message.add_reaction('👍')
    await message.add_reaction('👎')
    await message.add_reaction('🤷')

@slash.slash(name="clear", description="Supprime des messages")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    # Supprimer le message de commande
    await ctx.channel.purge(limit=1)

    # Vérifier si le nombre de messages à supprimer est valide
    if amount <= 0:
        await ctx.send("Le nombre de messages doit être supérieur à zéro.")
        return

    # Supprimer les messages dans le canal
    deleted = await ctx.channel.purge(limit=amount)

    # Envoyer un message pour confirmer la suppression
    await ctx.send(f"{len(deleted)} messages ont été supprimés.", delete_after=5)


    

@slash.slash(name="invite", description="Pour inviter le bot")
async def invite(ctx):
    embed = discord.Embed(title="Invite Pee1", description=f'''
            ► __Invite le bot__ : [click](https://discord.com/oauth2/authorize?client_id=1100474364262101032&scope=bot&permissions=8)
            ''', color=0xeee657)
    await ctx.send(embed=embed)

@slash.slash(name="Support", description="Donne lien vers le serveur de support")
async def support(ctx):
    embed = discord.Embed(title="Support", description=f'''
            ► __Support__ : [click](https://discord.gg/MhPfY9qaw4)
            ''', color=0xeee657)
    await ctx.send(embed=embed)


bot.run(METTRE VOTRE TOKEN ICI)