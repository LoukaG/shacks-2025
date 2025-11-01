# --- Imports des bibliothèques standards (intégrées à Python) ---
import json  # Pour gérer le fichier JSON
import time  # Pour l'horodatage (timestamping)
import os
import threading

# --- Imports des bibliothèques tierces (celles que vous avez installées) ---
import psutil                 # Pour les processus, le réseau, le CPU
import pyperclip              # Pour le presse-papiers
import pygetwindow as gw      # Pour le titre de la fenêtre active
import mss                    # Pour les captures d'écran (rapide)
from pynput.keyboard import Key, Listener as KeyboardListener # Pour le clavier
from pynput.mouse import Button, Listener as MouseListener    # Pour la souris
from watchdog.observers import Observer                       # Pour surveiller les fichiers
from watchdog.events import FileSystemEventHandler            # Pour gérer les événements de fichiers

last_title = None
event_log = []
stop_event = threading.Event()
running_lstnr = {
    "keyboard": None,
    "mouse": None
}

def start_tracking_activity():
    stop_event.clear()
    start_all_tracking_event()

def start_all_tracking_event():
    tasks = [
        (start_kbd_lstnr, ()),
        (start_mouse_lstnr, ()),
        (window_tracker_loop, ())
    ]
    for task_func, task_args in tasks:
        thread = threading.Thread(target=task_func, args=task_args, daemon=True)
        thread.start()

def stop_tracking_activity():
    stop_event.set()
    if running_lstnr["mouse"]:
        running_lstnr["mouse"].stop()
    save_log_to_json()


def add_to_log(data_dict):
    data_dict["timestamp"] = time.time()
    event_log.append(data_dict)

def get_active_window_title():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return active_window.title
    except Exception as e:
        pass
    return None

def start_lstnr(name, lstnr):
    running_lstnr[name] = lstnr
    lstnr.join()
    

# Keyboard
def start_kbd_lstnr():
    with KeyboardListener(on_press=log_keystroke) as lstnr:
        start_lstnr("keyboard", lstnr)

def log_keystroke(key):
    data = {
        "type": "keystroke",
        "key": str(key)
    }
    add_to_log(data)


# Mouse
def start_mouse_lstnr():
    with MouseListener(on_click=log_mouse_click) as lstnr:
        start_lstnr("mouse", lstnr)

def log_mouse_click(x, y, button, pressed):
    if pressed:
        data = {
            "type": "mouse_click",
            "x": x,
            "y": y,
            "button": str(button),
            "window_title": get_active_window_title()
        }
        add_to_log(data)


# Window
def window_tracker_loop():
    while not stop_event.is_set():
        log_active_window()
        stop_event.wait(2)

def log_active_window():
    global last_title
    title = get_active_window_title()
    if title and title is not last_title:
        last_title = title
        data = {
            "type": "window_change",
            "title": title
        }
        add_to_log(data)



# screenshots
def screenshot_loop(output_dir = "screenshots", interval = 10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    while not stop_event.is_set():
        file_name = f"{output_dir}/screenshot_{int(time.time())}"
        try:
            with mss.mss as sct:
                sct.shot(output=file_name)
                data = {
                    "type": "screenshot",
                    "file_path": file_name,
                    "window_title" : get_active_window_title()
                }
                add_to_log(data)
        except Exception as e:
            print (f"Erreur MSS: {e}")
        stop_event.wait(interval)


def save_log_to_json(file_name="intrusion_log.json"):
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(event_log, f, indent=4)
    except Exception as e:
        print(f"Log to JSON Error : {e}")





start_tracking_activity()
time.sleep(15)
stop_tracking_activity()