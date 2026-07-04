import os
import shutil
from flask import Blueprint, render_template, jsonify, send_from_directory
from config import DOWNLOAD_DIR, download_tasks

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'static'), 'robots.txt')

@main_bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'static'), 'sitemap.xml')

@main_bp.route('/api/server/status', methods=['GET'])
def get_server_status():
    try:
        total, used, free = shutil.disk_usage(DOWNLOAD_DIR)
        file_count = len([f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))])
        
        # Count active tasks safely to prevent RuntimeError from concurrent modifications
        active_tasks = 0
        for tid in list(download_tasks.keys()):
            t = download_tasks.get(tid)
            if t and t.get('status') in ['downloading', 'processing']:
                active_tasks += 1
        
        free_gb = round(free / (1024 ** 3), 2)
        total_gb = round(total / (1024 ** 3), 2)
        
        return jsonify({
            'success': True,
            'disk_free': f"{free_gb} GB / {total_gb} GB",
            'file_count': file_count,
            'active_tasks': active_tasks
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
