import discord

async def envoyer_message_et_obtenir_reponse(token: str, guild_id: int, user_id: int, message_a_envoyer: str) -> str:
    """
    Crée un canal privé avec l'utilisateur si nécessaire, envoie un message, 
    puis attend la réponse de l'utilisateur et la retourne.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    reponse_utilisateur = {"message": None}

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await channel.send(f"<@{user_id}> {message_a_envoyer}")

    @client.event
    async def on_message(message):
        if message.channel.name != channel_name:
            return
        if message.author.id != user_id:
            return
        
        reponse_utilisateur["message"] = message.content
        await client.close()

    await client.start(token)
    return reponse_utilisateur["message"]


async def envoyer_message(token: str, guild_id: int, user_id: int, message_a_envoyer: str):
    """
    Crée un canal privé avec l'utilisateur si nécessaire et envoie un message.
    Ne lit pas les réponses.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        await channel.send(f"<@{user_id}> {message_a_envoyer}")
        await client.close()

    await client.start(token)


async def envoyer_photo(token: str, guild_id: int, user_id: int, chemin_image: str):
    """
    Envoie uniquement une photo à un utilisateur dans un canal privé sur le serveur Discord.
    Crée le canal privé si nécessaire.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        guild = client.get_guild(guild_id)
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        file = discord.File(chemin_image)
        await channel.send(file=file)
        await client.close()

    await client.start(token)
