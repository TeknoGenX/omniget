import uuid
import time
import threading
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import DOWNLOAD_DIR, download_tasks, download_tasks_lock
from core.torrent_engine import run_aria2c_download

torrent_bp = Blueprint('torrent', __name__)

@torrent_bp.route('/api/torrent/upload', methods=['POST'])
def upload_torrent():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if not file.filename or not file.filename.endswith('.torrent'):
        return jsonify({'success': False, 'error': 'Invalid file format. Only .torrent files are allowed'}), 400
        
    speed_limit = request.form.get('speed_limit')
    task_id = uuid.uuid4().hex
    safe_name = secure_filename(file.filename)
    if not safe_name or not safe_name.endswith('.torrent'):
        safe_name = 'download.torrent'
    torrent_filename = f"{task_id}_{safe_name}"
    torrent_path = os.path.join(DOWNLOAD_DIR, torrent_filename)
    file.save(torrent_path)
    
    with download_tasks_lock:
        download_tasks[task_id] = {
            'status': 'downloading',
            'progress': 0.0,
            'speed': 'N/A',
            'eta': 'N/A',
            'filepath': None,
            'filename': None,
            'error': None,
            'speed_limit': speed_limit,
            'created_at': time.time()
        }
    
    threading.Thread(target=run_aria2c_download, args=(task_id, torrent_path, speed_limit), daemon=True).start()
    return jsonify({'success': True, 'task_id': task_id})

