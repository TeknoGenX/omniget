import os
import time
import shutil
import threading
import logging
from config import DOWNLOAD_DIR, download_tasks, download_tasks_lock

def start_cleanup_thread():
    def cleanup_loop():
        while True:
            try:
                now = time.time()
                active_filepaths = set()
                with download_tasks_lock:
                    for t in download_tasks.values():
                        if t and t.get('status') in ['downloading', 'processing', 'scheduled']:
                            fp = t.get('filepath')
                            if fp:
                                active_filepaths.add(os.path.realpath(fp))
                                
                # Clean up downloaded files and directories older than 2 hours (7200 seconds)
                for filename in os.listdir(DOWNLOAD_DIR):
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    if os.path.realpath(filepath) in active_filepaths:
                        continue
                        
                    try:
                        mtime = os.path.getmtime(filepath)
                    except OSError:
                        continue
                        
                    if now - mtime > 7200:
                        try:
                            if os.path.isfile(filepath) or os.path.islink(filepath):
                                os.remove(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                        except OSError as oe:
                            logging.debug(f"Cleanup error removing {filepath}: {oe}")
                
                # Clean up expired task records safely with thread lock
                with download_tasks_lock:
                    for tid in list(download_tasks.keys()):
                        t = download_tasks.get(tid)
                        if t and now - t.get('created_at', 0) > 7200:
                            if t.get('status') not in ['downloading', 'processing', 'scheduled']:
                                download_tasks.pop(tid, None)
            except Exception as e:
                logging.debug(f"Cleanup daemon error: {e}")
            time.sleep(60)

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()

