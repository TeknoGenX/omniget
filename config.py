import os
import threading

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Global task storage for real-time progress with thread lock
download_tasks = {}
download_tasks_lock = threading.Lock()

