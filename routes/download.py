import os
import tempfile
import uuid
import time
import urllib.parse
import threading
import requests
import yt_dlp
from flask import Blueprint, request, jsonify, send_file, Response
from config import DOWNLOAD_DIR, download_tasks
from core.ytdlp_engine import run_yt_dlp_download, clean_filename, multithreaded_download, run_generic_download
from core.torrent_engine import run_aria2c_download

from core.security import is_safe_url, safe_requests_get

download_bp = Blueprint('download', __name__)

@download_bp.route('/api/info', methods=['POST'])
def get_info():
    data = request.json or {}
    url = data.get('url')
    cookies_data = data.get('cookies')
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
        
    if not is_safe_url(url):
        return jsonify({'success': False, 'error': 'URL tidak valid atau diblokir demi alasan keamanan'}), 400

    temp_cookie_path = None
    if cookies_data:
        try:
            from core.security import sanitize_netscape_cookies
            sanitized = sanitize_netscape_cookies(cookies_data)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_f:
                temp_f.write(sanitized)
                temp_cookie_path = temp_f.name
        except Exception as e:
            return jsonify({'success': False, 'error': f'Gagal memproses cookies: {str(e)}'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'playlistend': 30,
            'socket_timeout': 15,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0'
        }
        if temp_cookie_path:
            ydl_opts['cookiefile'] = temp_cookie_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info.get('_type') == 'playlist' or 'entries' in info:
                playlist_title = info.get('title', 'Playlist')
                entries = info.get('entries', [])
                
                videos = []
                for entry in entries:
                    if entry:
                        duration_secs = entry.get('duration', 0)
                        mins = duration_secs // 60
                        secs = duration_secs % 60
                        duration_str = f"{mins}:{secs:02d}" if duration_secs else "Unknown"
                        
                        thumb = f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
                        if entry.get('thumbnails'):
                            thumb = entry.get('thumbnails')[0].get('url')
                            
                        videos.append({
                            'title': entry.get('title', 'Unknown Title'),
                            'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'duration': duration_str,
                            'uploader': entry.get('uploader', 'Unknown'),
                            'thumbnail': thumb
                        })
                return jsonify({
                    'success': True,
                    'is_playlist': True,
                    'title': playlist_title,
                    'videos': videos
                })
            
            duration_secs = info.get('duration', 0)
            mins = duration_secs // 60
            secs = duration_secs % 60
            duration_str = f"{mins}:{secs:02d}" if duration_secs else "Unknown"

            subtitles_list = []
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            all_subs = {}
            if subtitles:
                all_subs.update(subtitles)
            if automatic_captions:
                all_subs.update(automatic_captions)
                
            for lang_code, lang_info in all_subs.items():
                lang_name = lang_code
                if lang_info and len(lang_info) > 0:
                    lang_name = lang_info[0].get('name') or lang_code
                subtitles_list.append({
                    'code': lang_code,
                    'name': lang_name
                })

            return jsonify({
                'success': True,
                'is_playlist': False,
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': duration_str,
                'uploader': info.get('uploader', 'Unknown'),
                'views': f"{info.get('view_count', 0):,}",
                'url': url,
                'subtitles': subtitles_list
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if temp_cookie_path and os.path.exists(temp_cookie_path):
            try:
                os.unlink(temp_cookie_path)
            except Exception:
                pass

@download_bp.route('/api/download/start', methods=['POST'])
def start_download():
    import re
    data = request.json or {}
    url = data.get('url')
    format_type = data.get('format_type', '1080p')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    speed_limit = data.get('speed_limit')
    scheduled_time = data.get('scheduled_time')
    cookies_data = data.get('cookies')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
        
    if not url.startswith('magnet:'):
        if not is_safe_url(url):
            return jsonify({'success': False, 'error': 'URL tidak valid atau diblokir demi alasan keamanan'}), 400

    time_format_regex = re.compile(r'^(?:\d{1,2}:)?\d{1,2}:\d{1,2}$|^\d+$')
    if start_time and not time_format_regex.match(str(start_time)):
        return jsonify({'success': False, 'error': 'Format start_time tidak valid (gunakan HH:MM:SS, MM:SS, atau detik)'}), 400
        
    if end_time and not time_format_regex.match(str(end_time)):
        return jsonify({'success': False, 'error': 'Format end_time tidak valid (gunakan HH:MM:SS, MM:SS, atau detik)'}), 400
        
    task_id = uuid.uuid4().hex
    
    if url.startswith('magnet:') or '.torrent' in url:
        download_tasks[task_id] = {
            'status': 'downloading',
            'progress': 0.0,
            'speed': 'N/A',
            'eta': 'N/A',
            'filepath': None,
            'filename': None,
            'error': None,
            'created_at': time.time()
        }
        threading.Thread(target=run_aria2c_download, args=(task_id, url, speed_limit), daemon=True).start()
        return jsonify({'success': True, 'task_id': task_id})
    
    if scheduled_time:
        delay = max(0, int(scheduled_time) - int(time.time()))
        download_tasks[task_id] = {
            'status': 'scheduled',
            'progress': 0.0,
            'speed': 'N/A',
            'eta': 'N/A',
            'filepath': None,
            'filename': None,
            'error': None,
            'scheduled_time': scheduled_time,
            'created_at': time.time()
        }
        
        def run_later():
            if task_id in download_tasks:
                download_tasks[task_id]['status'] = 'downloading'
            run_yt_dlp_download(task_id, url, format_type, start_time, end_time, speed_limit, cookies_data)
            
        threading.Timer(delay, run_later).start()
        return jsonify({'success': True, 'task_id': task_id, 'scheduled': True})
        
    download_tasks[task_id] = {
        'status': 'downloading',
        'progress': 0.0,
        'speed': 'N/A',
        'eta': 'N/A',
        'filepath': None,
        'filename': None,
        'error': None,
        'created_at': time.time()
    }
    
    threading.Thread(target=run_yt_dlp_download, args=(task_id, url, format_type, start_time, end_time, speed_limit, cookies_data), daemon=True).start()
    return jsonify({'success': True, 'task_id': task_id})

@download_bp.route('/api/download/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    task = download_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
        
    lyrics_available = os.path.exists(os.path.join(DOWNLOAD_DIR, f"{task_id}_lyrics.txt"))
    
    return jsonify({
        'success': True,
        'status': task['status'],
        'progress': task['progress'],
        'speed': task['speed'],
        'eta': task['eta'],
        'filename': task['filename'],
        'error': task['error'],
        'lyrics_available': lyrics_available
    })

@download_bp.route('/api/download/file/<task_id>', methods=['GET'])
def get_download_file(task_id):
    task = download_tasks.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
        
    if task['status'] != 'completed':
        return jsonify({'success': False, 'error': f"File not ready. Status: {task['status']}"}), 400
        
    filepath = task['filepath']
    download_name = task['filename']
    speed_limit = task.get('speed_limit')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'File not found on server'}), 404
        
    if speed_limit:
        def generate():
            chunk_size = 8192
            sleep_time = chunk_size / (int(speed_limit) * 1024.0)
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    time.sleep(sleep_time)
                    
        headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{urllib.parse.quote(download_name)}",
            'Content-Type': 'application/octet-stream'
        }
        return Response(generate(), headers=headers)
        
    return send_file(
        filepath,
        as_attachment=True,
        download_name=download_name,
        conditional=True
    )

@download_bp.route('/api/download/generic', methods=['POST'])
def download_generic():
    data = request.json or {}
    url = data.get('url')
    media_type = data.get('type', 'image')
    speed_limit = data.get('speed_limit')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    if not is_safe_url(url):
        return jsonify({'success': False, 'error': 'URL tidak valid atau diblokir demi alasan keamanan'}), 400

    task_id = uuid.uuid4().hex
    
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
    
    threading.Thread(target=run_generic_download, args=(task_id, url, speed_limit), daemon=True).start()
    return jsonify({'success': True, 'task_id': task_id})

@download_bp.route('/api/download/subtitle', methods=['POST'])
def download_subtitle():
    data = request.json or {}
    url = data.get('url')
    lang = data.get('lang', 'en')
    sub_format = data.get('format', 'srt')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
        
    file_id = uuid.uuid4().hex
    try:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'subtitlesformat': sub_format,
            'outtmpl': os.path.join(DOWNLOAD_DIR, f"{file_id}_%(title)s.%(ext)s"),
            'quiet': True,
            'socket_timeout': 15,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'downloaded_subtitle')
            
            filename = None
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(file_id):
                    filename = f
                    break
                    
            if not filename:
                raise FileNotFoundError('Subtitle file not found')
                
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            safe_title = clean_filename(title)
            actual_ext = filename.split('.')[-1]
            download_name = f"{safe_title}.{lang}.{actual_ext}"
            
            def generate():
                try:
                    with open(filepath, 'rb') as f:
                        while chunk := f.read(65536):
                            yield chunk
                finally:
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
                        
            headers = {
                'Content-Disposition': f"attachment; filename*=UTF-8''{urllib.parse.quote(download_name)}",
                'Content-Type': 'text/plain'
            }
            return Response(generate(), headers=headers)
            
    except Exception as e:
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                try:
                    os.remove(os.path.join(DOWNLOAD_DIR, f))
                except OSError:
                    pass
        return jsonify({'success': False, 'error': str(e)}), 500

