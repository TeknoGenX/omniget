import urllib.parse
import html as html_lib
import re
import os
import requests
from flask import Blueprint, request, jsonify
from core.ytdlp_engine import clean_filename
from core.security import is_safe_url, safe_requests_get

grabber_bp = Blueprint('grabber', __name__)

@grabber_bp.route('/api/grab', methods=['POST'])
def grab_site_media():
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
        
    if not is_safe_url(url):
        return jsonify({'success': False, 'error': 'URL tidak valid atau diblokir demi alasan keamanan'}), 400
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = safe_requests_get(url, headers=headers, timeout=15)
        res.raise_for_status()
        html = res.text
        
        # Enhanced regex to capture src, data-src, data-original, href, srcset with or without quotes
        raw_urls = re.findall(
            r'(?:src|href|data-src|data-original|data-lazy-src)\s*=\s*["\']?([^"\'\s>]+?\.(?:jpg|jpeg|png|gif|webp|svg|mp4|webm|mkv|mp3|wav|m4a|pdf|zip|rar)(?:\?[^"\'\s>]*)?(?:#[^"\'\s>]*)?)["\']?',
            html, re.I
        )
        
        # Also parse srcset attributes
        srcset_matches = re.findall(r'srcset\s*=\s*["\']([^"\']+)["\']', html, re.I)
        for s in srcset_matches:
            parts = s.split(',')
            for part in parts:
                item_url = part.strip().split()[0]
                if item_url:
                    raw_urls.append(item_url)
        
        all_urls = list(set(raw_urls))
        results = []
        seen = set()
        
        for item in all_urls:
            item = html_lib.unescape(item.strip())
            if not item or item.startswith('data:'):
                continue
                
            resolved = urllib.parse.urljoin(url, item)
            if resolved in seen or not is_safe_url(resolved):
                continue
            seen.add(resolved)
            
            parsed_path = urllib.parse.urlparse(resolved).path
            filename = os.path.basename(parsed_path) or 'file'
            filename = clean_filename(urllib.parse.unquote(filename))
            ext = os.path.splitext(filename)[1].replace('.', '').lower() or 'unknown'
            
            category = 'other'
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                category = 'image'
            elif ext in ['mp4', 'webm', 'mkv', 'avi', 'mov']:
                category = 'video'
            elif ext in ['mp3', 'wav', 'm4a', 'flac', 'aac']:
                category = 'audio'
            elif ext in ['zip', 'rar', '7z', 'tar', 'gz', 'pdf', 'iso', 'exe', 'deb', 'apk']:
                category = 'document'
                
            results.append({
                'url': resolved,
                'name': filename,
                'ext': ext,
                'category': category
            })
            
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

