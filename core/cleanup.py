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
                # Clean up downloaded files and directories older than 2 hours (7200 seconds)
                for filename in os.listdir(DOWNLOAD_DIR):
                    filepath = os.path.join(DOWNLOAD_DIR, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                    except OSError:
                        continue
                        
                    if now - mtime > 7200:
                        # Extract 32-hex task_id prefix consistently
                        task_id = filename[:32]
                        
                        with download_tasks_lock:
                            t = download_tasks.get(task_id)
                            
                        if t and t.get('status') in ['downloading', 'processing', 'scheduled']:
                            continue
                            
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

