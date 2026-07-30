import urllib.parse
import socket
import ipaddress
import requests

def resolve_and_verify_ip(hostname):
    """
    Resolves hostname to IP addresses and verifies none are private/loopback.
    Returns (is_safe, primary_ip).
    """
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        if not addr_info:
            return False, None
        
        primary_ip = None
        for family, _, _, _, sockaddr in addr_info:
            ip = sockaddr[0]
            if not primary_ip:
                primary_ip = ip
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_private or 
                ip_obj.is_loopback or 
                ip_obj.is_link_local or 
                ip_obj.is_multicast):
                return False, None
        return True, primary_ip
    except Exception:
        return False, None

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
            
        is_safe, _ = resolve_and_verify_ip(hostname)
        return is_safe
    except Exception:
        return False

def safe_requests_get(url, **kwargs):
    """
    HTTP GET request wrapper that manually validates redirects to prevent SSRF & DNS Rebinding bypass.
    """
    kwargs['allow_redirects'] = False
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.get(current_url, **kwargs)
        
        # Double-check final response URL after requests connection
        if not is_safe_url(response.url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Destination URL resolved to unsafe address: {response.url}")

        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")

def safe_requests_head(url, **kwargs):
    """
    HTTP HEAD request wrapper that manually validates redirects to prevent SSRF & DNS Rebinding bypass.
    """
    kwargs['allow_redirects'] = False
    max_redirects = 5
    current_url = url
    
    for _ in range(max_redirects):
        if not is_safe_url(current_url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Blocked request to unsafe URL: {current_url}")
            
        response = requests.head(current_url, **kwargs)
        
        if not is_safe_url(response.url):
            raise requests.exceptions.RequestException(f"SSRF Protection: Destination URL resolved to unsafe address: {response.url}")

        if response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = response.headers.get('Location')
            if not redirect_url:
                break
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            return response
            
    raise requests.exceptions.TooManyRedirects("Exceeded maximum redirects allowed under SSRF protection.")

def sanitize_netscape_cookies(cookies_text):
    """
    Sanitize Netscape cookies text. Standardizes space/tab-separated columns
    into proper tab-separated columns so that yt-dlp/curl can parse them properly,
    handling lowercase true/false flags and wrapped lines seamlessly.
    """
    if not cookies_text:
        return ""
        
    output_lines = ["# Netscape HTTP Cookie File"]
    for line in cookies_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if not line.startswith("# Netscape"):
                output_lines.append(line)
            continue
            
        # Try tab split first
        parts = line.split('\t')
        if len(parts) < 6:
            parts = line.split()
            
        if len(parts) >= 6:
            domain = parts[0]
            flag = parts[1].upper() if parts[1].upper() in ['TRUE', 'FALSE'] else 'TRUE' if parts[0].startswith('.') else 'FALSE'
            path = parts[2] if len(parts) > 2 else '/'
            secure = parts[3].upper() if len(parts) > 3 and parts[3].upper() in ['TRUE', 'FALSE'] else 'FALSE'
            expiration = parts[4] if len(parts) > 4 else '0'
            name = parts[5] if len(parts) > 5 else ''
            value = "\t".join(parts[6:]) if len(parts) > 6 else ""
            
            output_lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
            
    return "\n".join(output_lines)

