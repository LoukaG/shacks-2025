import discord
import asyncio

async def envoyer_message_et_obtenir_reponse(token: str, guild_id: int, user_id: int, message_a_envoyer: str) -> str:
    """
    Crée un canal privé avec l'utilisateur si nécessaire, envoie un message, 
    puis attend la réponse de l'utilisateur et la retourne.
    """
    channel_name = f"discussion-privee-{user_id}"
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Stocker la réponse de l'utilisateur
    reponse_utilisateur = {"message": None}

    @client.event
    async def on_ready():
        print(f'Connecté en tant que {client.user}!')
        guild = client.get_guild(guild_id)

        # Vérifier si le canal existe déjà
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            # Créer un canal privé accessible seulement au bot et à l'utilisateur
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                discord.Object(id=user_id): discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
            print(f"Canal privé '{channel_name}' créé !")
        else:
            print(f"Canal privé '{channel_name}' déjà existant.")

        # Envoyer le message initial
        await channel.send(f"<@{user_id}> {message_a_envoyer}")

    @client.event
    async def on_message(message):
        # Filtrer uniquement le canal et l'utilisateur cible
        if message.channel.name != channel_name:
            return
        if message.author.id != user_id:
            return

        print(f"Message reçu : {message.content}")
        reponse_utilisateur["message"] = message.content
        await message.channel.send(f"Tu as dit : {message.content}")

        # Déconnecter le bot une fois la réponse reçue
        await client.close()

    # Lancer le bot et attendre la réponse
    await client.start(token)
    return reponse_utilisateur["message"]


# Exemple d'utilisation
if __name__ == "__main__":
    # Lien serveur discrd https://discord.gg/D4P2Cs57
    TOKEN = "TOKEN"
    GUILD_ID = 1434211042468302888
    USER_ID = 772835381615001640    # Jas
    MESSAGE = "Un intrus est détecté. 1 : Fermer ordi."

    reponse = asyncio.run(envoyer_message_et_obtenir_reponse(TOKEN, GUILD_ID, USER_ID, MESSAGE))
    print(f"La réponse de l'utilisateur : {reponse}")
