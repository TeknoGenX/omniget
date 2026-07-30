import os
import re
import shutil
import subprocess
from config import DOWNLOAD_DIR, download_tasks, download_tasks_lock

def run_aria2c_download(task_id, torrent_source, speed_limit=None):
    file_id = task_id
    
    # Create isolated download directory for this specific task
    task_download_dir = os.path.join(DOWNLOAD_DIR, task_id)
    if not os.path.exists(task_download_dir):
        os.makedirs(task_download_dir)
        
    cmd = [
        'aria2c',
        '--dir=' + task_download_dir,
        '--seed-time=0',
        '--max-overall-upload-limit=2K',
        '--summary-interval=1'
    ]
    
    if speed_limit:
        try:
            limit_val = int(speed_limit)
            if limit_val > 0:
                cmd.append(f'--max-download-limit={limit_val}K')
        except ValueError:
            pass
            
    # Add '--' option delimiter to prevent argument injection
    cmd.append('--')
    cmd.append(torrent_source)
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        filename = "Torrent_Download"
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
                
            if '(' in line and ')' in line and 'SPD:' in line:
                percent_match = re.search(r'\(([\d.]+)%\)', line)
                speed_match = re.search(r'SPD:([^\s\]]+)', line)
                eta_match = re.search(r'ETA:([^\s\]]+)', line)
                
                percent = float(percent_match.group(1)) if percent_match else 0.0
                speed = speed_match.group(1) if speed_match else "N/A"
                eta = eta_match.group(1) if eta_match else "N/A"
                
                with download_tasks_lock:
                    if task_id in download_tasks:
                        download_tasks[task_id]['status'] = 'downloading'
                        download_tasks[task_id]['progress'] = percent
                        download_tasks[task_id]['speed'] = speed
                        download_tasks[task_id]['eta'] = eta
                    
        process.wait()
        
        if process.returncode != 0:
            raise Exception(f"aria2c exited with code {process.returncode}")
            
        items = [os.path.join(task_download_dir, f) for f in os.listdir(task_download_dir) if not f.endswith('.torrent')]
        if not items:
            raise FileNotFoundError("Downloaded torrent file not found")
            
        if len(items) == 1 and os.path.isfile(items[0]):
            downloaded_path = items[0]
            filename = os.path.basename(downloaded_path)
            base_n, ext_n = os.path.splitext(filename)
            new_filepath = os.path.join(DOWNLOAD_DIR, filename)
            counter = 1
            while os.path.exists(new_filepath):
                filename = f"{base_n} ({counter}){ext_n}"
                new_filepath = os.path.join(DOWNLOAD_DIR, filename)
                counter += 1
            shutil.move(downloaded_path, new_filepath)
        else:
            filename = "Torrent_Files.zip"
            zip_base = os.path.join(DOWNLOAD_DIR, "Torrent_Files")
            counter = 1
            while os.path.exists(f"{zip_base}.zip"):
                zip_base = os.path.join(DOWNLOAD_DIR, f"Torrent_Files ({counter})")
                filename = f"Torrent_Files ({counter}).zip"
                counter += 1
            shutil.make_archive(zip_base, 'zip', task_download_dir)
            new_filepath = f"{zip_base}.zip"
        
        # Cleanup temporary task directory if it still exists
        try:
            if os.path.exists(task_download_dir):
                shutil.rmtree(task_download_dir)
        except Exception:
            pass
            
        with download_tasks_lock:
            if task_id in download_tasks:
                download_tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100.0,
                    'filepath': new_filepath,
                    'filename': filename
                })
            
    except Exception as e:
        # Cleanup temporary task directory in case of failure
        try:
            if os.path.exists(task_download_dir):
                shutil.rmtree(task_download_dir)
        except Exception:
            pass
            
        with download_tasks_lock:
            if task_id in download_tasks:
                download_tasks[task_id].update({
                    'status': 'failed',
                    'error': str(e)
                })

