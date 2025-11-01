import platform
import subprocess

def close_computer():
    os_name = platform.system()

    if os_name == "Windows":
        # Arrêt immédiat et forcé
        subprocess.run(["shutdown", "/s", "/t", "0", "/f"])

    elif os_name in ("Linux", "FreeBSD"):
        # Essaye systemctl, sinon shutdown
        try:
            subprocess.run(["systemctl", "poweroff", "-i"])
        except Exception:
            subprocess.run(["shutdown", "-h", "now"])

    elif os_name == "Darwin":
        # macOS (pour macOS, sudo peut être nécessaire)
        subprocess.run(["sudo", "shutdown", "-h", "now"])