@download_bp.route('/api/download/thumbnail', methods=['POST'])
def download_thumbnail():
    data = request.json or {}
    thumbnail_url = data.get('thumbnail_url')
    title = data.get('title', 'thumbnail')
    
    if not thumbnail_url:
        return jsonify({'success': False, 'error': 'Thumbnail URL is required'}), 400
        
    if not is_safe_url(thumbnail_url):
        return jsonify({'success': False, 'error': 'URL tidak valid atau diblokir demi alasan keamanan'}), 400
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = safe_requests_get(thumbnail_url, headers=headers, stream=True, timeout=15)
        res.raise_for_status()
        
        safe_title = clean_filename(title)
        filename = f"{safe_title}_thumbnail.jpg"
        
        def generate():
            try:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            finally:
                res.close()
                
        download_headers = {
            'Content-Disposition': f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}",
            'Content-Type': 'image/jpeg'
        }
        return Response(generate(), headers=download_headers)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@download_bp.route('/api/download/lyrics/<task_id>', methods=['GET'])
def download_lyrics(task_id):
    fmt = request.args.get('format', 'txt')
    if fmt not in ['txt', 'lrc']:
        return jsonify({'success': False, 'error': 'Format tidak didukung'}), 400
        
    filename = f"{task_id}_lyrics.{fmt}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'Lyrics not found'}), 404
        
    return send_file(filepath, as_attachment=True, download_name=f"lyrics.{fmt}")

@download_bp.route('/api/search', methods=['POST'])
def search_videos():
    data = request.json or {}
    query = data.get('query')
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400
        
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': True,
            'socket_timeout': 15,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0'
        }
        search_query = f"ytsearch5:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            entries = info.get('entries', [])
            
            results = []
            for entry in entries:
                if entry:
                    results.append({
                        'title': entry.get('title', 'Unknown Title'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'duration': entry.get('duration'),
                        'uploader': entry.get('uploader', 'Unknown'),
                        'id': entry.get('id'),
                        'thumbnail': f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg"
                    })
            return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
