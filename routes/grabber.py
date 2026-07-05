import urllib.parse
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
        
        img_urls = re.findall(r'src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg)(?:\?[^"\']*)?(?:#[^"\']*)?)["\']', html, re.I)
        media_urls = re.findall(r'(?:href|src)=["\']([^"\']+\.(?:mp4|webm|mkv|mp3|wav|m4a|pdf|zip|rar)(?:\?[^"\']*)?(?:#[^"\']*)?)["\']', html, re.I)
        
        all_urls = list(set(img_urls + media_urls))
        results = []
        
        for item in all_urls:
            if item.strip().startswith('data:'):
                continue
            resolved = urllib.parse.urljoin(url, item)
            parsed_path = urllib.parse.urlparse(resolved).path
            filename = os.path.basename(parsed_path) or 'file'
            ext = os.path.splitext(filename)[1].replace('.', '').lower() or 'unknown'
            
            category = 'other'
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                category = 'image'
            elif ext in ['mp4', 'webm', 'mkv']:
                category = 'video'
            elif ext in ['mp3', 'wav', 'm4a']:
                category = 'audio'
            elif ext in ['zip', 'rar', 'pdf']:
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
