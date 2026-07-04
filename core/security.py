import urllib.parse
import socket
import ipaddress
import requests

def is_safe_url(url):
    """
    Validate that the URL scheme is http/https and does not resolve
    to loopback, private, link-local, or multicast IP addresses (SSRF Protection).
    """
    if not url:
        return False
        
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Resolve hostname to all associated IPs (supports IPv4 and IPv6)
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_private or 
                ip_obj.is_loopback or 
                ip_obj.is_link_local or 
                ip_obj.is_multicast):
                return False
                
        return True
    except Exception:
        return False

def safe_requests_get(url, **kwargs):
    """
    HTTP GET request wrapper that manually validates redirects to prevent SSRF bypass.
    """
    # Force disable automatic redirects
    kwargs['allow_redirects'] = False
    
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.get(current_url, **kwargs)
        
        # Check for redirect status codes (301, 302, 303, 307, 308)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            # Resolve relative redirect URLs
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")

def safe_requests_head(url, **kwargs):
    """
    HTTP HEAD request wrapper that manually validates redirects to prevent SSRF bypass.
    """
    # Force disable automatic redirects
    kwargs['allow_redirects'] = False
    
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.head(current_url, **kwargs)
        
        # Check for redirect status codes (301, 302, 303, 307, 308)
        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            # Resolve relative redirect URLs
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")

def sanitize_netscape_cookies(cookies_text):
    """
    Sanitize Netscape cookies text. Standardizes any space-separated columns
    into tab-separated columns so that yt-dlp/curl can parse them properly.
    """
    if not cookies_text:
        return ""
        
    clean_lines = []
    for line in cookies_text.splitlines():
        line = line.strip()
        if not line:
            clean_lines.append("")
            continue
        if line.startswith("#"):
            clean_lines.append(line)
            continue
            
        parts = line.split()
        if len(parts) >= 6:
            domain = parts[0]
            flag = parts[1]
            path = parts[2]
            secure = parts[3]
            expiration = parts[4]
            name = parts[5]
            value = " ".join(parts[6:]) if len(parts) > 6 else ""
            clean_lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
        else:
            clean_lines.append(line)
            
    return "\n".join(clean_lines)
