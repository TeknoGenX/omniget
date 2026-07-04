import os
import time
import shutil
import threading
from config import DOWNLOAD_DIR, download_tasks

def start_cleanup_thread():
    def cleanup_loop():
        while True:
            try:
                now = time.time()
                # Clean up downloaded files and directories older than 10 minutes (600 seconds)
                for filename in os.listdir(DOWNLOAD_DIR):
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    if now - os.path.getmtime(filepath) > 600:
                        try:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                        except OSError:
                            pass
                
                # Clean up tasks older than 10 minutes safely (excluding active tasks)
                for tid in list(download_tasks.keys()):
                    t = download_tasks.get(tid)
                    if t and now - t.get('created_at', 0) > 600:
                        if t.get('status') not in ['downloading', 'processing', 'scheduled']:
                            download_tasks.pop(tid, None)
            except Exception as e:
                pass
            time.sleep(60)

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
