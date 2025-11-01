

import os
from dotenv import load_dotenv

load_dotenv()


# Variables lues depuis l'environnement
TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
GUILD_ID = int(os.getenv("GUILD_ID", "0") or 0)
USER_ID = int(os.getenv("USER_ID", "0") or 0)
TEMP_ESPIONNAGE = int(os.getenv("TEMP_ESPIONNAGE", "15"))  # Durée en secondes du mode espionnage
# Chemin de la dernière capture (aligné avec tray.py)
PATH_PHOTO_INTRUS = os.getenv("PATH_PHOTO_INTRUS", "captures/last_capture.jpg")
TOKEN_HUGGINGFACE = os.getenv("TOKEN_HUGGINGFACE")

# Avertir si des variables critiques sont manquantes (optionnel)
def _warn_missing():
	missing = []
	if not TOKEN_DISCORD:
		missing.append("TOKEN_DISCORD")
	if not GUILD_ID:
		missing.append("GUILD_ID")
	if not USER_ID:
		missing.append("USER_ID")
	if missing:
		print(f"[ENV] Variables manquantes dans .env: {', '.join(missing)}")

_warn_missing()