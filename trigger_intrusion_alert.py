from use_discord import envoyer_message_et_obtenir_reponse, envoyer_message, envoyer_photo
from close_computer import close_computer
from const import TOKEN_DISCORD, GUILD_ID, USER_ID
from threading import Event
from tracker_temp import tracker_temp   # ALEXIS, TODO
from summarize import summarize    # Imane, TODO
import asyncio


async def trigger_intrusion_alert(action_type: str):
    """
    Gère l'alerte en cas d'intrusion détectée.
    """
    if action_type == "close_computer":
        MESSAGE = "Un intrus est détecté. Nous avons procedé à la fermeture de l'ordinateur pour votre sécurité. VOICI UNE PHOTO DE L'INTRUS : "
        await envoyer_message(TOKEN_DISCORD, GUILD_ID, USER_ID, MESSAGE)
        await envoyer_photo(TOKEN_DISCORD, GUILD_ID, USER_ID, "old\photo_1.jpg")  # Imane, TODO, TODO
        # close_computer()
        print("Ordinateur fermé.")  # Pour test uniquement, # TODO

    elif action_type == "espionnage":

        # Lancer la tâche de tracking
        stop_event = Event()
        tracking_task = asyncio.create_task(tracker_temp(120, stop_event))   # ALEXIS, TODO

        # Envoyer le message et attendre la réponse
        MESSAGE = "Un intrus est détecté. Le mode espionnage est activé. Si vous souhaitez fermer l'ordinateur, répondez '1'."
        reponse = await envoyer_message_et_obtenir_reponse(TOKEN_DISCORD, GUILD_ID, USER_ID, MESSAGE)
        
        # Si il y a une réponse, faire un action
        if reponse == "1":
            stop_event.set()  # Arrêter le tracking
            MESSAGE = "Ordinateur en cours de fermeture..."
        else:
            MESSAGE = "Commande non reconnue. L'ordinateur reste allumé en mode espionnage."

        # Envoyer le message final
        await envoyer_message(TOKEN_DISCORD, GUILD_ID, USER_ID, MESSAGE)

        # Attendre la fin du tracking ou son interruption
        log_json_path = await tracking_task

        # Analyser le log JSON
        pdf_path, summary_json_path = summarize(log_json_path)  # Imane, TODO

        # Envoyer les fichiers
        # save_intrusion_information(pdf_path, summary_json_path) # Léo, TODO

        # Quitter
        if reponse != "1":
            close_computer()

asyncio.run(trigger_intrusion_alert("close_computer"))