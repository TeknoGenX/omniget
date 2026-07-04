import os
import re
import uuid
import time
import threading
import tempfile
import subprocess
import requests
import urllib.parse
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
from core.security import safe_requests_get, safe_requests_head
from config import DOWNLOAD_DIR, download_tasks

def trim_media(input_path, output_path, start_time, end_time):
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-ss', start_time
    ]
    if end_time:
        cmd.extend(['-to', end_time])
        
    cmd.extend([
        '-c', 'copy',
        output_path
    ])
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        # Fallback to re-encoding if stream copy fails
        cmd_reencode = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-ss', start_time
        ]
        if end_time:
            cmd_reencode.extend(['-to', end_time])
        cmd_reencode.extend([
            '-c:v', 'libx264', '-preset', 'veryfast',
            '-c:a', 'aac',
            output_path
        ])
        res2 = subprocess.run(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res2.returncode != 0:
            raise Exception(f"FFmpeg trim failed: {res2.stderr.decode()}")

def parse_vtt_to_lyrics(vtt_path):
    if not os.path.exists(vtt_path):
        return "", ""
        
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    plain_lines = []
    lrc_lines = []
    
    time_regex = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})')
    
    seen_text = set()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('WEBVTT') or line.startswith('NOTE') or line.startswith('STYLE'):
            continue
        
        match = time_regex.match(line)
        if match:
            start_time = match.group(1)
            parts = start_time.split(':')
            if len(parts) == 3:
                mins = int(parts[0]) * 60 + int(parts[1])
                secs = parts[2][:5]
                lrc_timestamp = f"[{mins:02d}:{secs}]"
            else:
                lrc_timestamp = ""
                
            text_lines = []
            j = i + 1
            while j < len(lines) and lines[j].strip() and not time_regex.match(lines[j].strip()):
                text_lines.append(lines[j].strip())
                j += 1
                
            text = " ".join(text_lines)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.strip()
            
            if text and text not in seen_text:
                seen_text.add(text)
                plain_lines.append(text)
                if lrc_timestamp:
                    lrc_lines.append(f"{lrc_timestamp} {text}")
                    
    return "\n".join(plain_lines), "\n".join(lrc_lines)

def embed_lyrics_in_mp3(mp3_path, lyrics_text):
    try:
        audio = MP3(mp3_path, ID3=ID3)
        try:
            audio.add_tags()
        except Exception:
            pass
        audio.tags.add(USLT(encoding=3, lang='eng', desc='Lyrics', text=lyrics_text))
        audio.save()
    except Exception as e:
        print(f"Failed to embed lyrics: {e}")

