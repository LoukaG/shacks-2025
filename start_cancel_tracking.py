import threading
import time
import tracking_activity as ta


c = False
def cancel():
    time.sleep(5)
    global c
    c = True
output = {}
threading.Thread(target=cancel, daemon=True).start()
tracking_thread = threading.Thread(target=ta.tracking, args=(15, output),daemon=True)
tracking_thread.start()
while tracking_thread.is_alive():
    if c:
        ta.stop_tracking()
    ta.stop_event.wait(1)
print(output["json_path"])