def download_chunk(url, start_byte, end_byte, chunk_file_path, thread_idx, progress_dict, task_id=None, total_bytes=0, start_time=None):
    try:
        headers = {
            'Range': f'bytes={start_byte}-{end_byte}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = safe_requests_get(url, headers=headers, stream=True, timeout=15)
        r.raise_for_status()
        
        downloaded = 0
        with open(chunk_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_dict[thread_idx] = downloaded
                    
                    if task_id and total_bytes > 0 and start_time:
                        total_downloaded = sum(v for k, v in progress_dict.items() if isinstance(k, int) and v > 0)
                        percent = (total_downloaded / total_bytes) * 100
                        elapsed = time.time() - start_time
                        
                        speed_str = "N/A"
                        eta_str = "N/A"
                        if elapsed > 0:
                            speed_bps = total_downloaded / elapsed
                            speed_kbps = speed_bps / 1024
                            speed_str = f"{speed_kbps:.1f} KB/s" if speed_kbps < 1024 else f"{speed_kbps/1024:.1f} MB/s"
                            
                            remaining_bytes = total_bytes - total_downloaded
                            eta_secs = int(remaining_bytes / speed_bps) if speed_bps > 0 else 0
                            eta_str = f"{eta_secs}s" if eta_secs < 60 else f"{eta_secs//60}m {eta_secs%60}s"
                            
                        if task_id in download_tasks:
                            download_tasks[task_id]['progress'] = round(percent, 1)
                            download_tasks[task_id]['speed'] = speed_str
                            download_tasks[task_id]['eta'] = eta_str
    except Exception as e:
        print(f"Chunk download error: {e}")
        progress_dict[f'failed_{thread_idx}'] = True

def multithreaded_download(url, output_path, num_threads=4, task_id=None):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = safe_requests_head(url, headers=headers, timeout=10)
        content_length = r.headers.get('content-length')
        accept_ranges = r.headers.get('accept-ranges', '').lower()
        
        if not content_length or 'bytes' not in accept_ranges or int(content_length) < 1024 * 100:
            r2 = safe_requests_get(url, headers=headers, stream=True, timeout=30)
            r2.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r2.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return
            
        total_bytes = int(content_length)
        chunk_size = total_bytes // num_threads
        
        threads = []
        chunk_paths = []
        progress_dict = {i: 0 for i in range(num_threads)}
        start_time = time.time()
        
        for i in range(num_threads):
            start = i * chunk_size
            end = total_bytes - 1 if i == num_threads - 1 else (i + 1) * chunk_size - 1
            chunk_path = f"{output_path}.part{i}"
            chunk_paths.append(chunk_path)
            
            t = threading.Thread(
                target=download_chunk, 
                args=(url, start, end, chunk_path, i, progress_dict, task_id, total_bytes, start_time)
            )
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # Verify if any segment failed
        for i in range(num_threads):
            if progress_dict.get(f'failed_{i}'):
                raise Exception(f"Segmented chunk {i} failed to download completely.")
                
        with open(output_path, 'wb') as outfile:
            for chunk_path in chunk_paths:
                if os.path.exists(chunk_path):
                    with open(chunk_path, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(chunk_path)
    except Exception as e:
        print(f"Segmented download failed: {e}. Falling back to single-threaded download...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r2 = safe_requests_get(url, headers=headers, stream=True, timeout=30)
        r2.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in r2.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def make_progress_hook(task_id):
    def hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
            else:
                percent = 0.0
            
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            if task_id in download_tasks:
                download_tasks[task_id]['status'] = 'downloading'
                download_tasks[task_id]['progress'] = round(percent, 1)
                download_tasks[task_id]['speed'] = speed
                download_tasks[task_id]['eta'] = eta
        elif d['status'] == 'finished':
            if task_id in download_tasks:
                download_tasks[task_id]['status'] = 'processing'
                download_tasks[task_id]['progress'] = 100.0
    return hook

def run_yt_dlp_download(task_id, url, format_type, start_time=None, end_time=None, speed_limit=None, cookies_data=None):
    file_id = task_id
    filepath = None
    temp_cookie_path = None
    try:
        if cookies_data:
            try:
                from core.security import sanitize_netscape_cookies
                sanitized = sanitize_netscape_cookies(cookies_data)
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_f:
                    temp_f.write(sanitized)
                    temp_cookie_path = temp_f.name
            except Exception as e:
                if task_id in download_tasks:
                    download_tasks[task_id]['status'] = 'failed'
                    download_tasks[task_id]['error'] = f'Gagal memproses cookies: {str(e)}'
                return
        outtmpl = os.path.join(DOWNLOAD_DIR, f"{file_id}_%(title)s.%(ext)s")
        
        is_audio = False
        ext = 'mp4'
        audio_bitrate = '192'
        height = 1080
        
        if 'mp3' in format_type or 'wav' in format_type or 'm4a' in format_type:
            is_audio = True
            if 'wav' in format_type:
                ext = 'wav'
            elif 'm4a' in format_type:
                ext = 'm4a'
            else:
                ext = 'mp3'
                if '320k' in format_type:
                    audio_bitrate = '320'
                elif '128k' in format_type:
                    audio_bitrate = '128'
                elif '64k' in format_type:
                    audio_bitrate = '64'
        else:
            if 'webm' in format_type:
                ext = 'webm'
            elif 'mkv' in format_type:
                ext = 'mkv'
            else:
                ext = 'mp4'
                
            if '1080p' in format_type:
                height = 1080
            elif '720p' in format_type:
                height = 720
            elif '480p' in format_type:
                height = 480
            elif '360p' in format_type:
                height = 360
        
        if is_audio:
            if ext == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': outtmpl,
                    'writethumbnail': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['id', 'en', 'all'],
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': audio_bitrate,
                        },
                        {
                            'key': 'EmbedThumbnail',
                        },
                        {
                            'key': 'FFmpegMetadata',
                        }
                    ],
                    'quiet': True,
                    'progress_hooks': [make_progress_hook(task_id)]
                }
            else:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': outtmpl,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['id', 'en', 'all'],
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': ext,
                        },
                        {
                            'key': 'FFmpegMetadata',
                        }
                    ],
                    'quiet': True,
                    'progress_hooks': [make_progress_hook(task_id)]
                }
        else:
            ydl_opts = {
                'format': f'bestvideo[height<={height}]+bestaudio/best',
                'outtmpl': outtmpl,
                'quiet': True,
                'merge_output_format': ext,
                'progress_hooks': [make_progress_hook(task_id)]
            }
            
        if speed_limit:
            ydl_opts['ratelimit'] = int(speed_limit) * 1024
            
        # Force IPv4 and add timeout defaults to prevent connection timeouts on cloud hosts
        ydl_opts['source_address'] = '0.0.0.0'
        ydl_opts['nocheckcertificate'] = True
        ydl_opts['socket_timeout'] = 15
        if temp_cookie_path:
            ydl_opts['cookiefile'] = temp_cookie_path
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'downloaded_media')
            actual_ext = ext
            
            filename = None
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(file_id) and not f.endswith('.vtt') and not f.endswith('.jpg'):
                    filename = f
                    break
                    
            if not filename:
                raise FileNotFoundError('Downloaded file not found')
                
            filepath = os.path.join(DOWNLOAD_DIR, filename)
            actual_ext = filename.split('.')[-1]
            
            if start_time or end_time:
                trimmed_filename = f"{file_id}_trimmed.{actual_ext}"
                trimmed_filepath = os.path.join(DOWNLOAD_DIR, trimmed_filename)
                trim_media(filepath, trimmed_filepath, start_time or "00:00:00", end_time)
                os.remove(filepath)
                filepath = trimmed_filepath
                filename = trimmed_filename
 
            vtt_path = None
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(file_id) and f.endswith('.vtt'):
                    vtt_path = os.path.join(DOWNLOAD_DIR, f)
                    break
            
            if vtt_path:
                plain_lyrics, lrc_lyrics = parse_vtt_to_lyrics(vtt_path)
                if plain_lyrics:
                    with open(os.path.join(DOWNLOAD_DIR, f"{file_id}_lyrics.txt"), 'w', encoding='utf-8') as lf:
                        lf.write(plain_lyrics)
                    with open(os.path.join(DOWNLOAD_DIR, f"{file_id}_lyrics.lrc"), 'w', encoding='utf-8') as lf:
                        lf.write(lrc_lyrics)
                    
                    if actual_ext == 'mp3':
                        embed_lyrics_in_mp3(filepath, plain_lyrics)
 
            safe_title = clean_filename(title)
            download_name = f"{safe_title}.{actual_ext}"
            
            if task_id in download_tasks:
                download_tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100.0,
                    'filepath': filepath,
                    'filename': download_name
                })
    except Exception as e:
        for f in os.listdir(DOWNLOAD_DIR):
            if f.startswith(file_id):
                try:
                    os.remove(os.path.join(DOWNLOAD_DIR, f))
                except OSError:
                    pass
        if task_id in download_tasks:
            download_tasks[task_id].update({
                'status': 'failed',
                'error': str(e)
            })
    finally:
        if temp_cookie_path and os.path.exists(temp_cookie_path):
            try:
                os.unlink(temp_cookie_path)
            except Exception:
                pass

def run_generic_download(task_id, url, speed_limit=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = safe_requests_head(url, headers=headers, timeout=10)
        
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        
        if filename:
            filename = urllib.parse.unquote(filename)
            filename = clean_filename(filename)
            
        if not filename or '.' not in filename:
            content_type = res.headers.get('content-type', '')
            ext = 'jpg'
            if 'image/gif' in content_type:
                ext = 'gif'
            elif 'image/png' in content_type:
                ext = 'png'
            elif 'image/webp' in content_type:
                ext = 'webp'
            elif 'video/mp4' in content_type:
                ext = 'mp4'
            elif 'audio/mpeg' in content_type:
                ext = 'mp3'
            filename = f"grabbed_file.{ext}"
            
        filepath = os.path.join(DOWNLOAD_DIR, f"{task_id}_{filename}")
        
        # Parallel dynamic segmentation downloader with progress tracking
        multithreaded_download(url, filepath, task_id=task_id)
        
        if task_id in download_tasks:
            download_tasks[task_id].update({
                'status': 'completed',
                'progress': 100.0,
                'filepath': filepath,
                'filename': filename
            })
            
    except Exception as e:
        if task_id in download_tasks:
            download_tasks[task_id].update({
                'status': 'failed',
                'error': str(e)
            })
